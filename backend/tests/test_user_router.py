"""Tests for the user profile routes.

These exercise the route wiring that doesn't need a database — auth gating and
request validation. The persisted happy path is covered at the service layer in
``test_user_service.py``; ``get_db`` is resolved here but never connects because
the endpoint body short-circuits before any query runs.
"""

import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from backend.auth.router import get_current_user
from backend.main import app
from backend.user.models import User


def _fake_user() -> User:
  """A minimal authenticated user (no session needed)."""
  return User(id=uuid.uuid4(), google_email="ada@example.com", handle=None)


@pytest.fixture
def authed() -> Iterator[None]:
  """Treat requests as signed in, regardless of session cookie."""
  app.dependency_overrides[get_current_user] = _fake_user
  yield
  app.dependency_overrides.clear()


def test_patch_user_requires_auth(client: TestClient) -> None:
  """No session → 401, before any write happens."""
  response = client.patch("/user", json={"handle": "ada"})
  assert response.status_code == 401


def test_patch_user_rejects_invalid_handle(
  client: TestClient, authed: None
) -> None:
  """A malformed handle fails validation (422) rather than reaching the db."""
  response = client.patch("/user", json={"handle": "No Spaces!"})
  assert response.status_code == 422
