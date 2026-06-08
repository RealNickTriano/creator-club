"""User service — orchestrates the repository and applies transforms.

This layer holds the business logic (which repository calls to make, in what
order) and any value transforms; the repository stays pure database access.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.user import repository
from backend.user.models import User


def _default_name(email: str) -> str:
  """Fallback display name derived from the email local part."""
  return email.split("@")[0]


async def create_user(
  session: AsyncSession,
  *,
  google_sub: str,
  email: str,
  name: str | None = None,
  avatar_url: str | None = None,
) -> User:
  """Create a user, applying a fallback display name when none is given."""
  return await repository.create(
    session,
    google_sub=google_sub,
    email=email,
    name=name or _default_name(email),
    avatar_url=avatar_url,
  )


async def get_user_by_id(
  session: AsyncSession, user_id: uuid.UUID
) -> User | None:
  """Return the user with this id, or ``None``."""
  return await repository.get_by_id(session, user_id)


async def get_user_by_google_sub(
  session: AsyncSession, google_sub: str
) -> User | None:
  """Return the user for this Google subject id, or ``None``."""
  return await repository.get_by_google_sub(session, google_sub)


async def stamp_login(session: AsyncSession, user: User) -> User:
  """Record that the user just signed in (stamps the current UTC time)."""
  await repository.update_last_login(session, user, datetime.now(UTC))
  return user


async def delete_user(session: AsyncSession, user: User) -> None:
  """Delete the user from the database."""
  await repository.delete(session, user)


async def get_or_create_from_google(
  session: AsyncSession,
  *,
  google_sub: str,
  email: str,
  name: str | None,
  avatar_url: str | None,
) -> User:
  """Resolve the user for a Google login, creating one on first sign-in.

  New users get no handle (chosen later); every login stamps the timestamp.
  """
  user = await get_user_by_google_sub(session, google_sub)
  if user is None:
    user = await create_user(
      session,
      google_sub=google_sub,
      email=email,
      name=name,
      avatar_url=avatar_url,
    )
  return await stamp_login(session, user)
