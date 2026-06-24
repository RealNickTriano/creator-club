"""Stripe webhook handling — turn events into membership state.

Webhooks are the **source of truth** for paid memberships (see
stripe-billing-plan.html): a subscription's life — first payment, monthly
renewal, card failure, cancellation — happens away from our UI, and Stripe
reports each step here. Every relevant event funnels to one place
(:func:`_provision`) that mirrors the Stripe Subscription onto the membership
row, so the existing entitlement check (which gates on ``current_period_end``)
keeps working untouched.

Handlers are deliberately idempotent: Stripe retries on non-200s and may send
the same event more than once, so we always upsert by (member, creator) rather
than assume a create-vs-update.
"""

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend import billing
from backend.membership import service as membership_service
from backend.membership.models import Membership

logger = logging.getLogger(__name__)

# Subscription lifecycle events whose payload object *is* the Subscription.
_SUBSCRIPTION_EVENTS = {
  "customer.subscription.created",
  "customer.subscription.updated",
  "customer.subscription.deleted",
}

# Statuses where the subscription has stopped granting access; for these we end
# the period at ``ended_at`` so the membership lapses immediately.
_ENDED_STATUSES = {"canceled", "unpaid", "incomplete_expired"}

_METADATA_KEYS = ("member_id", "creator_id", "tier_id")


async def handle_event(session: AsyncSession, event: object) -> None:
  """Route a verified Stripe event to its membership write (if any).

  Unrecognised event types are ignored — we subscribe narrowly, but Stripe may
  still deliver more than we handle.
  """
  event_type = event["type"]
  obj = event["data"]["object"]

  if event_type == "checkout.session.completed":
    # The session carries the new subscription's id; fetch the Subscription
    # (its items hold current_period_end) and provision from that.
    subscription_id = getattr(obj, "subscription", None)
    if subscription_id:
      subscription = await billing.get_subscription(subscription_id)
      await _provision(session, subscription)
  elif event_type in _SUBSCRIPTION_EVENTS:
    await _provision(session, obj)
  else:
    logger.debug("Stripe webhook: ignoring event type %s", event_type)


async def _provision(session: AsyncSession, subscription: object) -> Membership | None:
  """Mirror a Stripe Subscription onto its membership row.

  Returns the membership, or ``None`` when the subscription lacks the linking
  metadata we set at checkout (nothing we can map it to).
  """
  ids = _membership_ids(subscription)
  if ids is None:
    return None
  member_id, creator_id, tier_id = ids

  status = subscription["status"]
  ended_at = _to_datetime(getattr(subscription, "ended_at", None))
  # Active/past_due/etc. run to the item's period end; a fully ended
  # subscription lapses at ended_at so access stops right away.
  if status in _ENDED_STATUSES and ended_at is not None:
    current_period_end = ended_at
  else:
    current_period_end = _period_end(subscription)

  return await membership_service.provision_subscription(
    session,
    member_id=member_id,
    creator_id=creator_id,
    tier_id=tier_id,
    stripe_subscription_id=subscription["id"],
    status=status,
    current_period_end=current_period_end,
    canceled_at=_to_datetime(getattr(subscription, "canceled_at", None)),
  )


def _membership_ids(
  subscription: object,
) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID] | None:
  """Parse (member_id, creator_id, tier_id) from the subscription metadata."""
  metadata = getattr(subscription, "metadata", None)
  if metadata is None or any(key not in metadata for key in _METADATA_KEYS):
    logger.warning(
      "Stripe webhook: subscription %s missing linking metadata; skipping.",
      subscription["id"],
    )
    return None
  try:
    return tuple(uuid.UUID(metadata[key]) for key in _METADATA_KEYS)  # type: ignore[return-value]
  except ValueError:
    logger.warning(
      "Stripe webhook: subscription %s has non-UUID metadata; skipping.",
      subscription["id"],
    )
    return None


def _period_end(subscription: object) -> datetime | None:
  """The current period end, which lives on the first subscription item."""
  items = subscription["items"]["data"] if "items" in subscription else []
  if not items:
    return None
  item = items[0]
  raw = item["current_period_end"] if "current_period_end" in item else None
  return _to_datetime(raw)


def _to_datetime(epoch_seconds: int | None) -> datetime | None:
  """Convert a Stripe unix timestamp to a timezone-aware UTC datetime."""
  if not epoch_seconds:
    return None
  return datetime.fromtimestamp(epoch_seconds, tz=UTC)
