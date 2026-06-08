"""Tests for the user repository.

These run against a real (isolated) async Postgres database — see the
``db_session`` fixture in ``conftest.py`` — because the repository is, by
design, nothing but database access; mocking the session would test nothing.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.user import repository
from backend.user.models import User
from backend.user.schemas import NewUser


def _new_user(**overrides: object) -> NewUser:
  """A valid ``NewUser``, unique per call to avoid UNIQUE clashes."""
  token = uuid.uuid4().hex
  data: dict[str, object] = {
    "google_sub": f"sub-{token}",
    "google_email": f"{token}@example.com",
    "google_name": "Ada Lovelace",
    "google_avatar_url": "https://example.com/ada.png",
  }
  data.update(overrides)
  return NewUser(**data)  # type: ignore[arg-type]


async def test_create_user_persists_and_returns(db_session: AsyncSession) -> None:
  new_user = _new_user()
  user = await repository.create_user(db_session, new_user)

  assert isinstance(user.id, uuid.UUID)
  assert user.google_sub == new_user.google_sub
  assert user.google_email == new_user.google_email
  assert user.google_name == new_user.google_name
  assert user.google_avatar_url == new_user.google_avatar_url
  # Server default is populated after the post-insert refresh.
  assert user.created_at is not None
  # Fields not set at creation time.
  assert user.handle is None
  assert user.bio is None
  assert user.last_logged_in_at is None


async def test_create_user_allows_null_avatar(db_session: AsyncSession) -> None:
  user = await repository.create_user(db_session, _new_user(google_avatar_url=None))
  assert user.google_avatar_url is None


async def test_create_user_allows_null_name(db_session: AsyncSession) -> None:
  """A missing Google display name is stored as NULL, not defaulted."""
  user = await repository.create_user(db_session, _new_user(google_name=None))
  assert user.google_name is None


async def test_get_user_by_id_found(db_session: AsyncSession) -> None:
  created = await repository.create_user(db_session, _new_user())
  found = await repository.get_user_by_id(db_session, created.id)
  assert found is not None
  assert found.id == created.id


async def test_get_user_by_id_missing_returns_none(db_session: AsyncSession) -> None:
  assert await repository.get_user_by_id(db_session, uuid.uuid4()) is None


async def test_get_user_by_google_sub_found(db_session: AsyncSession) -> None:
  new_user = _new_user()
  created = await repository.create_user(db_session, new_user)
  found = await repository.get_user_by_google_sub(db_session, new_user.google_sub)
  assert found is not None
  assert found.id == created.id


async def test_get_user_by_google_sub_missing_returns_none(
  db_session: AsyncSession,
) -> None:
  assert await repository.get_user_by_google_sub(db_session, "no-such-sub") is None


async def test_delete_user_removes_row(db_session: AsyncSession) -> None:
  user = await repository.create_user(db_session, _new_user())
  user_id = user.id

  await repository.delete_user(db_session, user)

  assert await repository.get_user_by_id(db_session, user_id) is None


async def test_update_last_login_stamps_timestamp(db_session: AsyncSession) -> None:
  user = await repository.create_user(db_session, _new_user())
  assert user.last_logged_in_at is None

  when = datetime(2026, 6, 7, 12, 0, tzinfo=UTC)
  await repository.update_last_login(db_session, user, when)

  refreshed = await repository.get_user_by_id(db_session, user.id)
  assert refreshed is not None
  assert refreshed.last_logged_in_at == when


async def test_update_user_persists_changes(db_session: AsyncSession) -> None:
  """``update_user`` writes the given User's state back as-is (no field policy
  here — that lives in the service layer)."""
  user = await repository.create_user(db_session, _new_user())

  user.handle = "ada"
  user.bio = "Mathematician"
  updated = await repository.update_user(db_session, user)

  assert updated.handle == "ada"
  assert updated.bio == "Mathematician"

  # The change is durable, not just reflected on the returned object.
  refreshed = await repository.get_user_by_id(db_session, user.id)
  assert refreshed is not None
  assert refreshed.handle == "ada"
  assert refreshed.bio == "Mathematician"


async def test_update_user_replaces_detached_object(db_session: AsyncSession) -> None:
  """A fully-formed (detached) User with an existing id replaces that row."""
  new_user = _new_user()
  created = await repository.create_user(db_session, new_user)
  db_session.expunge(created)  # detach: simulate an object built elsewhere

  replacement = User(
    id=created.id,
    google_sub=new_user.google_sub,
    google_email=new_user.google_email,
    google_name="Augusta Ada King",
    google_avatar_url=None,
    handle="countess",
  )
  updated = await repository.update_user(db_session, replacement)

  assert updated.id == created.id
  assert updated.google_name == "Augusta Ada King"
  assert updated.google_avatar_url is None
  assert updated.handle == "countess"
