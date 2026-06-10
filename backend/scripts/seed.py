"""Seed the local dev database with test data.

Five creators with handles and bios, each with a small tier ladder, plus
memberships: the seed users support each other, and every real (non-seed)
account is subscribed to a few creators so the home grid has content when you
sign in.

Idempotent: existing users (by ``google_sub``) are skipped, a creator who
already has tiers keeps their ladder untouched, and memberships go through the
service's upsert. Rerunning is safe.

Memberships are seeded directly through the service layer, so paid tiers skip
the simulated billing delay in :mod:`backend.billing`.

Run from ``backend/`` with the database up (``docker compose up -d``):

    uv run python scripts/seed.py
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import SessionLocal
from backend.membership import service as membership_service
from backend.tier import service as tier_service
from backend.tier.schemas import NewTier
from backend.user import service as user_service
from backend.user.models import User
from backend.user.schemas import NewUser, UpdateUser

# (creation data, profile) per user — the seed- prefix on google_sub marks
# these rows as test data and keys the rerun check.
SEED_USERS: list[tuple[NewUser, UpdateUser]] = [
  (
    NewUser(
      google_sub="seed-mayamakes",
      google_email="maya@example.com",
      google_name="Maya Lin",
    ),
    UpdateUser(
      handle="mayamakes",
      bio="Ceramics, slow process videos, and the occasional kiln disaster.",
    ),
  ),
  (
    NewUser(
      google_sub="seed-longgame",
      google_email="longgame@example.com",
      google_name="The Long Game",
    ),
    UpdateUser(
      handle="longgame",
      bio="A weekly essay on strategy, careers, and compounding decisions.",
    ),
  ),
  (
    NewUser(
      google_sub="seed-devdiaries",
      google_email="devdiaries@example.com",
      google_name="Dev Diaries",
    ),
    UpdateUser(
      handle="devdiaries",
      bio="Building in public: devlogs, postmortems, and code walkthroughs.",
    ),
  ),
  (
    NewUser(
      google_sub="seed-quietstudio",
      google_email="quietstudio@example.com",
      google_name="Quiet Studio",
    ),
    UpdateUser(
      handle="quietstudio",
      bio="Ambient music and field recordings, released a few tracks at a time.",
    ),
  ),
  (
    NewUser(
      google_sub="seed-pixelpoet",
      google_email="iris@example.com",
      google_name="Iris Vale",
    ),
    UpdateUser(
      handle="pixelpoet",
      bio="Pixel art studies and tiny interactive poems for the web.",
    ),
  ),
]

# Each creator's ladder, bottom rung first (rank = list index).
SEED_TIERS: dict[str, list[NewTier]] = {
  "mayamakes": [
    NewTier(name="Free", rank=0, price_cents=0, description="Public posts and studio updates."),
    NewTier(name="Supporter", rank=1, price_cents=500, description="Process videos and glaze notes."),
    NewTier(name="Insider", rank=2, price_cents=1200, description="Monthly live throwing sessions."),
  ],
  "longgame": [
    NewTier(name="Free", rank=0, price_cents=0, description="The occasional public essay."),
    NewTier(name="Member", rank=1, price_cents=800, description="Every weekly essay, plus the archive."),
    NewTier(name="All-Access", rank=2, price_cents=2000, description="Essays plus the monthly Q&A thread."),
  ],
  "devdiaries": [
    NewTier(name="Free", rank=0, price_cents=0, description="Devlog highlights."),
    NewTier(name="Supporter", rank=1, price_cents=400, description="Full postmortems and code walkthroughs."),
  ],
  "quietstudio": [
    NewTier(name="Free", rank=0, price_cents=0, description="A track each month."),
    NewTier(name="Supporter", rank=1, price_cents=300, description="Full releases and field-recording packs."),
    NewTier(name="Patron", rank=2, price_cents=1000, description="Stems, early mixes, and requests."),
  ],
  "pixelpoet": [
    NewTier(name="Free", rank=0, price_cents=0, description="Weekly pixel studies."),
    NewTier(name="Collector", rank=1, price_cents=600, description="Source files and interactive builds."),
  ],
}

# (member handle, creator handle, tier rank) — the seed users support each
# other so creator pages and member lists aren't empty.
SEED_MEMBERSHIPS: list[tuple[str, str, int]] = [
  ("pixelpoet", "mayamakes", 0),
  ("mayamakes", "quietstudio", 1),
  ("devdiaries", "longgame", 1),
  ("quietstudio", "pixelpoet", 1),
  ("longgame", "devdiaries", 0),
]

# (creator handle, tier rank) given to every real (non-seed) account, so the
# signed-in dev sees a populated home grid.
DEV_MEMBERSHIPS: list[tuple[str, int]] = [
  ("mayamakes", 2),
  ("longgame", 2),
  ("devdiaries", 0),
  ("quietstudio", 1),
]


async def _seed_users(session: AsyncSession) -> dict[str, User]:
  """Create the seed users (skipping existing) and return them by handle."""
  users: dict[str, User] = {}
  for new_user, profile in SEED_USERS:
    assert profile.handle is not None
    user = await user_service.get_user_by_google_sub(session, new_user.google_sub)
    if user is None:
      user = await user_service.create_user(session, new_user)
      user = await user_service.update_user(session, user, profile)
      print(f"created @{profile.handle} ({new_user.google_name})")
    else:
      print(f"skipped @{profile.handle} (already seeded)")
    users[profile.handle] = user
  return users


async def _seed_tiers(session: AsyncSession, users: dict[str, User]) -> None:
  """Give each creator their ladder, leaving any existing ladder untouched."""
  for handle, ladder in SEED_TIERS.items():
    creator = users[handle]
    existing = await tier_service.list_tiers_by_user(session, creator.id)
    if existing:
      print(f"skipped tiers for @{handle} (already has {len(existing)})")
      continue
    for new_tier in ladder:
      await tier_service.create_tier(session, creator.id, new_tier)
    print(f"created {len(ladder)} tiers for @{handle}")


async def _join(
  session: AsyncSession, member: User, creator: User, rank: int
) -> None:
  """Upsert ``member``'s membership onto the creator's tier at ``rank``."""
  tiers = await tier_service.list_tiers_by_user(session, creator.id)
  tier = next(t for t in tiers if t.rank == rank)
  _, created = await membership_service.set_membership(
    session, member.id, creator.id, tier.id
  )
  verb = "joined" if created else "kept"
  member_name = f"@{member.handle}" if member.handle else member.google_email
  print(f"{member_name} {verb} @{creator.handle} ({tier.name})")


async def _seed_memberships(
  session: AsyncSession, users: dict[str, User]
) -> None:
  """Cross-subscribe the seed users, then subscribe every real account."""
  for member_handle, creator_handle, rank in SEED_MEMBERSHIPS:
    await _join(session, users[member_handle], users[creator_handle], rank)

  dev_users = (
    await session.scalars(select(User).where(~User.google_sub.like("seed-%")))
  ).all()
  for dev_user in dev_users:
    for creator_handle, rank in DEV_MEMBERSHIPS:
      await _join(session, dev_user, users[creator_handle], rank)


async def main() -> None:
  async with SessionLocal() as session:
    users = await _seed_users(session)
    await _seed_tiers(session, users)
    await _seed_memberships(session, users)


if __name__ == "__main__":
  asyncio.run(main())
