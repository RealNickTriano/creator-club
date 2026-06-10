"""Placeholder billing — logs and waits instead of charging.

Real payments are a deferred phase. This stub stands in so paid tiers can be
joined today: it logs the would-be charge and sleeps briefly to feel like a
real payment round-trip. The real implementation replaces this module (and
brings actual period bookkeeping with it).
"""

import asyncio
import logging
import uuid

from backend.tier.models import Tier

logger = logging.getLogger(__name__)

# How long the fake payment round-trip takes. Tests patch this to 0.
SIMULATED_BILLING_SECONDS = 2.0


async def charge_for_tier(member_id: uuid.UUID, tier: Tier) -> None:
  """Pretend to charge ``member_id`` for ``tier``: log it and wait."""
  logger.info(
    "Simulated billing: charging user %s $%.2f for tier %r (%s)",
    member_id,
    tier.price_cents / 100,
    tier.name,
    tier.id,
  )
  await asyncio.sleep(SIMULATED_BILLING_SECONDS)
