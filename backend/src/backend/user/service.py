"""User service — orchestrates the repository and applies transforms.

This layer holds the business logic (which repository calls to make, in what
order) and any value transforms; the repository stays pure database access.
"""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.user import repository
from backend.user.models import User


def _default_name(email: str) -> str:
  """Fallback display name derived from the email local part."""
  return email.split("@")[0]


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
  user = await repository.get_by_google_sub(session, google_sub)
  if user is None:
    user = await repository.create(
      session,
      google_sub=google_sub,
      email=email,
      name=name or _default_name(email),
      avatar_url=avatar_url,
    )
  await repository.update_last_login(session, user, datetime.now(UTC))
  return user
