"""Tests for the post service layer.

The pure decision matrix lives in ``test_entitlements.py``; these cases cover
the *assembly* — that ``view_post`` / ``list_feed`` look up the right
membership and tiers for real rows — against the isolated Postgres
``db_session``.
"""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from backend.membership import repository as membership_repository
from backend.post import service
from backend.post.models import Post
from backend.post.schemas import NewPost, UpdatePost
from backend.tier import repository as tier_repository
from backend.tier.models import Tier
from backend.tier.schemas import NewTier
from backend.user import repository as user_repository
from backend.user.models import User
from backend.user.schemas import NewUser


async def _create_user(db_session: AsyncSession) -> User:
  """A persisted user, unique per call to avoid UNIQUE clashes."""
  token = uuid.uuid4().hex
  return await user_repository.create_user(
    db_session,
    NewUser(google_sub=f"sub-{token}", google_email=f"{token}@example.com"),
  )


async def _create_tier(
  db_session: AsyncSession, owner: User, rank: int = 0, price_cents: int = 0
) -> Tier:
  """A persisted tier owned by ``owner``."""
  return await tier_repository.create_tier(
    db_session,
    owner.id,
    NewTier(
      name=f"tier-{uuid.uuid4().hex[:8]}",
      rank=rank,
      price_cents=price_cents,
      description=None,
    ),
  )


async def _create_post(
  db_session: AsyncSession,
  author: User,
  required_tier_id: uuid.UUID | None = None,
  published: bool = True,
) -> Post:
  """A persisted post by ``author``, published unless stated otherwise."""
  post = await service.create_post(
    db_session,
    author.id,
    NewPost(
      title=f"Post {uuid.uuid4().hex[:8]}",
      teaser="A teaser.",
      body="The full body.",
      required_tier_id=required_tier_id,
    ),
  )
  if published:
    post = await service.update_post(
      db_session, post, UpdatePost(published_at=datetime.now(UTC))
    )
  return post


async def test_view_post_public_for_signed_out_viewer(
  db_session: AsyncSession,
) -> None:
  author = await _create_user(db_session)
  post = await _create_post(db_session, author)

  _, decision, required_tier = await service.view_post(db_session, post, None)

  assert decision.allowed is True
  assert decision.reason == "public"
  assert required_tier is None


async def test_view_post_author_sees_own_gated_post(
  db_session: AsyncSession,
) -> None:
  author = await _create_user(db_session)
  tier = await _create_tier(db_session, author, rank=1, price_cents=500)
  post = await _create_post(db_session, author, required_tier_id=tier.id)

  _, decision, required_tier = await service.view_post(db_session, post, author)

  assert decision.allowed is True
  assert decision.reason == "creator"
  assert required_tier is not None and required_tier.id == tier.id


async def test_view_post_non_member_is_locked_with_unlock_tier(
  db_session: AsyncSession,
) -> None:
  author = await _create_user(db_session)
  viewer = await _create_user(db_session)
  tier = await _create_tier(db_session, author, rank=1, price_cents=500)
  post = await _create_post(db_session, author, required_tier_id=tier.id)

  _, decision, required_tier = await service.view_post(db_session, post, viewer)

  assert decision.allowed is False
  assert decision.reason == "no_membership"
  assert required_tier is not None and required_tier.id == tier.id


async def test_view_post_member_at_required_tier_unlocks(
  db_session: AsyncSession,
) -> None:
  author = await _create_user(db_session)
  viewer = await _create_user(db_session)
  tier = await _create_tier(db_session, author, rank=1, price_cents=500)
  post = await _create_post(db_session, author, required_tier_id=tier.id)
  await membership_repository.create_membership(
    db_session, viewer.id, author.id, tier.id
  )

  _, decision, _ = await service.view_post(db_session, post, viewer)

  assert decision.allowed is True
  assert decision.reason == "member_ok"


async def test_view_post_under_tier_is_locked(db_session: AsyncSession) -> None:
  author = await _create_user(db_session)
  viewer = await _create_user(db_session)
  free = await _create_tier(db_session, author, rank=0)
  paid = await _create_tier(db_session, author, rank=1, price_cents=500)
  post = await _create_post(db_session, author, required_tier_id=paid.id)
  await membership_repository.create_membership(
    db_session, viewer.id, author.id, free.id
  )

  _, decision, required_tier = await service.view_post(db_session, post, viewer)

  assert decision.allowed is False
  assert decision.reason == "tier_too_low"
  assert required_tier is not None and required_tier.id == paid.id


async def test_view_post_expired_membership_is_locked(
  db_session: AsyncSession,
) -> None:
  author = await _create_user(db_session)
  viewer = await _create_user(db_session)
  tier = await _create_tier(db_session, author, rank=1, price_cents=500)
  post = await _create_post(db_session, author, required_tier_id=tier.id)
  membership = await membership_repository.create_membership(
    db_session, viewer.id, author.id, tier.id
  )
  membership.current_period_end = datetime.now(UTC) - timedelta(days=1)
  await membership_repository.update_membership(db_session, membership)

  _, decision, _ = await service.view_post(db_session, post, viewer)

  assert decision.allowed is False
  assert decision.reason == "membership_expired"


async def test_list_feed_excludes_drafts_and_applies_entitlements(
  db_session: AsyncSession,
) -> None:
  """One feed, one viewer: public unlocked, gated locked, draft invisible."""
  author = await _create_user(db_session)
  viewer = await _create_user(db_session)
  tier = await _create_tier(db_session, author, rank=1, price_cents=500)
  public_post = await _create_post(db_session, author)
  gated_post = await _create_post(db_session, author, required_tier_id=tier.id)
  await _create_post(db_session, author, published=False)  # draft

  views = await service.list_feed(db_session, author.id, viewer)

  by_id = {post.id: decision for post, decision, _ in views}
  assert set(by_id) == {public_post.id, gated_post.id}
  assert by_id[public_post.id].reason == "public"
  assert by_id[gated_post.id].reason == "no_membership"


async def test_list_feed_author_sees_everything_published(
  db_session: AsyncSession,
) -> None:
  author = await _create_user(db_session)
  tier = await _create_tier(db_session, author, rank=1, price_cents=500)
  await _create_post(db_session, author, required_tier_id=tier.id)

  views = await service.list_feed(db_session, author.id, author)

  assert len(views) == 1
  _, decision, _ = views[0]
  assert decision.allowed is True
  assert decision.reason == "creator"


async def test_update_post_publish_and_revert_to_draft(
  db_session: AsyncSession,
) -> None:
  """PATCH semantics: explicit null clears published_at, omission keeps it."""
  author = await _create_user(db_session)
  post = await _create_post(db_session, author, published=False)

  published = await service.update_post(
    db_session, post, UpdatePost(published_at=datetime.now(UTC))
  )
  assert published.published_at is not None

  retitled = await service.update_post(
    db_session, published, UpdatePost(title="Renamed")
  )
  assert retitled.published_at is not None  # untouched fields stay put

  reverted = await service.update_post(
    db_session, retitled, UpdatePost(published_at=None)
  )
  assert reverted.published_at is None
