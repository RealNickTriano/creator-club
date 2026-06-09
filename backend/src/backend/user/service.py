"""User service — orchestrates the repository and applies transforms.

This layer holds the business logic (which repository calls to make, in what
order) and any value transforms; the repository stays pure database access.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.user import repository
from backend.user.models import User
from backend.user.schemas import NewUser, UpdateUser


async def create_user(session: AsyncSession, new_user: NewUser) -> User:
  """Create a user. A missing Google display name is left ``None``."""
  return await repository.create_user(session, new_user)


async def get_user_by_id(
  session: AsyncSession, user_id: uuid.UUID
) -> User | None:
  """Return the user with this id, or ``None``."""
  return await repository.get_user_by_id(session, user_id)


async def get_user_by_google_sub(
  session: AsyncSession, google_sub: str
) -> User | None:
  """Return the user for this Google subject id, or ``None``."""
  return await repository.get_user_by_google_sub(session, google_sub)


async def update_user(
  session: AsyncSession, user: User, update: UpdateUser
) -> User:
  """Apply the provided profile fields to ``user`` and persist them.

  Only fields actually present in ``update`` are written (PATCH semantics), so
  omitting a field leaves the stored value alone. Persistence is delegated to
  :func:`repository.update_user`.
  """
  for field, value in update.model_dump(exclude_unset=True).items():
    setattr(user, field, value)
  return await repository.update_user(session, user)


async def stamp_login(session: AsyncSession, user: User) -> User:
  """Record that the user just signed in (stamps the current UTC time)."""
  await repository.update_last_login(session, user, datetime.now(UTC))
  return user


async def delete_user(session: AsyncSession, user: User) -> None:
  """Delete the user from the database."""
  await repository.delete_user(session, user)


async def get_or_create_from_google(
  session: AsyncSession, new_user: NewUser
) -> User:
  """Resolve the user for a Google login, creating one on first sign-in.

  New users get no handle (chosen later); every login stamps the timestamp.
  """
  user = await get_user_by_google_sub(session, new_user.google_sub)
  if user is None:
    user = await create_user(session, new_user)
  return await stamp_login(session, user)
