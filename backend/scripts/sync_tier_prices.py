"""Backfill Stripe Products/Prices for existing paid tiers.

One-off and idempotent: finds paid tiers (``price_cents > 0``) that don't yet
have a ``stripe_price_id`` and syncs each through the billing module, creating
its Stripe Product + recurring Price. Safe to rerun — already-synced tiers are
skipped by the query.

Needs the database up and ``STRIPE_SECRET_KEY`` configured (test mode). Run
from ``backend/``:

    uv run python scripts/sync_tier_prices.py
"""

import asyncio

from sqlalchemy import select

from backend import billing
from backend.db import SessionLocal
from backend.tier.models import Tier

# Register every model on the shared metadata so Tier's foreign key to ``users``
# resolves when the query compiles (these modules are otherwise unused here).
import backend.membership.models  # noqa: E402,F401
import backend.post.models  # noqa: E402,F401
import backend.user.models  # noqa: E402,F401


async def main() -> None:
  async with SessionLocal() as session:
    tiers = list(
      await session.scalars(
        select(Tier).where(
          Tier.price_cents > 0, Tier.stripe_price_id.is_(None)
        )
      )
    )
    if not tiers:
      print("No paid tiers need syncing.")
      return

    for tier in tiers:
      await billing.sync_tier_pricing(tier)
      await session.commit()
      print(
        f"synced {tier.name} (${tier.price_cents / 100:.2f}) "
        f"→ {tier.stripe_price_id}"
      )

  print(f"Done: {len(tiers)} tier(s) synced.")


if __name__ == "__main__":
  asyncio.run(main())
