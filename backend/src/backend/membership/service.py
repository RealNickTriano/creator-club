"""Membership service — orchestrates the repository and applies transforms.

This layer holds the business logic (which repository calls to make, in what
order) and any value transforms; the repository stays pure database access.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.membership import repository
from backend.membership.models import Membership
from backend.tier.models import Tier


async def list_memberships_by_member(
  session: AsyncSession, member_id: uuid.UUID
) -> list[tuple[Membership, Tier]]:
  """Return all memberships held by ``member_id``, each with its tier."""
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
  self, free tier) — that's the router's job. ``current_period_end = None`` is
  open-ended, which is only correct while every reachable tier is free; the
  billing phase replaces this with real period bookkeeping.

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
  ):
    return membership, False  # already holding exactly this — no-op

  membership.tier_id = tier_id
  membership.canceled_at = None
  membership.current_period_end = None
  return await repository.update_membership(session, membership), False
