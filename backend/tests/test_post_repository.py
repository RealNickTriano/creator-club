"""Tests for the post repository against the isolated Postgres ``db_session``."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from backend.post import repository
from backend.post.models import Post
from backend.post.schemas import NewPost
from backend.user import repository as user_repository
from backend.user.models import User
from backend.user.schemas import NewUser


async def _create_user(db_session: AsyncSession) -> User:
  """A persisted user to author posts, unique per call to avoid UNIQUE clashes."""
  token = uuid.uuid4().hex
  return await user_repository.create_user(
    db_session,
    NewUser(google_sub=f"sub-{token}", google_email=f"{token}@example.com"),
  )


def _new_post(**overrides: object) -> NewPost:
  """A valid ``NewPost``; override fields per test."""
  data: dict[str, object] = {
    "title": f"Post {uuid.uuid4().hex[:8]}",
    "teaser": "A teaser.",
    "body": "The full body.",
    "required_tier_id": None,
  }
  data.update(overrides)
  return NewPost(**data)  # type: ignore[arg-type]


async def _publish(
  db_session: AsyncSession, post: Post, published_at: datetime
) -> Post:
  """Stamp ``published_at`` on a draft and persist it."""
  post.published_at = published_at
  return await repository.update_post(db_session, post)


async def test_create_post_is_a_draft(db_session: AsyncSession) -> None:
  """New posts start unpublished; created_at comes from the database."""
  author = await _create_user(db_session)

  post = await repository.create_post(db_session, author.id, _new_post())

  assert post.user_id == author.id
  assert post.published_at is None
  assert post.created_at is not None


async def test_get_post_by_id(db_session: AsyncSession) -> None:
  author = await _create_user(db_session)
  post = await repository.create_post(db_session, author.id, _new_post())

  found = await repository.get_post_by_id(db_session, post.id)

  assert found is not None
  assert found.id == post.id
  assert await repository.get_post_by_id(db_session, uuid.uuid4()) is None


async def test_list_published_excludes_drafts_and_other_authors(
  db_session: AsyncSession,
) -> None:
  author = await _create_user(db_session)
  other = await _create_user(db_session)
  published = await repository.create_post(db_session, author.id, _new_post())
  await _publish(db_session, published, datetime.now(UTC))
  await repository.create_post(db_session, author.id, _new_post())  # draft
  theirs = await repository.create_post(db_session, other.id, _new_post())
  await _publish(db_session, theirs, datetime.now(UTC))

  posts = await repository.list_published_posts_by_user(db_session, author.id)

  assert [p.id for p in posts] == [published.id]


async def test_list_published_orders_newest_first(
  db_session: AsyncSession,
) -> None:
  author = await _create_user(db_session)
  now = datetime.now(UTC)
  older = await repository.create_post(db_session, author.id, _new_post())
  await _publish(db_session, older, now - timedelta(days=1))
  newer = await repository.create_post(db_session, author.id, _new_post())
  await _publish(db_session, newer, now)

  posts = await repository.list_published_posts_by_user(db_session, author.id)

  assert [p.id for p in posts] == [newer.id, older.id]


async def test_list_drafts_excludes_published(db_session: AsyncSession) -> None:
  author = await _create_user(db_session)
  draft = await repository.create_post(db_session, author.id, _new_post())
  published = await repository.create_post(db_session, author.id, _new_post())
  await _publish(db_session, published, datetime.now(UTC))

  drafts = await repository.list_draft_posts_by_user(db_session, author.id)

  assert [p.id for p in drafts] == [draft.id]


async def test_update_post_persists_changes(db_session: AsyncSession) -> None:
  author = await _create_user(db_session)
  post = await repository.create_post(db_session, author.id, _new_post())

  post.title = "Renamed"
  updated = await repository.update_post(db_session, post)

  assert updated.title == "Renamed"
  found = await repository.get_post_by_id(db_session, post.id)
  assert found is not None and found.title == "Renamed"


async def test_delete_post_removes_row(db_session: AsyncSession) -> None:
  author = await _create_user(db_session)
  post = await repository.create_post(db_session, author.id, _new_post())

  await repository.delete_post(db_session, post)

  assert await repository.get_post_by_id(db_session, post.id) is None
