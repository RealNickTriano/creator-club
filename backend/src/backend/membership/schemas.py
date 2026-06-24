"""Pydantic schemas for the membership API shape.

Write side:

* :class:`NewMembership` — the (creator, tier) pair the current user wants to
  hold; the member always comes from the session, never the body.

Read side:

* :class:`PublicMembership` — the membership with its held tier and the
  creator's public profile embedded, plus the derived ``active`` status, so
  clients never re-derive or re-fetch any of it.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.tier.schemas import PublicTier
from backend.user.schemas import PublicUser


class NewMembership(BaseModel):
  """The target of the upsert: hold this tier of this creator."""

  creator_id: uuid.UUID
  tier_id: uuid.UUID


class CheckoutSession(BaseModel):
  """A redirect to Stripe Checkout, returned when a paid tier needs payment.

  The membership isn't created yet — the webhook provisions it once payment
  completes — so the client redirects the browser to ``checkout_url``.
  """

  checkout_url: str


class PublicMembership(BaseModel):
  """A membership as returned to the member: row fields + tier + creator + status."""

  model_config = ConfigDict(from_attributes=True)

  id: uuid.UUID
  member_id: uuid.UUID
  creator_id: uuid.UUID
  started_at: datetime
  current_period_end: datetime | None
  canceled_at: datetime | None
  tier: PublicTier
  creator: PublicUser
  active: bool
