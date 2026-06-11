"""Pydantic schemas for the post API shape.

Read side:

* :class:`PostAccess` — the entitlement decision for one viewer/post pair.
* :class:`PublicPost` — a post as a viewer sees it: metadata + teaser always,
  ``body`` only when the attached :class:`PostAccess` allows it.

Write side:

* :class:`NewPost` — what an author supplies to create a post; the author
  comes from the session, never the body.
* :class:`UpdatePost` — the author-editable fields, including ``published_at``
  to publish (set) or revert to draft (null).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from backend.entitlements import PostAccessReason
from backend.tier.schemas import PublicTier


class NewPost(BaseModel):
  """Fields needed to create a post (as a draft) for the current user.

  ``required_tier_id: None`` makes the post public; otherwise it must point at
  one of the author's own tiers.
  """

  title: str = Field(min_length=1, max_length=200)
  teaser: str
  body: str
  required_tier_id: uuid.UUID | None = None


class UpdatePost(BaseModel):
  """Author-editable post fields.

  PATCH semantics: only fields present in the request are applied. Setting
  ``published_at`` publishes a draft; explicitly nulling it reverts a post to
  draft. Likewise ``required_tier_id: null`` makes the post public.
  """

  title: str | None = Field(default=None, min_length=1, max_length=200)
  teaser: str | None = None
  body: str | None = None
  required_tier_id: uuid.UUID | None = None
  published_at: datetime | None = None


class PostAccess(BaseModel):
  """Can the current viewer see this post's body — and if not, why not?

  ``required_tier`` is the tier that would unlock the post (the upsell);
  ``None`` for public posts.
  """

  allowed: bool
  reason: PostAccessReason
  required_tier: PublicTier | None


class PublicPost(BaseModel):
  """A post as one viewer sees it, entitlement already applied.

  ``teaser`` is always present; ``body`` is ``None`` unless ``access.allowed``.
  """

  id: uuid.UUID
  user_id: uuid.UUID
  title: str
  teaser: str
  body: str | None
  required_tier_id: uuid.UUID | None
  published_at: datetime | None
  created_at: datetime
  access: PostAccess
