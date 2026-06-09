"""Tests for the tier repository.

These run against a real (isolated) async Postgres database — see the
``db_session`` fixture in ``conftest.py`` — because the repository is, by
design, nothing but database access; mocking the session would test nothing.
Tiers belong to a user, so each test creates its owner first.
"""

import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.tier import repository
from backend.tier.schemas import NewTier
from backend.user import repository as user_repository
from backend.user.models import User
from backend.user.schemas import NewUser


async def _create_user(db_session: AsyncSession) -> User:
  """A persisted user to own tiers, unique per call to avoid UNIQUE clashes."""
  token = uuid.uuid4().hex
  return await user_repository.create_user(
    db_session,
    NewUser(google_sub=f"sub-{token}", google_email=f"{token}@example.com"),
  )


def _new_tier(**overrides: object) -> NewTier:
  """A valid ``NewTier``; override ``name``/``rank`` to control uniqueness."""
  data: dict[str, object] = {
    "name": f"tier-{uuid.uuid4().hex[:8]}",
    "rank": 1,
    "price_cents": 500,
    "description": "Early access",
  }
  data.update(overrides)
  return NewTier(**data)  # type: ignore[arg-type]


async def test_create_tier_persists_and_returns(db_session: AsyncSession) -> None:
  user = await _create_user(db_session)
  new_tier = _new_tier()

  tier = await repository.create_tier(db_session, user.id, new_tier)

  assert isinstance(tier.id, uuid.UUID)
  assert tier.user_id == user.id
  assert tier.name == new_tier.name
  assert tier.rank == new_tier.rank
  assert tier.price_cents == new_tier.price_cents
  assert tier.description == new_tier.description
  # Server defaults are populated after the post-insert refresh.
  assert tier.created_at is not None
  assert tier.updated_at is not None


async def test_create_tier_allows_null_description(
  db_session: AsyncSession,
) -> None:
  user = await _create_user(db_session)
  tier = await repository.create_tier(db_session, user.id, _new_tier(description=None))
  assert tier.description is None


async def test_get_tier_by_id_found(db_session: AsyncSession) -> None:
  user = await _create_user(db_session)
  created = await repository.create_tier(db_session, user.id, _new_tier())

  found = await repository.get_tier_by_id(db_session, created.id)
  assert found is not None
  assert found.id == created.id


async def test_get_tier_by_id_missing_returns_none(db_session: AsyncSession) -> None:
  assert await repository.get_tier_by_id(db_session, uuid.uuid4()) is None


async def test_list_tiers_by_user_orders_by_rank(db_session: AsyncSession) -> None:
  """Tiers come back rank-ascending regardless of insertion order."""
  user = await _create_user(db_session)
  for rank in (2, 0, 1):
    await repository.create_tier(db_session, user.id, _new_tier(rank=rank))

  tiers = await repository.list_tiers_by_user(db_session, user.id)
  assert [tier.rank for tier in tiers] == [0, 1, 2]


async def test_list_tiers_by_user_excludes_other_owners(
  db_session: AsyncSession,
) -> None:
  user = await _create_user(db_session)
  other = await _create_user(db_session)
  await repository.create_tier(db_session, user.id, _new_tier(rank=0))
  await repository.create_tier(db_session, other.id, _new_tier(rank=0))

  tiers = await repository.list_tiers_by_user(db_session, user.id)
  assert [tier.user_id for tier in tiers] == [user.id]


async def test_update_tier_persists_changes(db_session: AsyncSession) -> None:
  user = await _create_user(db_session)
  tier = await repository.create_tier(db_session, user.id, _new_tier())

  tier.name = "Gold"
  tier.price_cents = 1200
  updated = await repository.update_tier(db_session, tier)

  assert updated.name == "Gold"
  assert updated.price_cents == 1200

  # The change is durable, not just reflected on the returned object.
  refreshed = await repository.get_tier_by_id(db_session, tier.id)
  assert refreshed is not None
  assert refreshed.name == "Gold"
  assert refreshed.price_cents == 1200


async def test_delete_tier_removes_row(db_session: AsyncSession) -> None:
  user = await _create_user(db_session)
  tier = await repository.create_tier(db_session, user.id, _new_tier())
  tier_id = tier.id

  await repository.delete_tier(db_session, tier)

  assert await repository.get_tier_by_id(db_session, tier_id) is None


async def test_duplicate_name_per_owner_rejected(db_session: AsyncSession) -> None:
  """UNIQUE (user_id, name): the same owner can't reuse a tier name."""
  user = await _create_user(db_session)
  await repository.create_tier(db_session, user.id, _new_tier(name="Gold", rank=0))

  with pytest.raises(IntegrityError):
    await repository.create_tier(db_session, user.id, _new_tier(name="Gold", rank=1))


async def test_duplicate_rank_per_owner_rejected(db_session: AsyncSession) -> None:
  """UNIQUE (user_id, rank): two rungs can't share an access level."""
  user = await _create_user(db_session)
  await repository.create_tier(db_session, user.id, _new_tier(rank=3))

  with pytest.raises(IntegrityError):
    await repository.create_tier(db_session, user.id, _new_tier(rank=3))


async def test_same_name_and_rank_allowed_across_owners(
  db_session: AsyncSession,
) -> None:
  """The uniqueness is per owner — different creators can both have "Gold"."""
  user = await _create_user(db_session)
  other = await _create_user(db_session)

  await repository.create_tier(db_session, user.id, _new_tier(name="Gold", rank=0))
  tier = await repository.create_tier(
    db_session, other.id, _new_tier(name="Gold", rank=0)
  )
  assert tier.user_id == other.id
