"""Tier service — orchestrates the repository and applies transforms.

This layer holds the business logic (which repository calls to make, in what
order) and any value transforms; the repository stays pure database access.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.tier import repository
from backend.tier.models import Tier
from backend.tier.schemas import NewTier, UpdateTier


async def create_tier(
  session: AsyncSession, user_id: uuid.UUID, new_tier: NewTier
) -> Tier:
  """Add a rung to this user's ladder and return it."""
  return await repository.create_tier(session, user_id, new_tier)


async def get_tier_by_id(
  session: AsyncSession, tier_id: uuid.UUID
) -> Tier | None:
  """Return the tier with this id, or ``None``."""
  return await repository.get_tier_by_id(session, tier_id)


async def list_tiers_by_user(
  session: AsyncSession, user_id: uuid.UUID
) -> list[Tier]:
  """Return this user's tier ladder, ordered by ``rank`` ascending."""
  return await repository.list_tiers_by_user(session, user_id)


async def update_tier(
  session: AsyncSession, tier: Tier, update: UpdateTier
) -> Tier:
  """Apply the provided fields to ``tier`` and persist them.

  Only fields actually present in ``update`` are written (PATCH semantics), so
  omitting a field leaves the stored value alone. ``updated_at`` is bumped by
  the model's ``onupdate`` when anything changes.
  """
  for field, value in update.model_dump(exclude_unset=True).items():
    setattr(tier, field, value)
  return await repository.update_tier(session, tier)


async def delete_tier(session: AsyncSession, tier: Tier) -> None:
  """Delete the tier from the database."""
  await repository.delete_tier(session, tier)
