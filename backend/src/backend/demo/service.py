"""Demo service — create a fresh, empty demo account.

"Continue as demo" mints a brand-new account that starts exactly like a
first-time signup: no handle, tiers, posts, or memberships. It carries only a
synthetic identity (see :mod:`backend.demo.identity`) so the session has a user
to point at, and the visitor lands in the same onboarding a real new user sees.

Each demo login creates its own account, so concurrent visitors never share
state. Teardown of old demo accounts (delete-on-logout, a TTL sweep) is
deferred — at the expected volume the rows simply accumulate harmlessly.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.demo.identity import DEMO_NAME, new_demo_email
from backend.user import service as user_service
from backend.user.models import User
from backend.user.schemas import NewUser


async def create_demo_user(session: AsyncSession) -> User:
  """Create and return a fresh, empty demo account.

  No Google identity (``google_sub`` stays ``None``) and a unique synthetic
  email. Everything else — handle, tiers, posts, memberships — is left unset.
  """
  return await user_service.create_user(
    session,
    NewUser(google_email=new_demo_email(), google_name=DEMO_NAME),
  )
