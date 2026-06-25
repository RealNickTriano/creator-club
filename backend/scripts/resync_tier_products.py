"""Backfill descriptive Stripe Product names for already-synced paid tiers.

One-off and idempotent: finds paid tiers (``price_cents > 0``) that already have
a ``stripe_product_id`` and re-pushes each Product through the billing module, so
its name/description pick up the creator-scoped format (e.g. "Jane Doe – Gold
membership") instead of the bare ``tier.name``. Prices are untouched — this only
updates the Product. Safe to rerun.

Needs the database up and ``STRIPE_SECRET_KEY`` configured (test mode). Run
from ``backend/``:

    uv run python scripts/resync_tier_products.py
"""

import asyncio

from sqlalchemy import select

from backend import billing
from backend.db import SessionLocal
from backend.tier.models import Tier
from backend.user.models import User

# Register every model on the shared metadata so Tier's foreign key to ``users``
# resolves when the query compiles (these modules are otherwise unused here).
import backend.membership.models  # noqa: E402,F401
import backend.post.models  # noqa: E402,F401


async def main() -> None:
  async with SessionLocal() as session:
    tiers = list(
      await session.scalars(
        select(Tier).where(
          Tier.price_cents > 0, Tier.stripe_product_id.is_not(None)
        )
      )
    )
    if not tiers:
      print("No synced paid tiers to update.")
      return

    for tier in tiers:
      creator = await session.get(User, tier.user_id)
      if creator is None:
        print(f"skipped {tier.name} ({tier.id}): creator not found")
        continue
      # Updates the existing Product's name/description in place (price kept).
      await billing.sync_tier_pricing(tier, creator)
      print(f"updated {tier.stripe_product_id} → {tier.name} for {creator.id}")

  print(f"Done: {len(tiers)} tier(s) processed.")


if __name__ == "__main__":
  asyncio.run(main())
