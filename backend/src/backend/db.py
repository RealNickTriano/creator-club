"""Database engine, session factory, and the declarative base.

Async SQLAlchemy (asyncpg). Models inherit from :class:`Base`; routes get a
session via the :func:`get_db` dependency.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
  AsyncSession,
  async_sessionmaker,
  create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings

engine = create_async_engine(settings.database_url, echo=False)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
  """Declarative base for all ORM models."""


async def get_db() -> AsyncGenerator[AsyncSession]:
  """Yield a database session, closing it when the request finishes."""
  async with SessionLocal() as session:
    yield session
