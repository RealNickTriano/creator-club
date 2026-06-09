"""Pydantic schemas for the tier API shape.

Read side:

* :class:`PublicTier` — a tier as anyone may see it (the ladder is shown to
  every signed-in viewer, so there is no private variant).

Write side:

* :class:`NewTier` — what a creator supplies to add a rung to their ladder;
  the owner comes from the session, never the body.
* :class:`UpdateTier` — the owner-editable fields a creator may PATCH.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NewTier(BaseModel):
  """Fields needed to create a tier on the current user's ladder.

  ``price_cents: 0`` makes a free tier (conventionally ``rank 0``).
  """

  name: str = Field(min_length=1, max_length=80)
  rank: int = Field(ge=0)
  price_cents: int = Field(ge=0)
  description: str | None = None


class UpdateTier(BaseModel):
  """Owner-editable tier fields.

  PATCH semantics: only fields present in the request are applied; anything
  omitted is left untouched.
  """

  name: str | None = Field(default=None, min_length=1, max_length=80)
  rank: int | None = Field(default=None, ge=0)
  price_cents: int | None = Field(default=None, ge=0)
  description: str | None = None


class PublicTier(BaseModel):
  """A tier as seen by anyone — the ladder is public to signed-in viewers."""

  model_config = ConfigDict(from_attributes=True)

  id: uuid.UUID
  user_id: uuid.UUID
  name: str
  rank: int
  price_cents: int
  description: str | None
  created_at: datetime
  updated_at: datetime
