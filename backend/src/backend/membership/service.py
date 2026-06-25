"""Membership service — orchestrates the repository and applies transforms.

This layer holds the business logic (which repository calls to make, in what
order) and any value transforms; the repository stays pure database access.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.membership import repository
from backend.membership.models import Membership
from backend.tier.models import Tier
from backend.user.models import User

# Stripe subscription statuses where access has stopped — a membership in one of
# these is "terminal". Shared with the webhook handler (which uses it to end the
# period at ``ended_at``) and the atomic upsert (which lets a terminal status win
# a same-second ordering tie), so every layer agrees on what "ended" means.
ENDED_STATUSES = frozenset({"canceled", "unpaid", "incomplete_expired"})


async def list_memberships_by_member(
  session: AsyncSession, member_id: uuid.UUID
) -> list[tuple[Membership, Tier, User]]:
  """Return all memberships held by ``member_id``, each with its tier and creator."""
  return await repository.list_memberships_by_member(session, member_id)


async def get_membership_by_member_and_creator(
  session: AsyncSession, member_id: uuid.UUID, creator_id: uuid.UUID
) -> Membership | None:
  """Return this member's membership to this creator, or ``None``."""
  return await repository.get_membership_by_member_and_creator(
    session, member_id, creator_id
  )


async def set_membership(
  session: AsyncSession,
  member_id: uuid.UUID,
  creator_id: uuid.UUID,
  tier_id: uuid.UUID,
) -> tuple[Membership, bool]:
  """Upsert the member's membership to this creator onto ``tier_id``.

  The whole lifecycle in one call (see api-routes.html): no row → join;
  existing row → resume / re-tier, clearing ``canceled_at`` and reopening the
  period while keeping the original ``started_at``. The same tier is a no-op
  that returns the membership unchanged.

  Inputs are expected to be validated already (tier belongs to creator, not
  self) and any billing handled — that's the router's job, which only calls this
  for **free** tiers. A free membership has no Stripe subscription, so re-tiering
  here also clears any lingering ``stripe_subscription_id``/``status`` left by a
  now-lapsed paid subscription — leaving a clean, open-ended row.

  Returns ``(membership, created)`` so the route can answer 201 vs 200.
  """
  membership = await repository.get_membership_by_member_and_creator(
    session, member_id, creator_id
  )
  if membership is None:
    created = await repository.create_membership(
      session, member_id, creator_id, tier_id
    )
    return created, True

  if (
    membership.tier_id == tier_id
    and membership.canceled_at is None
    and membership.current_period_end is None
    and membership.stripe_subscription_id is None
  ):
    return membership, False  # already holding exactly this — no-op

  membership.tier_id = tier_id
  membership.canceled_at = None
  membership.current_period_end = None
  membership.stripe_subscription_id = None
  membership.status = None
  return await repository.update_membership(session, membership), False


async def retier(
  session: AsyncSession, membership: Membership, tier_id: uuid.UUID
) -> Membership:
  """Point an active paid membership at a new tier, in place.

  The optimistic local mirror of an in-place Stripe subscription tier swap (see
  :func:`backend.billing.change_subscription_tier`): the period and the
  subscription id are unchanged, so we only move ``tier_id`` and clear
  ``canceled_at`` (re-tiering reactivates). The ``customer.subscription.updated``
  webhook reconciles ``status``/``current_period_end`` right after.
  """
  membership.tier_id = tier_id
  membership.canceled_at = None
  return await repository.update_membership(session, membership)


async def provision_subscription(
  session: AsyncSession,
  *,
  member_id: uuid.UUID,
  creator_id: uuid.UUID,
  tier_id: uuid.UUID,
  stripe_subscription_id: str,
  status: str,
  current_period_end: datetime | None,
  canceled_at: datetime | None,
  last_event_at: datetime | None = None,
) -> Membership | None:
  """Upsert the membership backing a Stripe subscription (webhook-driven).

  This is the authority for *paid* memberships: it mirrors Stripe's state onto
  the row — the subscription id, its ``status``, and the real
  ``current_period_end`` (the access boundary the entitlement check reads) and
  ``canceled_at``. Keyed on (member, creator), so it upgrades an existing free
  membership in place and is idempotent across the duplicate/retried events
  Stripe may deliver.

  The write is a single atomic upsert (see
  :func:`backend.membership.repository.upsert_provisioned_membership`) so
  concurrent webhook deliveries can't race. Two guards, enforced in the
  statement, keep a stray event from corrupting the row:

  * *Superseded subscription* — if the row is currently active on a **different**
    subscription id, a late event (e.g. from a duplicate sub left by an earlier
    bug) must not clobber it.
  * *Out-of-order delivery* — ``last_event_at`` (the event's ``created`` time) is
    a monotonic marker: an event older than the last one applied is ignored, so a
    redelivered or reordered event can't truncate or resurrect access. On a
    same-second tie a terminal status wins.
  """
  return await repository.upsert_provisioned_membership(
    session,
    member_id=member_id,
    creator_id=creator_id,
    tier_id=tier_id,
    stripe_subscription_id=stripe_subscription_id,
    status=status,
    current_period_end=current_period_end,
    canceled_at=canceled_at,
    last_event_at=last_event_at,
    ended_statuses=ENDED_STATUSES,
  )


async def mark_canceled(
  session: AsyncSession, membership: Membership
) -> Membership:
  """Stamp the membership as canceled now.

  Audit only: ``current_period_end`` still gates access, so the fan keeps what
  they paid for until the period lapses (the cancellation is scheduled at
  period end in Stripe). The webhook re-stamps the same field idempotently when
  Stripe confirms.
  """
  membership.canceled_at = datetime.now(UTC)
  return await repository.update_membership(session, membership)
