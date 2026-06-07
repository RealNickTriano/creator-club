"""Shared pytest fixtures.

As the app grows, this is where API tests will override dependencies — e.g.
``app.dependency_overrides[get_current_user]`` / ``[get_db]`` — to swap in fake
users and sessions instead of running real OAuth or hitting Postgres.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
    """A TestClient bound to the FastAPI app."""
    return TestClient(app)
