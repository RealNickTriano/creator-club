"""Tests for the tier service layer.

Like the repository tests, these run against the isolated Postgres
``db_session`` — the field-application logic is only meaningful once it's
actually persisted.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.tier import repository, service
from backend.tier.schemas import NewTier, UpdateTier
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


async def test_create_tier_assigns_owner(db_session: AsyncSession) -> None:
  user = await _create_user(db_session)
  tier = await service.create_tier(db_session, user.id, _new_tier())
  assert tier.user_id == user.id


async def test_list_tiers_by_user_orders_by_rank(db_session: AsyncSession) -> None:
  user = await _create_user(db_session)
  for rank in (5, 0):
    await service.create_tier(db_session, user.id, _new_tier(rank=rank))

  tiers = await service.list_tiers_by_user(db_session, user.id)
  assert [tier.rank for tier in tiers] == [0, 5]


async def test_update_tier_applies_and_persists_fields(
  db_session: AsyncSession,
) -> None:
  user = await _create_user(db_session)
  tier = await service.create_tier(db_session, user.id, _new_tier())

  updated = await service.update_tier(
    db_session, tier, UpdateTier(name="Gold", price_cents=1200)
  )

  assert updated.name == "Gold"
  assert updated.price_cents == 1200

  # Durable, not just reflected on the returned object.
  refreshed = await repository.get_tier_by_id(db_session, tier.id)
  assert refreshed is not None
  assert refreshed.name == "Gold"
  assert refreshed.price_cents == 1200


async def test_update_tier_only_touches_provided_fields(
  db_session: AsyncSession,
) -> None:
  """PATCH semantics: omitted fields keep their stored value."""
  user = await _create_user(db_session)
  tier = await service.create_tier(
    db_session, user.id, _new_tier(name="Gold", description="Early access")
  )

  await service.update_tier(db_session, tier, UpdateTier(price_cents=0))

  refreshed = await repository.get_tier_by_id(db_session, tier.id)
  assert refreshed is not None
  assert refreshed.price_cents == 0
  assert refreshed.name == "Gold"  # left untouched by the price-only update
  assert refreshed.description == "Early access"


async def test_update_tier_bumps_updated_at(db_session: AsyncSession) -> None:
  user = await _create_user(db_session)
  tier = await service.create_tier(db_session, user.id, _new_tier())
  before = tier.updated_at

  updated = await service.update_tier(db_session, tier, UpdateTier(name="Gold"))

  assert updated.updated_at > before


async def test_delete_tier_removes_row(db_session: AsyncSession) -> None:
  user = await _create_user(db_session)
  tier = await service.create_tier(db_session, user.id, _new_tier())
  tier_id = tier.id

  await service.delete_tier(db_session, tier)

  assert await service.get_tier_by_id(db_session, tier_id) is None
