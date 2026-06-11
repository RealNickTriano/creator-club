"""Post repository — database operations only, no business logic."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.post.models import Post
from backend.post.schemas import NewPost


async def create_post(
  session: AsyncSession, user_id: uuid.UUID, new_post: NewPost
) -> Post:
  """Insert and return a new (draft) post authored by ``user_id``."""
  post = Post(user_id=user_id, **new_post.model_dump())
  session.add(post)
  await session.commit()
  await session.refresh(post)
  return post


async def get_post_by_id(session: AsyncSession, post_id: uuid.UUID) -> Post | None:
  """Return the post with this id, or ``None``."""
  return await session.get(Post, post_id)


async def list_published_posts_by_user(
  session: AsyncSession, user_id: uuid.UUID
) -> list[Post]:
  """Return this user's published posts, newest first. Drafts are excluded."""
  result = await session.scalars(
    select(Post)
    .where(Post.user_id == user_id, Post.published_at.is_not(None))
    .order_by(Post.published_at.desc())
  )
  return list(result)


async def list_draft_posts_by_user(
  session: AsyncSession, user_id: uuid.UUID
) -> list[Post]:
  """Return this user's drafts (``published_at IS NULL``), newest first."""
  result = await session.scalars(
    select(Post)
    .where(Post.user_id == user_id, Post.published_at.is_(None))
    .order_by(Post.created_at.desc())
  )
  return list(result)


async def update_post(session: AsyncSession, post: Post) -> Post:
  """Persist ``post``, replacing the stored row with this object's state."""
  merged = await session.merge(post)
  await session.commit()
  await session.refresh(merged)
  return merged


async def delete_post(session: AsyncSession, post: Post) -> None:
  """Remove ``post`` from the database."""
  await session.delete(post)
  await session.commit()
