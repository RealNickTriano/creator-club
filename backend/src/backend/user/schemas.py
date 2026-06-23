"""Pydantic schemas for the user-facing API shape.

Read side — two audiences, layered so the public field list lives in one place:

* :class:`PublicUser` — what any authenticated viewer may see (e.g. on a
  creator profile).
* :class:`PrivateUser` — the same, plus owner-only fields, returned only when
  a user is viewing themselves.

Write side:

* :class:`NewUser` — the inputs needed to create a user (the identity Google
  hands us at sign-in).
* :class:`UpdateUser` — the owner-editable profile fields a user may PATCH.

The ORM's ``google_sub`` appears in neither read schema, so it can never reach
the wire — but it *is* a creation input, hence its presence on :class:`NewUser`.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from backend.demo.identity import is_demo_email

HANDLE_PATTERN = r"^[a-z0-9_]{3,30}$"


class NewUser(BaseModel):
  """Fields needed to create a user, sourced from the Google profile.

  ``google_sub`` is optional: Google sign-in always supplies it, but a demo
  account (the "continue as demo" path) has no Google identity and leaves it
  unset. ``google_name`` and ``google_avatar_url`` are optional because Google
  may omit them. ``personal_name`` — the name Creator Club addresses the user
  by — defaults to ``google_name`` in the service when not supplied.
  """

  google_sub: str | None = None
  google_email: str
  google_name: str | None = None
  google_avatar_url: str | None = None
  personal_name: str | None = None


class UpdateUser(BaseModel):
  """Owner-editable profile fields.

  PATCH semantics: only fields present in the request are applied; anything
  omitted is left untouched. ``handle`` is constrained to a URL-safe slug
  (3–30 lowercase letters, digits or underscores) since it routes to
  ``/c/{handle}``.
  """

  handle: str | None = Field(default=None, pattern=HANDLE_PATTERN)
  bio: str | None = None
  display_name: str | None = None
  personal_name: str | None = None


class PublicUser(BaseModel):
  """A user as seen by anyone — safe to expose on a creator profile."""

  model_config = ConfigDict(from_attributes=True)

  id: uuid.UUID
  handle: str | None
  google_name: str | None
  display_name: str | None
  bio: str | None
  google_avatar_url: str | None


class PrivateUser(PublicUser):
  """A user viewing themselves — adds owner-only fields.

  ``personal_name`` is how Creator Club addresses the user (greetings,
  email) — it's not part of the public profile. ``is_demo`` lets the client
  surface "you're in demo mode" without re-deriving the rule.
  """

  google_email: str
  personal_name: str | None
  last_logged_in_at: datetime | None
  created_at: datetime

  @computed_field  # type: ignore[prop-decorator]
  @property
  def is_demo(self) -> bool:
    """Whether this is a throwaway 'continue as demo' account."""
    return is_demo_email(self.google_email)
