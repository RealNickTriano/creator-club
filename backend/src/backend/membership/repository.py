"""Membership repository — database operations only, no business logic."""

import uuid

from sqlalchemy import select
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
