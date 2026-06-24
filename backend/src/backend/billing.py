"""Stripe billing integration (test mode only — see stripe-billing-plan.html).

Phase 1 lives here: keeping paid tiers in sync with Stripe **Products** and
**Prices** so a tier can be sold via Checkout later. A tier maps to one Product
(its name/description) carrying one active recurring Price (its ``price_cents``).

Prices are **immutable** in Stripe: changing a tier's price never edits the old
Price, it creates a new one and archives the old (existing subscriptions keep
the price they signed up on — exactly the behavior we want).

``charge_for_tier`` is the leftover simulated charge from before billing was
real; it still backs the paid-join flow until Phase 2 swaps that to Checkout.
"""

import asyncio
import logging
import uuid

from backend.stripe_client import get_stripe
from backend.tier.models import Tier

logger = logging.getLogger(__name__)

# How long the fake payment round-trip takes. Tests patch this to 0.
SIMULATED_BILLING_SECONDS = 2.0


def _product_params(tier: Tier) -> dict:
  """Stripe Product fields mirrored from the tier (description only if set)."""
  params: dict = {"name": tier.name, "metadata": {"tier_id": str(tier.id)}}
  if tier.description:
    params["description"] = tier.description
  return params


def _price_params(tier: Tier) -> dict:
  """A monthly recurring Price, in cents, under the tier's Product."""
  return {
    "product": tier.stripe_product_id,
    "currency": "usd",
    "unit_amount": tier.price_cents,
    "recurring": {"interval": "month"},
    "metadata": {"tier_id": str(tier.id)},
  }


async def sync_tier_pricing(tier: Tier) -> bool:
  """Ensure a paid tier has a Stripe Product + active recurring Price.

  Creates the Product and/or Price when their ids are missing, and keeps the
  Product's display fields in sync otherwise. A missing ``stripe_price_id``
  always means "create a Price at the current ``price_cents``" — to *reprice*,
  the caller nulls ``stripe_price_id`` first and archives the old one (see
  :func:`archive_price`), since Prices are immutable.

  Free tiers (``price_cents == 0``) carry no Stripe objects, so this is a no-op.
  Mutates ``tier``'s ``stripe_*`` ids in place and returns True if any changed,
  so the caller knows to persist.
  """
  if tier.price_cents <= 0:
    return False

  client = get_stripe()
  changed = False

  if tier.stripe_product_id is None:
    product = await client.v1.products.create_async(_product_params(tier))
    tier.stripe_product_id = product.id
    changed = True
  else:
    await client.v1.products.update_async(
      tier.stripe_product_id, _product_params(tier)
    )

  if tier.stripe_price_id is None:
    price = await client.v1.prices.create_async(_price_params(tier))
    tier.stripe_price_id = price.id
    changed = True

  return changed


async def archive_price(price_id: str) -> None:
  """Deactivate a Price so it's no longer offered.

  Prices can't be deleted; archiving (``active=False``) hides it from new
  checkouts while leaving any existing subscriptions on it untouched.
  """
  client = get_stripe()
  await client.v1.prices.update_async(price_id, {"active": False})


async def charge_for_tier(member_id: uuid.UUID, tier: Tier) -> None:
  """Pretend to charge ``member_id`` for ``tier``: log it and wait.

  Deferred-billing leftover — replaced by Stripe Checkout in Phase 2.
  """
  logger.info(
    "Simulated billing: charging user %s $%.2f for tier %r (%s)",
    member_id,
    tier.price_cents / 100,
    tier.name,
    tier.id,
  )
  await asyncio.sleep(SIMULATED_BILLING_SECONDS)
