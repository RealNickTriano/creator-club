"""Tests for the membership service layer.

``set_membership`` is the whole lifecycle in one upsert — join, no-op,
re-tier, resume — so these cases walk a membership through it against the
isolated Postgres ``db_session``.
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from backend.membership import repository, service
from backend.tier import repository as tier_repository
from backend.tier.models import Tier
from backend.tier.schemas import NewTier
from backend.user import repository as user_repository
from backend.user.models import User
from backend.user.schemas import NewUser


async def _create_user(db_session: AsyncSession) -> User:
  """A persisted user, unique per call to avoid UNIQUE clashes."""
  token = uuid.uuid4().hex
  return await user_repository.create_user(
    db_session,
    NewUser(google_sub=f"sub-{token}", google_email=f"{token}@example.com"),
  )


async def _create_tier(
  db_session: AsyncSession, owner: User, rank: int = 0
) -> Tier:
  """A persisted free tier owned by ``owner``."""
  return await tier_repository.create_tier(
    db_session,
    owner.id,
    NewTier(
      name=f"tier-{uuid.uuid4().hex[:8]}",
      rank=rank,
      price_cents=0,
      description=None,
    ),
  )


async def test_set_membership_joins_when_none_exists(
  db_session: AsyncSession,
) -> None:
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)

  membership, created = await service.set_membership(
    db_session, member.id, creator.id, tier.id
  )

  assert created is True
  assert membership.tier_id == tier.id
  assert membership.current_period_end is None
  assert membership.canceled_at is None


async def test_set_membership_same_tier_is_a_noop(
  db_session: AsyncSession,
) -> None:
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)
  first, _ = await service.set_membership(
    db_session, member.id, creator.id, tier.id
  )

  again, created = await service.set_membership(
    db_session, member.id, creator.id, tier.id
  )

  assert created is False
  assert again.id == first.id
  assert again.tier_id == tier.id


async def test_set_membership_changes_tier_on_same_row(
  db_session: AsyncSession,
) -> None:
  """Upgrade/downgrade updates the one row, per the per-creator uniqueness."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  free = await _create_tier(db_session, creator, rank=0)
  higher = await _create_tier(db_session, creator, rank=1)
  first, _ = await service.set_membership(
    db_session, member.id, creator.id, free.id
  )

  changed, created = await service.set_membership(
    db_session, member.id, creator.id, higher.id
  )

  assert created is False
  assert changed.id == first.id
  assert changed.tier_id == higher.id


async def test_list_memberships_by_member_returns_held_memberships(
  db_session: AsyncSession,
) -> None:
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)
  membership, _ = await service.set_membership(
    db_session, member.id, creator.id, tier.id
  )

  rows = await service.list_memberships_by_member(db_session, member.id)

  assert [(m.id, t.id, c.id) for m, t, c in rows] == [
    (membership.id, tier.id, creator.id)
  ]


async def test_set_membership_resumes_a_canceled_membership(
  db_session: AsyncSession,
) -> None:
  """Rejoining clears the cancel stamps but keeps the original started_at."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)
  membership, _ = await service.set_membership(
    db_session, member.id, creator.id, tier.id
  )
  originally_started = membership.started_at

  # Cancel: stamp the request and close the open-ended period immediately.
  now = datetime.now(UTC)
  membership.canceled_at = now
  membership.current_period_end = now - timedelta(seconds=1)
  await repository.update_membership(db_session, membership)

  resumed, created = await service.set_membership(
    db_session, member.id, creator.id, tier.id
  )

  assert created is False
  assert resumed.id == membership.id
  assert resumed.canceled_at is None
  assert resumed.current_period_end is None
  assert resumed.started_at == originally_started
