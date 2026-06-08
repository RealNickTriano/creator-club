"""Google OAuth sign-in routes (via fastapi-sso)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.google import GoogleSSO
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db import get_db
from backend.user import service as user_service
from backend.user.models import User
from backend.user.schemas import PrivateUser

router = APIRouter(prefix="/auth", tags=["auth"])

google_sso = GoogleSSO(
  client_id=settings.google_oauth_client_id,
  client_secret=settings.google_oauth_client_secret,
  redirect_uri=settings.google_redirect_uri,
  allow_insecure_http=True,  # local dev only — require HTTPS in production
)


async def get_current_user(
  request: Request,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
  """Resolve the signed-in user from the session, or raise 401.

  The shared auth dependency for protected routes — override it in tests to
  inject a fake user. A session pointing at a deleted user is treated as
  signed-out and the stale session is cleared.
  """
  user_id = request.session.get("user_id")
  if user_id is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

  user = await user_service.get_user_by_id(db, uuid.UUID(user_id))
  if user is None:
    request.session.clear()
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

  return user


@router.get("/google/login")
async def google_login() -> RedirectResponse:
  """Redirect the user to Google's OAuth consent screen."""
  async with google_sso:
    return await google_sso.get_login_redirect()


@router.get("/google/callback")
async def google_callback(
  request: Request,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> RedirectResponse:
  """Handle Google's callback: verify, persist the user, start a session.

  Stores the user id in the signed session cookie and redirects back to the
  frontend, which then loads the current user from ``/auth/me``.
  """
  async with google_sso:
    try:
      google_user = await google_sso.verify_and_process(request)
    except Exception as exc:
      raise HTTPException(
        status_code=400, detail=f"Authentication failed: {exc}"
      ) from exc

  if google_user is None or google_user.id is None:
    raise HTTPException(status_code=400, detail="Google returned no user")

  user = await user_service.get_or_create_from_google(
    db,
    google_sub=google_user.id,
    email=google_user.email or "",
    name=google_user.display_name,
    avatar_url=google_user.picture,
  )

  request.session["user_id"] = str(user.id)
  return RedirectResponse(url=settings.frontend_url)


@router.get("/me", response_model=PrivateUser)
async def me(user: Annotated[User, Depends(get_current_user)]) -> User:
  """Return the currently signed-in user, or 401 if there's no session."""
  return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request) -> Response:
  """Clear the session cookie."""
  request.session.clear()
  return Response(status_code=status.HTTP_204_NO_CONTENT)
