"""User repository — database operations only, no business logic."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.user.models import User


async def get_by_google_sub(session: AsyncSession, google_sub: str) -> User | None:
  """Return the user with this Google subject id, or ``None``."""
  return await session.scalar(select(User).where(User.google_sub == google_sub))


async def create(
  session: AsyncSession,
  *,
  google_sub: str,
  email: str,
  name: str,
  avatar_url: str | None,
) -> User:
  """Insert and return a new user with the given fields."""
  user = User(
    google_sub=google_sub, email=email, name=name, avatar_url=avatar_url
  )
  session.add(user)
  await session.commit()
  await session.refresh(user)
  return user


async def update_last_login(
  session: AsyncSession, user: User, when: datetime
) -> None:
  """Persist the user's last sign-in timestamp."""
  user.last_logged_in_at = when
  await session.commit()
