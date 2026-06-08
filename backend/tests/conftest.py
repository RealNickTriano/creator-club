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
os.environ.setdefault(
  "DATABASE_URL", "postgresql+asyncpg://app:app@localhost:5432/creatorclub"
)

from collections.abc import AsyncGenerator

import asyncpg
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from backend.db import Base
from backend.main import app

# A dedicated test database derived from the configured one, so repository
# tests build their own schema and never read or mutate real data.
_DB_URL = make_url(os.environ["DATABASE_URL"])
_TEST_DB_NAME = f"{_DB_URL.database or 'creatorclub'}_test"
TEST_DATABASE_URL = _DB_URL.set(database=_TEST_DB_NAME)


@pytest.fixture
def client() -> TestClient:
  """A TestClient bound to the FastAPI app."""
  return TestClient(app)


async def _ensure_test_database() -> None:
  """Create the test database if it doesn't already exist (idempotent).

  ``CREATE DATABASE`` can't run inside a transaction, so this uses a raw
  asyncpg connection to the ``postgres`` maintenance database rather than
  SQLAlchemy.
  """
  admin = await asyncpg.connect(
    host=_DB_URL.host,
    port=_DB_URL.port,
    user=_DB_URL.username,
    password=_DB_URL.password,
    database="postgres",
  )
  try:
    exists = await admin.fetchval(
      "select 1 from pg_database where datname = $1", _TEST_DB_NAME
    )
    if not exists:
      await admin.execute(f'CREATE DATABASE "{_TEST_DB_NAME}"')
  finally:
    await admin.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
  """An async session against an isolated test database.

  Tables are (re)created from the ORM metadata before each test and dropped
  afterwards, so every test starts empty and nothing leaks between tests — or
  into the real ``creatorclub`` database.
  """
  await _ensure_test_database()
  engine = create_async_engine(TEST_DATABASE_URL)
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)
    await conn.run_sync(Base.metadata.create_all)
  try:
    async with AsyncSession(engine, expire_on_commit=False) as session:
      yield session
  finally:
    async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
