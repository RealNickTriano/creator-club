"""Tests for the user service layer.

Like the repository tests, the ``update_user`` cases run against the isolated
Postgres ``db_session`` — the field-application logic is only meaningful once
it's actually persisted.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.user import repository, service
from backend.user.schemas import NewUser, UpdateUser


def _new_user(**overrides: object) -> NewUser:
  """A valid ``NewUser``, unique per call to avoid UNIQUE clashes."""
  token = uuid.uuid4().hex
  data: dict[str, object] = {
    "google_sub": f"sub-{token}",
    "google_email": f"{token}@example.com",
    "google_name": "Ada Lovelace",
    "google_avatar_url": None,
  }
  data.update(overrides)
  return NewUser(**data)  # type: ignore[arg-type]


async def test_update_user_applies_and_persists_fields(
  db_session: AsyncSession,
) -> None:
  user = await repository.create_user(db_session, _new_user())

  updated = await service.update_user(
    db_session, user, UpdateUser(handle="ada", bio="Mathematician")
  )

  assert updated.handle == "ada"
  assert updated.bio == "Mathematician"

  # Durable, not just reflected on the returned object.
  refreshed = await repository.get_user_by_id(db_session, user.id)
  assert refreshed is not None
  assert refreshed.handle == "ada"
  assert refreshed.bio == "Mathematician"


async def test_update_user_only_touches_provided_fields(
  db_session: AsyncSession,
) -> None:
  """PATCH semantics: omitted fields keep their stored value."""
  user = await repository.create_user(db_session, _new_user())
  await service.update_user(db_session, user, UpdateUser(bio="first"))

  await service.update_user(db_session, user, UpdateUser(handle="ada"))

  refreshed = await repository.get_user_by_id(db_session, user.id)
  assert refreshed is not None
  assert refreshed.handle == "ada"
  assert refreshed.bio == "first"  # left untouched by the handle-only update


async def test_create_user_defaults_personal_name_to_google_name(
  db_session: AsyncSession,
) -> None:
  """Creator Club addresses new users by their Google name to start."""
  user = await service.create_user(db_session, _new_user())

  assert user.personal_name == "Ada Lovelace"
  assert user.display_name is None  # shown name falls back to google_name


async def test_create_user_keeps_explicit_personal_name(
  db_session: AsyncSession,
) -> None:
  user = await service.create_user(
    db_session, _new_user(personal_name="Augusta Ada King")
  )

  assert user.personal_name == "Augusta Ada King"


async def test_update_user_applies_names(db_session: AsyncSession) -> None:
  user = await service.create_user(db_session, _new_user())

  await service.update_user(
    db_session,
    user,
    UpdateUser(display_name="Ada", personal_name="Augusta Ada King"),
  )

  refreshed = await repository.get_user_by_id(db_session, user.id)
  assert refreshed is not None
  assert refreshed.display_name == "Ada"
  assert refreshed.personal_name == "Augusta Ada King"


async def test_get_user_by_handle_is_case_insensitive(
  db_session: AsyncSession,
) -> None:
  """Handles are stored lowercase, so a mixed-case lookup still resolves."""
  user = await repository.create_user(db_session, _new_user())
  await service.update_user(db_session, user, UpdateUser(handle="ada"))

  found = await service.get_user_by_handle(db_session, "ADA")
  assert found is not None
  assert found.id == user.id
