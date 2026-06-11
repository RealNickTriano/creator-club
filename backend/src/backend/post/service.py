"""Post service — orchestrates the repository and applies entitlements.

This layer holds the business logic (which repository calls to make, in what
order) and pairs each post with the viewer's access decision; the repository
stays pure database access and the decision itself lives in
:mod:`backend.entitlements` as a pure function.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.entitlements import PostAccessDecision, decide_post_access
from backend.membership import service as membership_service
from backend.post import repository
from backend.post.models import Post
from backend.post.schemas import NewPost, UpdatePost
from backend.tier import service as tier_service
from backend.tier.models import Tier
from backend.user.models import User

# A post paired with the viewer's decision and the tier that would unlock it.
PostView = tuple[Post, PostAccessDecision, Tier | None]


async def create_post(
  session: AsyncSession, user_id: uuid.UUID, new_post: NewPost
) -> Post:
  """Create a post (as a draft) authored by this user and return it."""
  return await repository.create_post(session, user_id, new_post)


async def get_post_by_id(
  session: AsyncSession, post_id: uuid.UUID
) -> Post | None:
  """Return the post with this id, or ``None``."""
  return await repository.get_post_by_id(session, post_id)


async def list_draft_posts_by_user(
  session: AsyncSession, user_id: uuid.UUID
) -> list[Post]:
  """Return this user's drafts, newest first."""
  return await repository.list_draft_posts_by_user(session, user_id)


async def update_post(
  session: AsyncSession, post: Post, update: UpdatePost
) -> Post:
  """Apply the provided fields to ``post`` and persist them.

  Only fields actually present in ``update`` are written (PATCH semantics), so
  omitting a field leaves the stored value alone — while an explicit ``null``
  clears ``published_at`` (back to draft) or ``required_tier_id`` (public).
  """
  for field, value in update.model_dump(exclude_unset=True).items():
    setattr(post, field, value)
  return await repository.update_post(session, post)


async def delete_post(session: AsyncSession, post: Post) -> None:
  """Delete the post from the database."""
  await repository.delete_post(session, post)


async def _held_membership(
  session: AsyncSession, viewer: User | None, creator_id: uuid.UUID
) -> tuple[int | None, datetime | None]:
  """The rank and period end of the viewer's membership to this creator.

  ``(None, None)`` when signed out, not a member, or the viewer *is* the
  creator (the author path never consults a membership).
  """
  if viewer is None or viewer.id == creator_id:
    return None, None
  membership = await membership_service.get_membership_by_member_and_creator(
    session, viewer.id, creator_id
  )
  if membership is None:
    return None, None
  tier = await tier_service.get_tier_by_id(session, membership.tier_id)
  if tier is None:
    return None, None
  return tier.rank, membership.current_period_end


async def view_post(
  session: AsyncSession, post: Post, viewer: User | None
) -> PostView:
  """Pair one post with this viewer's access decision and unlock tier."""
  required_tier = (
    await tier_service.get_tier_by_id(session, post.required_tier_id)
    if post.required_tier_id is not None
    else None
  )
  held_rank, period_end = await _held_membership(session, viewer, post.user_id)
  decision = decide_post_access(
    viewer_is_author=viewer is not None and viewer.id == post.user_id,
    required_rank=required_tier.rank if required_tier else None,
    held_rank=held_rank,
    current_period_end=period_end,
    now=datetime.now(UTC),
  )
  return post, decision, required_tier


async def list_feed(
  session: AsyncSession, creator_id: uuid.UUID, viewer: User | None
) -> list[PostView]:
  """The creator's published posts, each with this viewer's access decision.

  The membership and tier ladder are loaded once and reused across posts, so
  the feed costs a fixed number of queries regardless of length.
  """
  posts = await repository.list_published_posts_by_user(session, creator_id)
  tiers = await tier_service.list_tiers_by_user(session, creator_id)
  tiers_by_id = {tier.id: tier for tier in tiers}
  held_rank, period_end = await _held_membership(session, viewer, creator_id)
  now = datetime.now(UTC)

  views: list[PostView] = []
  for post in posts:
    required_tier = (
      tiers_by_id.get(post.required_tier_id)
      if post.required_tier_id is not None
      else None
    )
    decision = decide_post_access(
      viewer_is_author=viewer is not None and viewer.id == creator_id,
      required_rank=required_tier.rank if required_tier else None,
      held_rank=held_rank,
      current_period_end=period_end,
      now=now,
    )
    views.append((post, decision, required_tier))
  return views
