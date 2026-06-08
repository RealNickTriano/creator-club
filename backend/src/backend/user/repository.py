"""User repository — database operations only, no business logic."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.user.models import User
from backend.user.schemas import NewUser


async def create_user(session: AsyncSession, new_user: NewUser) -> User:
  """Insert and return a new user from the given creation data.

  Persistence only: ``new_user`` is expected to be fully resolved (e.g. with a
  display name already filled in) — that's the service layer's job.
  """
  user = User(**new_user.model_dump())
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


