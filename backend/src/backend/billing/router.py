"""Billing routes — a fan's own billing management.

The single endpoint here opens the Stripe Customer Portal, where a fan
self-serves their subscriptions (cancel, switch card, view invoices). Listing
the subscriptions themselves is the job of ``GET /memberships``.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend import billing
from backend.auth.router import get_current_user
from backend.config import settings
from backend.user.models import User

router = APIRouter(prefix="/billing", tags=["billing"])


class PortalSession(BaseModel):
  """A redirect to the Stripe Customer Portal."""

  portal_url: str


@router.post("/portal", response_model=PortalSession)
async def create_portal_session(
  user: Annotated[User, Depends(get_current_user)],
) -> PortalSession:
  """Open the Stripe Customer Portal for the signed-in user.

  400 if they have no Stripe Customer yet — they've never subscribed to a paid
  tier, so there's nothing to manage.
  """
  if user.stripe_customer_id is None:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="No billing account yet — subscribe to a paid tier first.",
    )
  return_url = f"{settings.frontend_url.rstrip('/')}/billing"
  url = await billing.create_billing_portal_session(
    user.stripe_customer_id, return_url
  )
  return PortalSession(portal_url=url)
