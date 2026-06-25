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
  CancelMembership,
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
    status=membership.status,
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

  existing = await membership_service.get_membership_by_member_and_creator(
    db, user.id, creator.id
  )
  # A live paid subscription with this creator (at most one — the row is unique
  # per member·creator) is modified in place rather than re-bought; a lapsed one
  # falls through to a fresh join.
  has_live_subscription = (
    existing is not None
    and existing.stripe_subscription_id is not None
    and membership_is_active_now(existing.current_period_end)
  )

  if tier.price_cents > 0:
    if has_live_subscription:
      # Tier change on an existing subscription: swap the price in place so the
      # fan keeps one subscription (no second charge). Re-selecting the held
      # tier is a no-op unless it was pending cancellation (then it resumes).
      if existing.tier_id == tier.id and existing.canceled_at is None:
        return _to_public(existing, tier, creator)
      await billing.change_subscription_tier(
        existing.stripe_subscription_id, user, tier, creator
      )
      # Optimistic local mirror; the subscription.updated webhook reconciles
      # status/period. Matches how cancel stamps the row ahead of its webhook.
      updated = await membership_service.retier(db, existing, tier.id)
      return _to_public(updated, tier, creator)

    # New paid subscription: hand off to Stripe Checkout. Ensure the fan has a
    # Customer (created once, then reused), then return the hosted URL for the
    # client to redirect to. The membership is created by the webhook once
    # payment completes.
    if user.stripe_customer_id is None:
      customer_id = await billing.create_customer(user)
      user = await user_service.attach_stripe_customer(db, user, customer_id)
    checkout_url = await billing.create_subscription_checkout(user, tier, creator)
    return CheckoutSession(checkout_url=checkout_url)

  # Free tier. Switching off a live paid subscription isn't a tier change — the
  # fan cancels first (keeping access until period end), then joins free once it
  # lapses. Blocking here keeps "stop paying" on the one correct cancel path.
  if has_live_subscription:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="Cancel your membership to move to the free tier.",
    )

  membership, created = await membership_service.set_membership(
    db, user.id, creator.id, tier.id
  )
  if created:
    response.status_code = status.HTTP_201_CREATED
  return _to_public(membership, tier, creator)


@router.post("/cancel", response_model=PublicMembership)
async def cancel_membership(
  body: CancelMembership,
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> PublicMembership:
  """Cancel the current user's membership with a creator.

  A paid membership's Stripe subscription is scheduled to end at period close,
  so access continues until then; the row is stamped canceled now for immediate
  feedback (the webhook reconfirms it). 404 if no such membership.
  """
  membership = await membership_service.get_membership_by_member_and_creator(
    db, user.id, body.creator_id
  )
  if membership is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found."
    )

  if membership.stripe_subscription_id:
    await billing.cancel_subscription(membership.stripe_subscription_id)
  membership = await membership_service.mark_canceled(db, membership)

  tier = await tier_service.get_tier_by_id(db, membership.tier_id)
  creator = await user_service.get_user_by_id(db, membership.creator_id)
  return _to_public(membership, tier, creator)
