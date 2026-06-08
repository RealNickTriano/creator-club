"""User repository — database operations only, no business logic."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.user.models import User


async def create_user(
  session: AsyncSession,
  *,
  google_sub: str,
  google_email: str,
  google_name: str,
  google_avatar_url: str | None,
) -> User:
  """Insert and return a new user with the given fields."""
  user = User(
    google_sub=google_sub,
    google_email=google_email,
    google_name=google_name,
    google_avatar_url=google_avatar_url,
  )
  session.add(user)
  await session.commit()
  await session.refresh(user)
  return user

async def delete_user(session: AsyncSession, user: User) -> None:
  """Remove ``user`` from the database."""
  await session.delete(user)
  await session.commit()
  
async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
  """Return the user with this id, or ``None``."""
  return await session.get(User, user_id)

async def get_user_by_google_sub(session: AsyncSession, google_sub: str) -> User | None:
  """Return the user with this Google subject id, or ``None``."""
  return await session.scalar(select(User).where(User.google_sub == google_sub))

async def update_user(session: AsyncSession, user: User) -> User:
  """Persist ``user``, replacing the stored row with this object's state."""
  
  merged = await session.merge(user)
  await session.commit()
  await session.refresh(merged)
  return merged


async def update_last_login(
  session: AsyncSession, user: User, when: datetime
) -> None:
  """Persist the user's last sign-in timestamp."""
  user.last_logged_in_at = when
  await session.commit()


