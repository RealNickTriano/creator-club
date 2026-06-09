"""Tests for the tier routes.

Auth gating and request validation go through the ``TestClient`` without a
database, like the user router tests. The router's own behavior — the
``get_owned_tier`` guard and the IntegrityError→409 mapping — needs real rows,
so those cases call the route functions directly against the isolated Postgres
``db_session`` (a sync ``TestClient`` can't share the async session's event
loop).
"""

import uuid
from collections.abc import Iterator

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.router import get_current_user
from backend.main import app
from backend.tier import router as tier_router
from backend.tier.schemas import NewTier, UpdateTier
from backend.user import repository as user_repository
from backend.user.models import User
from backend.user.schemas import NewUser


async def _create_user(db_session: AsyncSession) -> User:
  """A persisted user to own tiers, unique per call to avoid UNIQUE clashes."""
  token = uuid.uuid4().hex
  return await user_repository.create_user(
    db_session,
    NewUser(google_sub=f"sub-{token}", google_email=f"{token}@example.com"),
  )


def _new_tier(**overrides: object) -> NewTier:
  """A valid ``NewTier``; override ``name``/``rank`` to control uniqueness."""
  data: dict[str, object] = {
    "name": f"tier-{uuid.uuid4().hex[:8]}",
    "rank": 1,
    "price_cents": 500,
    "description": None,
  }
  data.update(overrides)
  return NewTier(**data)  # type: ignore[arg-type]


def _fake_user() -> User:
  """A minimal authenticated user (no session needed)."""
  return User(id=uuid.uuid4(), google_email="ada@example.com", handle=None)


@pytest.fixture
def authed() -> Iterator[None]:
  """Treat requests as signed in, regardless of session cookie."""
  app.dependency_overrides[get_current_user] = _fake_user
  yield
  app.dependency_overrides.clear()


def test_create_tier_requires_auth(client: TestClient) -> None:
  """No session → 401, before any write happens."""
  response = client.post(
    "/tiers", json={"name": "Gold", "rank": 0, "price_cents": 0}
  )
  assert response.status_code == 401


def test_update_tier_requires_auth(client: TestClient) -> None:
  response = client.patch(f"/tiers/{uuid.uuid4()}", json={"name": "Gold"})
  assert response.status_code == 401


def test_delete_tier_requires_auth(client: TestClient) -> None:
  response = client.delete(f"/tiers/{uuid.uuid4()}")
  assert response.status_code == 401


def test_list_tiers_requires_handle_param(client: TestClient) -> None:
  """``handle`` is a required query param — omitting it fails validation."""
  response = client.get("/tiers")
  assert response.status_code == 422


def test_create_tier_rejects_blank_name(client: TestClient, authed: None) -> None:
  """Invalid bodies fail validation (422) rather than reaching the db."""
  response = client.post("/tiers", json={"name": "", "rank": 0, "price_cents": 0})
  assert response.status_code == 422


def test_create_tier_rejects_negative_price(
  client: TestClient, authed: None
) -> None:
  response = client.post(
    "/tiers", json={"name": "Gold", "rank": 0, "price_cents": -1}
  )
  assert response.status_code == 422


def test_create_tier_rejects_negative_rank(
  client: TestClient, authed: None
) -> None:
  response = client.post(
    "/tiers", json={"name": "Gold", "rank": -1, "price_cents": 0}
  )
  assert response.status_code == 422


async def test_get_owned_tier_missing_raises_404(db_session: AsyncSession) -> None:
  user = await _create_user(db_session)

  with pytest.raises(HTTPException) as exc_info:
    await tier_router.get_owned_tier(uuid.uuid4(), user, db_session)
  assert exc_info.value.status_code == 404


async def test_get_owned_tier_other_owner_raises_403(
  db_session: AsyncSession,
) -> None:
  owner = await _create_user(db_session)
  intruder = await _create_user(db_session)
  tier = await tier_router.create_tier(_new_tier(), owner, db_session)

  with pytest.raises(HTTPException) as exc_info:
    await tier_router.get_owned_tier(tier.id, intruder, db_session)
  assert exc_info.value.status_code == 403


async def test_get_owned_tier_returns_own_tier(db_session: AsyncSession) -> None:
  owner = await _create_user(db_session)
  tier = await tier_router.create_tier(_new_tier(), owner, db_session)

  found = await tier_router.get_owned_tier(tier.id, owner, db_session)
  assert found.id == tier.id


async def test_create_tier_duplicate_name_returns_409(
  db_session: AsyncSession,
) -> None:
  """The (user_id, name) UNIQUE clash surfaces as 409, not a server error."""
  user = await _create_user(db_session)
  await tier_router.create_tier(_new_tier(name="Gold", rank=0), user, db_session)

  with pytest.raises(HTTPException) as exc_info:
    await tier_router.create_tier(_new_tier(name="Gold", rank=1), user, db_session)
  assert exc_info.value.status_code == 409


async def test_update_tier_duplicate_rank_returns_409(
  db_session: AsyncSession,
) -> None:
  """Editing a tier onto another rung's rank surfaces as 409."""
  user = await _create_user(db_session)
  await tier_router.create_tier(_new_tier(rank=0), user, db_session)
  tier = await tier_router.create_tier(_new_tier(rank=1), user, db_session)

  with pytest.raises(HTTPException) as exc_info:
    await tier_router.update_tier(UpdateTier(rank=0), tier, db_session)
  assert exc_info.value.status_code == 409
