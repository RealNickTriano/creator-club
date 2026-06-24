"""Stripe webhook route — verifies and dispatches inbound events.

Unlike the rest of the API there's no session cookie here: the request comes
from Stripe, not a browser, and the **signature is the authentication**. We read
the raw body (signature verification needs the exact bytes), verify it, then
hand the parsed event to the service.
"""

from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend import billing
from backend.db import get_db
from backend.webhooks import service as webhook_service

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
  request: Request,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
  """Receive a Stripe event, verify its signature, and apply it.

  Returns 200 on success (Stripe retries anything else) and 400 when the
  signature is missing or invalid.
  """
  payload = await request.body()
  signature = request.headers.get("stripe-signature")
  try:
    event = billing.construct_event(payload, signature)
  except (ValueError, stripe.SignatureVerificationError) as exc:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Invalid Stripe webhook signature.",
    ) from exc

  await webhook_service.handle_event(db, event)
  return Response(status_code=status.HTTP_200_OK)
