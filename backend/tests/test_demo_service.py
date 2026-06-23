"""Tests for the demo service.

A fresh demo account must look exactly like a brand-new signup — a synthetic
identity and nothing else — so the visitor lands in the real onboarding flow.
Runs against the isolated Postgres ``db_session``.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.demo import service
from backend.demo.identity import DEMO_NAME, is_demo
from backend.membership import service as membership_service
from backend.post import repository as post_repository
from backend.tier import service as tier_service
from backend.user import repository as user_repository
from backend.user import service as user_service
from backend.user.schemas import NewUser


async def test_create_demo_user_has_synthetic_demo_identity(
  db_session: AsyncSession,
) -> None:
  demo = await service.create_demo_user(db_session)

  assert is_demo(demo)
  assert demo.google_sub is None  # no Google identity
  assert demo.google_name == DEMO_NAME
  assert demo.personal_name == DEMO_NAME  # defaulted from google_name

  # Durably persisted, not just returned.
  refreshed = await user_repository.get_user_by_id(db_session, demo.id)
  assert refreshed is not None
  assert is_demo(refreshed)


async def test_create_demo_user_starts_empty(db_session: AsyncSession) -> None:
  """No handle, tiers, posts, or memberships — like a just-signed-up user."""
  demo = await service.create_demo_user(db_session)

  assert demo.handle is None
  assert demo.display_name is None
  assert demo.bio is None
  assert demo.google_avatar_url is None

  assert await tier_service.list_tiers_by_user(db_session, demo.id) == []
  assert await post_repository.list_published_posts_by_user(
    db_session, demo.id
  ) == []
  assert await post_repository.list_draft_posts_by_user(db_session, demo.id) == []
  assert await membership_service.list_memberships_by_member(
    db_session, demo.id
  ) == []


async def test_create_demo_user_is_unique_per_call(
  db_session: AsyncSession,
) -> None:
  """Each demo login gets its own account, so concurrent visitors don't share."""
  first = await service.create_demo_user(db_session)
  second = await service.create_demo_user(db_session)

  assert first.id != second.id
  assert first.google_email != second.google_email
  assert is_demo(first) and is_demo(second)


async def test_is_demo_is_false_for_a_regular_account(
  db_session: AsyncSession,
) -> None:
  """A normal Google account is never mistaken for a demo."""
  token = uuid.uuid4().hex
  regular = await user_service.create_user(
    db_session,
    NewUser(
      google_sub=f"sub-{token}",
      google_email=f"{token}@example.com",
      google_name="Ada Lovelace",
    ),
  )

  assert not is_demo(regular)
