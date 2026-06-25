"""Shared pytest fixtures.

Repository tests run against a throwaway PostgreSQL instance started in a Docker
container by ``testcontainers`` (see :func:`postgres_container`). The container
is created once per test session and torn down at the end; each test gets a
freshly-built schema, so the suite is fully self-contained and never touches a
developer's real database.

As the app grows, this is also where API tests will override dependencies — e.g.
``app.dependency_overrides[get_current_user]`` / ``[get_db]`` — to swap in fake
users and sessions instead of running real OAuth.
"""

import os

# Required settings must exist before the app (and its config) is imported.
# Tests don't perform a real OAuth round-trip, so dummy values are fine.
os.environ.setdefault("GOOGLE_OAUTH_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_OAUTH_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault(
  "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"
)
# Unused by the repository tests (they point at the container below), but the
# app's config still requires it to import.
os.environ.setdefault(
  "DATABASE_URL", "postgresql+asyncpg://app:app@localhost:5432/creatorclub"
)

from collections.abc import AsyncGenerator, Iterator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import make_url
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from backend import billing
from backend.db import Base
from backend.main import app


@pytest.fixture
def client() -> TestClient:
  """A TestClient bound to the FastAPI app."""
  return TestClient(app)


@pytest.fixture(autouse=True)
def stub_stripe_billing(monkeypatch: pytest.MonkeyPatch) -> None:
  """Keep the suite hermetic — never call Stripe over the network.

  Tier create/update and paid-tier checkout call Stripe in real code (see
  :mod:`backend.billing`); here we replace every network helper with a no-op or
  a deterministic stub so unit tests neither need a Stripe key nor make HTTP
  calls. A test that wants to assert real billing behavior can re-patch them.
  """

  async def _no_sync(tier: object, creator: object) -> bool:
    return False

  async def _no_archive(price_id: str) -> None:
    return None

  async def _stub_customer(user: object) -> str:
    return "cus_test_stub"

  async def _stub_checkout(member: object, tier: object, creator: object) -> str:
    return "https://checkout.stripe.test/stub-session"

  async def _no_cancel(subscription_id: str) -> None:
    return None

  monkeypatch.setattr(billing, "sync_tier_pricing", _no_sync)
  monkeypatch.setattr(billing, "archive_price", _no_archive)
  monkeypatch.setattr(billing, "create_customer", _stub_customer)
  monkeypatch.setattr(billing, "create_subscription_checkout", _stub_checkout)
  monkeypatch.setattr(billing, "cancel_subscription", _no_cancel)


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
  """Start a disposable PostgreSQL container for the whole test session.

  Pinned to the same image as ``docker-compose.yml`` so tests exercise the same
  Postgres version as local/dev runs.
  """
  with PostgresContainer("postgres:17") as postgres:
    yield postgres


@pytest.fixture(scope="session")
def test_database_url(postgres_container: PostgresContainer) -> URL:
  """The container's connection URL, normalised to the async (asyncpg) driver."""
  return make_url(postgres_container.get_connection_url()).set(
    drivername="postgresql+asyncpg"
  )


@pytest_asyncio.fixture
async def db_session(test_database_url: URL) -> AsyncGenerator[AsyncSession]:
  """An async session against the containerised database.

  The schema is (re)created from the ORM metadata before each test and dropped
  afterwards, so every test starts from empty tables and nothing leaks between
  tests.
  """
  engine = create_async_engine(test_database_url)
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  try:
    async with AsyncSession(engine, expire_on_commit=False) as session:
      yield session
  finally:
    async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
