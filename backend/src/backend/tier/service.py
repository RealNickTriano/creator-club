"""Tier service — orchestrates the repository and applies transforms.

This layer holds the business logic (which repository calls to make, in what
order) and any value transforms; the repository stays pure database access.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend import billing
from backend.tier import repository
from backend.tier.models import Tier
from backend.tier.schemas import NewTier, UpdateTier
from backend.user import service as user_service


async def create_tier(
  session: AsyncSession, user_id: uuid.UUID, new_tier: NewTier
) -> Tier:
  """Add a rung to this user's ladder and return it.

  Paid tiers are synced to a Stripe Product/Price so they can be sold; the
  resulting ids are persisted. Free tiers carry no Stripe objects.
  """
  tier = await repository.create_tier(session, user_id, new_tier)
  creator = await user_service.get_user_by_id(session, user_id)
  if creator and await billing.sync_tier_pricing(tier, creator):
    tier = await repository.update_tier(session, tier)
  return tier


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

  Stripe is kept in step for paid tiers: a name/description edit updates the
  Product; a price change points the tier at a fresh Price and archives the old
  one (Prices are immutable). Tiers not yet synced get their Product/Price
  created. Unrelated edits (e.g. rank only) make no Stripe call.
  """
  fields = update.model_dump(exclude_unset=True)
  old_price_cents = tier.price_cents
  old_price_id = tier.stripe_price_id
  for field, value in fields.items():
    setattr(tier, field, value)

  price_changed = tier.price_cents != old_price_cents
  display_changed = "name" in fields or "description" in fields
  unsynced_paid = tier.price_cents > 0 and old_price_id is None

  if price_changed or display_changed or unsynced_paid:
    creator = await user_service.get_user_by_id(session, tier.user_id)
    if price_changed:
      tier.stripe_price_id = None  # immutable Price → create a fresh one
    if creator:
      await billing.sync_tier_pricing(tier, creator)
    if price_changed and old_price_id:
      await billing.archive_price(old_price_id)

  return await repository.update_tier(session, tier)


async def delete_tier(session: AsyncSession, tier: Tier) -> None:
  """Delete the tier from the database."""
  await repository.delete_tier(session, tier)
