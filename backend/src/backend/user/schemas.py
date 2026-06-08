"""Pydantic schemas for the user-facing API shape.

Two audiences, layered so the public field list lives in one place:

* :class:`PublicUser` — what any authenticated viewer may see (e.g. on a
  creator profile).
* :class:`PrivateUser` — the same, plus owner-only fields, returned only when
  a user is viewing themselves.

The ORM's ``google_sub`` appears in neither, so it can never reach the wire.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PublicUser(BaseModel):
  """A user as seen by anyone — safe to expose on a creator profile."""

  model_config = ConfigDict(from_attributes=True)

  id: uuid.UUID
  handle: str | None
  name: str
  bio: str | None
  avatar_url: str | None


class PrivateUser(PublicUser):
  """A user viewing themselves — adds owner-only fields."""

  email: str
  last_logged_in_at: datetime | None
  created_at: datetime
