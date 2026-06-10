"""Pydantic schemas for the membership API shape.

Write side:

* :class:`NewMembership` — the (creator, tier) pair the current user wants to
  hold; the member always comes from the session, never the body.

Read side:

* :class:`PublicMembership` — the membership with its held tier embedded and
  the derived ``active`` status, so clients never re-derive it.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.tier.schemas import PublicTier


class NewMembership(BaseModel):
  """The target of the upsert: hold this tier of this creator."""

  creator_id: uuid.UUID
  tier_id: uuid.UUID


class PublicMembership(BaseModel):
  """A membership as returned to the member: row fields + tier + status."""

  model_config = ConfigDict(from_attributes=True)

  id: uuid.UUID
  member_id: uuid.UUID
  creator_id: uuid.UUID
  started_at: datetime
  current_period_end: datetime | None
  canceled_at: datetime | None
  tier: PublicTier
  active: bool
