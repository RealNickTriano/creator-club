"""Membership routes — the relationship between a viewer and a creator."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend import billing
from backend.auth.router import get_current_user
from backend.db import get_db
from backend.entitlements import membership_is_active_now
from backend.membership import service as membership_service
from backend.membership.models import Membership
from backend.membership.schemas import (
  CheckoutSession,
  NewMembership,
  PublicMembership,
)
from backend.tier import service as tier_service
from backend.tier.models import Tier
from backend.tier.schemas import PublicTier
from backend.user import service as user_service
from backend.user.models import User
from backend.user.schemas import PublicUser

router = APIRouter(prefix="/memberships", tags=["memberships"])


def _to_public(
  membership: Membership, tier: Tier, creator: User
) -> PublicMembership:
  """Assemble the response shape: row fields + tier + creator + derived status."""
  return PublicMembership(
    id=membership.id,
    member_id=membership.member_id,
    creator_id=membership.creator_id,
    started_at=membership.started_at,
    current_period_end=membership.current_period_end,
    canceled_at=membership.canceled_at,
    tier=PublicTier.model_validate(tier),
    creator=PublicUser.model_validate(creator),
    active=membership_is_active_now(membership.current_period_end),
  )


@router.get("", response_model=list[PublicMembership])
async def list_my_memberships(
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> list[PublicMembership]:
  """List the current user's memberships (``member_id`` = you, from the session)."""
  rows = await membership_service.list_memberships_by_member(db, user.id)
  return [_to_public(membership, tier, creator) for membership, tier, creator in rows]


@router.post("", response_model=PublicMembership | CheckoutSession)
async def set_membership(
  new_membership: NewMembership,
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
  response: Response,
) -> PublicMembership | CheckoutSession:
  """Join a creator at a tier.

  **Free tiers** upsert directly — one call covers join / resume / downgrade /
  no-op, the service deciding from the existing row (201 when newly created,
  200 otherwise). **Paid tiers** can't grant access until money changes hands,
  so instead of upserting we return a Stripe Checkout URL; the membership is
  provisioned later from the webhook (see stripe-billing-plan.html).
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
    # Paid: hand off to Stripe Checkout. Ensure the fan has a Customer (created
    # once, then reused), then return the hosted URL for the client to redirect
    # to. The membership is created by the webhook once payment completes.
    if user.stripe_customer_id is None:
      customer_id = await billing.create_customer(user)
      user = await user_service.attach_stripe_customer(db, user, customer_id)
    checkout_url = await billing.create_subscription_checkout(user, tier, creator)
    return CheckoutSession(checkout_url=checkout_url)

  membership, created = await membership_service.set_membership(
    db, user.id, creator.id, tier.id
  )
  if created:
    response.status_code = status.HTTP_201_CREATED
  return _to_public(membership, tier, creator)
