"""Membership repository — database operations only, no business logic."""

import uuid
from collections.abc import Collection
from datetime import datetime

from sqlalchemy import and_, func, not_, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.membership.models import Membership
from backend.tier.models import Tier
from backend.user.models import User


async def create_membership(
  session: AsyncSession,
  member_id: uuid.UUID,
  creator_id: uuid.UUID,
  tier_id: uuid.UUID,
) -> Membership:
  """Insert and return a new membership of ``member_id`` to ``creator_id``."""
  membership = Membership(
    member_id=member_id, creator_id=creator_id, tier_id=tier_id
  )
  session.add(membership)
  await session.commit()
  await session.refresh(membership)
  return membership


async def get_membership_by_member_and_creator(
  session: AsyncSession, member_id: uuid.UUID, creator_id: uuid.UUID
) -> Membership | None:
  """Return this member's membership to this creator, or ``None``.

  At most one exists, per the (member_id, creator_id) uniqueness.
  """
  return await session.scalar(
    select(Membership).where(
      Membership.member_id == member_id,
      Membership.creator_id == creator_id,
    )
  )


async def list_memberships_by_member(
  session: AsyncSession, member_id: uuid.UUID
) -> list[tuple[Membership, Tier, User]]:
  """Return all of this member's memberships, each with its held tier and creator."""
  rows = await session.execute(
    select(Membership, Tier, User)
    .join(Tier, Membership.tier_id == Tier.id)
    .join(User, Membership.creator_id == User.id)
    .where(Membership.member_id == member_id)
    .order_by(Membership.started_at)
  )
  return [(membership, tier, creator) for membership, tier, creator in rows.all()]


async def update_membership(
  session: AsyncSession, membership: Membership
) -> Membership:
  """Persist ``membership``, replacing the stored row with this object's state."""
  merged = await session.merge(membership)
  await session.commit()
  await session.refresh(merged)
  return merged


async def upsert_provisioned_membership(
  session: AsyncSession,
  *,
  member_id: uuid.UUID,
  creator_id: uuid.UUID,
  tier_id: uuid.UUID,
  stripe_subscription_id: str,
  status: str,
  current_period_end: datetime | None,
  canceled_at: datetime | None,
  last_event_at: datetime | None,
  ended_statuses: Collection[str],
) -> Membership | None:
  """Atomically mirror a Stripe subscription onto the (member, creator) row.

  A single ``INSERT … ON CONFLICT DO UPDATE`` so two concurrent webhook
  deliveries can't race: Postgres serialises on the unique index, and the
  guard conditions live in the statement's ``WHERE`` (a compare-and-set the
  database evaluates against the latest committed row), not in a separate
  read-then-write. The two guards mirror the service's intent:

  * **Superseded subscription** — don't let an event from a *different*
    subscription clobber a row that's currently active on another one.
  * **Out-of-order delivery** — don't let an event older than the one already
    applied (``last_event_at``) overwrite newer state; on a same-second tie a
    terminal status wins, so a stale ``active`` can't resurrect a cancellation.

  ``last_event_at`` only ever advances (``COALESCE`` keeps the stored marker
  when an event carries no ``created``). Returns the row, or ``None`` only if a
  concurrent delete removed it (not expected in this app).

  Does **not** commit: the webhook handler owns the transaction so this write
  and the event-idempotency claim commit together (see
  :func:`backend.webhooks.service.handle_event`).
  """
  stmt = pg_insert(Membership).values(
    member_id=member_id,
    creator_id=creator_id,
    tier_id=tier_id,
    stripe_subscription_id=stripe_subscription_id,
    status=status,
    current_period_end=current_period_end,
    canceled_at=canceled_at,
    last_event_at=last_event_at,
  )
  excluded = stmt.excluded
  ended = list(ended_statuses)

  superseded = and_(
    Membership.stripe_subscription_id.isnot(None),
    Membership.stripe_subscription_id != excluded.stripe_subscription_id,
    or_(
      Membership.current_period_end.is_(None),
      Membership.current_period_end > func.now(),
    ),
  )
  stale = and_(
    Membership.last_event_at.isnot(None),
    excluded.last_event_at.isnot(None),
    or_(
      excluded.last_event_at < Membership.last_event_at,
      and_(
        excluded.last_event_at == Membership.last_event_at,
        Membership.status.in_(ended),
        excluded.status.not_in(ended),
      ),
    ),
  )

  stmt = stmt.on_conflict_do_update(
    index_elements=["member_id", "creator_id"],
    set_={
      "tier_id": excluded.tier_id,
      "stripe_subscription_id": excluded.stripe_subscription_id,
      "status": excluded.status,
      "current_period_end": excluded.current_period_end,
      "canceled_at": excluded.canceled_at,
      "last_event_at": func.coalesce(
        excluded.last_event_at, Membership.last_event_at
      ),
    },
    where=and_(not_(superseded), not_(stale)),
  )

  await session.execute(stmt)
  await session.flush()
  # Re-read the authoritative row (populate_existing refreshes any cached
  # instance) within the same uncommitted transaction, so callers get the
  # effective state whether the update fired or a guard skipped it.
  return await session.scalar(
    select(Membership)
    .where(
      Membership.member_id == member_id,
      Membership.creator_id == creator_id,
    )
    .execution_options(populate_existing=True)
  )
