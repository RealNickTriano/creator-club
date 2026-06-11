"""Tests for the post routes.

Auth gating and request validation go through the ``TestClient`` without a
database, like the tier router tests. The router's own behavior — the
``get_owned_post`` / ``get_viewable_post`` guards, the own-tier check, and the
entitlement-applied response shape — needs real rows, so those cases call the
route functions directly against the isolated Postgres ``db_session``.
"""

import uuid
from datetime import UTC, datetime

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.post import router as post_router
from backend.post import service as post_service
from backend.post.schemas import NewPost, UpdatePost
from backend.tier import repository as tier_repository
from backend.tier.models import Tier
from backend.tier.schemas import NewTier
from backend.user import repository as user_repository
from backend.user.models import User
from backend.user.schemas import NewUser


async def _create_user(db_session: AsyncSession) -> User:
  """A persisted user with a handle, unique per call to avoid UNIQUE clashes."""
  token = uuid.uuid4().hex
  user = await user_repository.create_user(
    db_session,
    NewUser(google_sub=f"sub-{token}", google_email=f"{token}@example.com"),
  )
  user.handle = f"handle-{token[:12]}"
  return await user_repository.update_user(db_session, user)


async def _create_tier(db_session: AsyncSession, owner: User) -> Tier:
  """A persisted paid tier owned by ``owner``."""
  return await tier_repository.create_tier(
    db_session,
    owner.id,
    NewTier(
      name=f"tier-{uuid.uuid4().hex[:8]}",
      rank=1,
      price_cents=500,
      description=None,
    ),
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


def test_create_post_requires_auth(client: TestClient) -> None:
  """No session → 401, before any write happens."""
  response = client.post(
    "/posts", json={"title": "Hi", "teaser": "t", "body": "b"}
  )
  assert response.status_code == 401


def test_list_drafts_requires_auth(client: TestClient) -> None:
  response = client.get("/posts/drafts")
  assert response.status_code == 401


def test_update_post_requires_auth(client: TestClient) -> None:
  response = client.patch(f"/posts/{uuid.uuid4()}", json={"title": "Hi"})
  assert response.status_code == 401


def test_delete_post_requires_auth(client: TestClient) -> None:
  response = client.delete(f"/posts/{uuid.uuid4()}")
  assert response.status_code == 401


def test_list_posts_requires_handle_param(client: TestClient) -> None:
  """``handle`` is a required query param — omitting it fails validation."""
  response = client.get("/posts")
  assert response.status_code == 422


async def test_get_owned_post_missing_raises_404(
  db_session: AsyncSession,
) -> None:
  user = await _create_user(db_session)

  with pytest.raises(HTTPException) as exc_info:
    await post_router.get_owned_post(uuid.uuid4(), user, db_session)
  assert exc_info.value.status_code == 404


async def test_get_owned_post_other_author_raises_403(
  db_session: AsyncSession,
) -> None:
  author = await _create_user(db_session)
  intruder = await _create_user(db_session)
  post = await post_service.create_post(db_session, author.id, _new_post())

  with pytest.raises(HTTPException) as exc_info:
    await post_router.get_owned_post(post.id, intruder, db_session)
  assert exc_info.value.status_code == 403


async def test_get_viewable_post_hides_drafts_from_others(
  db_session: AsyncSession,
) -> None:
  """Drafts 404 (not 403) for everyone but the author — existence is hidden."""
  author = await _create_user(db_session)
  other = await _create_user(db_session)
  draft = await post_service.create_post(db_session, author.id, _new_post())

  with pytest.raises(HTTPException) as exc_info:
    await post_router.get_viewable_post(draft.id, other, db_session)
  assert exc_info.value.status_code == 404

  with pytest.raises(HTTPException) as exc_info:
    await post_router.get_viewable_post(draft.id, None, db_session)
  assert exc_info.value.status_code == 404

  found = await post_router.get_viewable_post(draft.id, author, db_session)
  assert found.id == draft.id


async def test_create_post_rejects_foreign_tier(
  db_session: AsyncSession,
) -> None:
  """Gating by someone else's tier (or a nonexistent one) is a 400."""
  author = await _create_user(db_session)
  other = await _create_user(db_session)
  their_tier = await _create_tier(db_session, other)

  with pytest.raises(HTTPException) as exc_info:
    await post_router.create_post(
      _new_post(required_tier_id=their_tier.id), author, db_session
    )
  assert exc_info.value.status_code == 400

  with pytest.raises(HTTPException) as exc_info:
    await post_router.create_post(
      _new_post(required_tier_id=uuid.uuid4()), author, db_session
    )
  assert exc_info.value.status_code == 400


async def test_create_post_returns_creator_view(
  db_session: AsyncSession,
) -> None:
  author = await _create_user(db_session)
  tier = await _create_tier(db_session, author)

  created = await post_router.create_post(
    _new_post(required_tier_id=tier.id), author, db_session
  )

  assert created.published_at is None  # drafts by default
  assert created.body == "The full body."  # the author always sees the body
  assert created.access.allowed is True
  assert created.access.reason == "creator"
  assert created.access.required_tier is not None
  assert created.access.required_tier.id == tier.id


async def test_update_post_rejects_foreign_tier(
  db_session: AsyncSession,
) -> None:
  author = await _create_user(db_session)
  other = await _create_user(db_session)
  their_tier = await _create_tier(db_session, other)
  post = await post_service.create_post(db_session, author.id, _new_post())

  with pytest.raises(HTTPException) as exc_info:
    await post_router.update_post(
      UpdatePost(required_tier_id=their_tier.id), post, author, db_session
    )
  assert exc_info.value.status_code == 400


async def test_feed_locks_body_for_non_members(
  db_session: AsyncSession,
) -> None:
  """The wire shape: locked posts carry teaser + upsell, never the body."""
  author = await _create_user(db_session)
  viewer = await _create_user(db_session)
  tier = await _create_tier(db_session, author)
  post = await post_service.create_post(
    db_session, author.id, _new_post(required_tier_id=tier.id)
  )
  await post_service.update_post(
    db_session, post, UpdatePost(published_at=datetime.now(UTC))
  )

  assert author.handle is not None
  feed = await post_router.list_creator_posts(author.handle, viewer, db_session)

  assert len(feed) == 1
  item = feed[0]
  assert item.body is None
  assert item.teaser == "A teaser."
  assert item.access.allowed is False
  assert item.access.reason == "no_membership"
  assert item.access.required_tier is not None
  assert item.access.required_tier.id == tier.id


async def test_feed_unknown_handle_raises_404(db_session: AsyncSession) -> None:
  with pytest.raises(HTTPException) as exc_info:
    await post_router.list_creator_posts("no-such-handle", None, db_session)
  assert exc_info.value.status_code == 404
