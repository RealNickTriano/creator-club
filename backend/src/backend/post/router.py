"""Post routes — creating, editing, and reading gated content.

Reads apply the entitlement decision for the current viewer: the teaser is
always returned, the body only when allowed. Writes are author-only — the
author always comes from the session.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.router import get_current_user, get_current_user_or_none
from backend.db import get_db
from backend.entitlements import PostAccessDecision
from backend.post import service as post_service
from backend.post.models import Post
from backend.post.schemas import NewPost, PostAccess, PublicPost, UpdatePost
from backend.tier import service as tier_service
from backend.tier.models import Tier
from backend.tier.schemas import PublicTier
from backend.user import service as user_service
from backend.user.models import User

router = APIRouter(prefix="/posts", tags=["posts"])


def _to_public(
  post: Post, decision: PostAccessDecision, required_tier: Tier | None
) -> PublicPost:
  """Assemble the response shape: metadata + teaser, body only when allowed."""
  return PublicPost(
    id=post.id,
    user_id=post.user_id,
    title=post.title,
    teaser=post.teaser,
    body=post.body if decision.allowed else None,
    required_tier_id=post.required_tier_id,
    published_at=post.published_at,
    created_at=post.created_at,
    access=PostAccess(
      allowed=decision.allowed,
      reason=decision.reason,
      required_tier=PublicTier.model_validate(required_tier)
      if required_tier
      else None,
    ),
  )


async def get_owned_post(
  post_id: uuid.UUID,
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> Post:
  """Resolve the post and verify the session user authored it.

  404 if no such post; 403 if it belongs to someone else. The shared guard for
  the author-only ``/posts/{post_id}`` routes (PATCH, DELETE).
  """
  post = await post_service.get_post_by_id(db, post_id)
  if post is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
  if post.user_id != user.id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
  return post


async def get_viewable_post(
  post_id: uuid.UUID,
  viewer: Annotated[User | None, Depends(get_current_user_or_none)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> Post:
  """Resolve the post for reading: drafts exist only for their author.

  404 if no such post, or if it's a draft and the viewer isn't the author —
  hiding the draft's existence rather than answering 403.
  """
  post = await post_service.get_post_by_id(db, post_id)
  if post is None or (
    post.published_at is None and (viewer is None or viewer.id != post.user_id)
  ):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
  return post


async def _require_own_tier(
  db: AsyncSession, user: User, tier_id: uuid.UUID
) -> None:
  """400 unless ``tier_id`` is one of this user's own tiers.

  A post may only be gated by a rung of its author's own ladder — anything
  else would compare ranks across unrelated ladders.
  """
  tier = await tier_service.get_tier_by_id(db, tier_id)
  if tier is None or tier.user_id != user.id:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="required_tier_id must be one of your own tiers.",
    )


@router.get("", response_model=list[PublicPost])
async def list_creator_posts(
  handle: str,
  viewer: Annotated[User | None, Depends(get_current_user_or_none)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> list[PublicPost]:
  """A creator's published feed (by handle), entitlements applied per viewer.

  Drafts are excluded. Each item carries metadata + teaser + the access
  decision; the body is included only when allowed. Open to signed-out
  visitors for the same reason as ``GET /tiers``: it backs the creator page,
  and a signed-out viewer is simply one with no membership (locked posts
  return their teaser and the tier to unlock).
  """
  creator = await user_service.get_user_by_handle(db, handle)
  if creator is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
  views = await post_service.list_feed(db, creator.id, viewer)
  return [_to_public(post, decision, tier) for post, decision, tier in views]


@router.get("/drafts", response_model=list[PublicPost])
async def list_my_drafts(
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> list[PublicPost]:
  """The current user's drafts, newest first, with full body.

  The author comes from the session, so this only ever returns your own
  drafts — it powers the owner-only "Drafts" view on the creator page.
  """
  drafts = await post_service.list_draft_posts_by_user(db, user.id)
  views = [await post_service.view_post(db, draft, user) for draft in drafts]
  return [_to_public(post, decision, tier) for post, decision, tier in views]


@router.post("", response_model=PublicPost, status_code=status.HTTP_201_CREATED)
async def create_post(
  new_post: NewPost,
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> PublicPost:
  """Create a post authored by the signed-in user, as a draft.

  ``required_tier_id`` (when set) must be one of the author's own tiers (400
  otherwise). Publish later via PATCH by setting ``published_at``.
  """
  if new_post.required_tier_id is not None:
    await _require_own_tier(db, user, new_post.required_tier_id)
  post = await post_service.create_post(db, user.id, new_post)
  return _to_public(*await post_service.view_post(db, post, user))


@router.get("/{post_id}", response_model=PublicPost)
async def get_post(
  post: Annotated[Post, Depends(get_viewable_post)],
  viewer: Annotated[User | None, Depends(get_current_user_or_none)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> PublicPost:
  """A single post with the entitlement applied for the current viewer.

  Teaser always; body only when allowed — plus the access decision and the
  tier needed to unlock. Drafts 404 for everyone but their author.
  """
  return _to_public(*await post_service.view_post(db, post, viewer))


@router.get("/{post_id}/access", response_model=PostAccess)
async def get_post_access(
  post: Annotated[Post, Depends(get_viewable_post)],
  viewer: Annotated[User | None, Depends(get_current_user_or_none)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> PostAccess:
  """The core question, answered directly: can this viewer see this post?

  Returns the decision (``allowed`` + machine-readable ``reason``) and the
  tier that would unlock the post — without any post content.
  """
  _, decision, required_tier = await post_service.view_post(db, post, viewer)
  return PostAccess(
    allowed=decision.allowed,
    reason=decision.reason,
    required_tier=PublicTier.model_validate(required_tier)
    if required_tier
    else None,
  )


@router.patch("/{post_id}", response_model=PublicPost)
async def update_post(
  update: UpdatePost,
  post: Annotated[Post, Depends(get_owned_post)],
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> PublicPost:
  """Edit a post; publish or unpublish it. Author only.

  Setting ``published_at`` publishes a draft; nulling it reverts to draft.
  A new ``required_tier_id`` must be one of the author's own tiers (400).
  """
  if update.required_tier_id is not None:
    await _require_own_tier(db, user, update.required_tier_id)
  updated = await post_service.update_post(db, post, update)
  return _to_public(*await post_service.view_post(db, updated, user))


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
  post: Annotated[Post, Depends(get_owned_post)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
  """Delete a post. Author only."""
  await post_service.delete_post(db, post)
  return Response(status_code=status.HTTP_204_NO_CONTENT)
