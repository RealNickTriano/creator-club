"""Shared pytest fixtures.

As the app grows, this is where API tests will override dependencies — e.g.
``app.dependency_overrides[get_current_user]`` / ``[get_db]`` — to swap in fake
users and sessions instead of running real OAuth or hitting Postgres.
"""

import os

# Required settings must exist before the app (and its config) is imported.
# Tests don't perform a real OAuth round-trip, so dummy values are fine.
os.environ.setdefault("GOOGLE_OAUTH_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_OAUTH_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault(
  "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"
)

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
  """A TestClient bound to the FastAPI app."""
  return TestClient(app)
