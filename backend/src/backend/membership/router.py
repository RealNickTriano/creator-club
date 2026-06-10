"""Membership routes — the relationship between a viewer and a creator."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.router import get_current_user
from backend.db import get_db
from backend.entitlements import membership_is_active_now
from backend.membership import service as membership_service
from backend.membership.models import Membership
from backend.membership.schemas import NewMembership, PublicMembership
from backend.tier import service as tier_service
from backend.tier.models import Tier
from backend.tier.schemas import PublicTier
from backend.user import service as user_service
from backend.user.models import User

router = APIRouter(prefix="/memberships", tags=["memberships"])


def _to_public(membership: Membership, tier: Tier) -> PublicMembership:
  """Assemble the response shape: row fields + held tier + derived status."""
  return PublicMembership(
    id=membership.id,
    member_id=membership.member_id,
    creator_id=membership.creator_id,
    started_at=membership.started_at,
    current_period_end=membership.current_period_end,
    canceled_at=membership.canceled_at,
    tier=PublicTier.model_validate(tier),
    active=membership_is_active_now(membership.current_period_end),
  )


@router.get("", response_model=list[PublicMembership])
async def list_my_memberships(
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> list[PublicMembership]:
  """List the current user's memberships (``member_id`` = you, from the session)."""
  pairs = await membership_service.list_memberships_by_member(db, user.id)
  return [_to_public(membership, tier) for membership, tier in pairs]


@router.post("", response_model=PublicMembership)
async def set_membership(
  new_membership: NewMembership,
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
  response: Response,
) -> PublicMembership:
  """Set the current user's membership with a creator to a tier (upsert).

  One call covers join / resume / upgrade / downgrade / no-op — the service
  decides from the existing row. 201 when a membership was newly created,
  200 otherwise.
  """
  creator = await user_service.get_user_by_id(db, new_membership.creator_id)
  if creator is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found."
    )

  tier = await tier_service.get_tier_by_id(db, new_membership.tier_id)
  if tier is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, detail="Tier not found."
    )
  if tier.user_id != creator.id:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="That tier does not belong to this creator.",
    )
  if user.id == creator.id:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="You can't subscribe to yourself.",
    )
  if tier.price_cents > 0:
    raise HTTPException(
      status_code=status.HTTP_402_PAYMENT_REQUIRED,
      detail="Paid tiers aren't available yet — billing is coming later.",
    )

  membership, created = await membership_service.set_membership(
    db, user.id, creator.id, tier.id
  )
  if created:
    response.status_code = status.HTTP_201_CREATED
  return _to_public(membership, tier)
