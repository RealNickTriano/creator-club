"""Tier repository — database operations only, no business logic."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.tier.models import Tier
from backend.tier.schemas import NewTier


async def create_tier(
  session: AsyncSession, user_id: uuid.UUID, new_tier: NewTier
) -> Tier:
  """Insert and return a new tier owned by ``user_id``."""
  tier = Tier(user_id=user_id, **new_tier.model_dump())
  session.add(tier)
  await session.commit()
  await session.refresh(tier)
  return tier


async def get_tier_by_id(session: AsyncSession, tier_id: uuid.UUID) -> Tier | None:
  """Return the tier with this id, or ``None``."""
  return await session.get(Tier, tier_id)


async def list_tiers_by_user(
  session: AsyncSession, user_id: uuid.UUID
) -> list[Tier]:
  """Return all tiers owned by this user, ordered by ``rank`` ascending."""
  result = await session.scalars(
    select(Tier).where(Tier.user_id == user_id).order_by(Tier.rank)
  )
  return list(result)


async def update_tier(session: AsyncSession, tier: Tier) -> Tier:
  """Persist ``tier``, replacing the stored row with this object's state."""
  merged = await session.merge(tier)
  await session.commit()
  await session.refresh(merged)
  return merged


async def delete_tier(session: AsyncSession, tier: Tier) -> None:
  """Remove ``tier`` from the database."""
  await session.delete(tier)
  await session.commit()
