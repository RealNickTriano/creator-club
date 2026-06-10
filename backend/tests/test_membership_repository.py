"""Tests for the membership repository.

These run against a real (isolated) async Postgres database — see the
``db_session`` fixture in ``conftest.py``. Memberships join two users through
a tier, so each test builds that cast first.
"""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.membership import repository
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
  db_session: AsyncSession, owner: User, rank: int = 0, price_cents: int = 0
) -> Tier:
  """A persisted tier owned by ``owner`` (free by default)."""
  return await tier_repository.create_tier(
    db_session,
    owner.id,
    NewTier(
      name=f"tier-{uuid.uuid4().hex[:8]}",
      rank=rank,
      price_cents=price_cents,
      description=None,
    ),
  )


async def test_create_membership_persists_and_returns(
  db_session: AsyncSession,
) -> None:
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)

  membership = await repository.create_membership(
    db_session, member.id, creator.id, tier.id
  )

  assert isinstance(membership.id, uuid.UUID)
  assert membership.member_id == member.id
  assert membership.creator_id == creator.id
  assert membership.tier_id == tier.id
  # Server default is populated after the post-insert refresh.
  assert membership.started_at is not None
  # Open-ended and uncanceled at creation.
  assert membership.current_period_end is None
  assert membership.canceled_at is None


async def test_get_membership_by_member_and_creator_found(
  db_session: AsyncSession,
) -> None:
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)
  created = await repository.create_membership(
    db_session, member.id, creator.id, tier.id
  )

  found = await repository.get_membership_by_member_and_creator(
    db_session, member.id, creator.id
  )
  assert found is not None
  assert found.id == created.id


async def test_get_membership_by_member_and_creator_missing_returns_none(
  db_session: AsyncSession,
) -> None:
  member = await _create_user(db_session)
  creator = await _create_user(db_session)

  found = await repository.get_membership_by_member_and_creator(
    db_session, member.id, creator.id
  )
  assert found is None


async def test_list_memberships_by_member_returns_pairs(
  db_session: AsyncSession,
) -> None:
  """Each membership comes back paired with its held tier; others' rows don't."""
  member = await _create_user(db_session)
  creator_a = await _create_user(db_session)
  creator_b = await _create_user(db_session)
  tier_a = await _create_tier(db_session, creator_a)
  tier_b = await _create_tier(db_session, creator_b)
  first = await repository.create_membership(
    db_session, member.id, creator_a.id, tier_a.id
  )
  second = await repository.create_membership(
    db_session, member.id, creator_b.id, tier_b.id
  )
  # Another member's membership must not leak into the listing.
  other = await _create_user(db_session)
  await repository.create_membership(db_session, other.id, creator_a.id, tier_a.id)

  pairs = await repository.list_memberships_by_member(db_session, member.id)

  assert {m.id for m, _ in pairs} == {first.id, second.id}
  assert {(m.id, t.id) for m, t in pairs} == {
    (first.id, tier_a.id),
    (second.id, tier_b.id),
  }


async def test_list_memberships_by_member_empty(db_session: AsyncSession) -> None:
  member = await _create_user(db_session)

  assert await repository.list_memberships_by_member(db_session, member.id) == []


async def test_update_membership_persists_changes(db_session: AsyncSession) -> None:
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)
  membership = await repository.create_membership(
    db_session, member.id, creator.id, tier.id
  )

  when = datetime(2026, 6, 9, 12, 0, tzinfo=UTC)
  membership.canceled_at = when
  membership.current_period_end = when
  updated = await repository.update_membership(db_session, membership)

  assert updated.canceled_at == when
  assert updated.current_period_end == when

  # The change is durable, not just reflected on the returned object.
  refreshed = await repository.get_membership_by_member_and_creator(
    db_session, member.id, creator.id
  )
  assert refreshed is not None
  assert refreshed.canceled_at == when


async def test_duplicate_membership_per_creator_rejected(
  db_session: AsyncSession,
) -> None:
  """UNIQUE (member_id, creator_id): one membership per pair."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator, rank=0)
  other_tier = await _create_tier(db_session, creator, rank=1)
  await repository.create_membership(db_session, member.id, creator.id, tier.id)

  with pytest.raises(IntegrityError):
    await repository.create_membership(
      db_session, member.id, creator.id, other_tier.id
    )


async def test_self_membership_rejected(db_session: AsyncSession) -> None:
  """CHECK (member_id <> creator_id): no one is a member of themself."""
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)

  with pytest.raises(IntegrityError):
    await repository.create_membership(
      db_session, creator.id, creator.id, tier.id
    )
