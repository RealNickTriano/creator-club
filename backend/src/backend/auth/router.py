"""Google OAuth sign-in routes (via fastapi-sso)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.google import GoogleSSO
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db import get_db
from backend.user import service as user_service

router = APIRouter(prefix="/auth", tags=["auth"])

google_sso = GoogleSSO(
  client_id=settings.google_oauth_client_id,
  client_secret=settings.google_oauth_client_secret,
  redirect_uri=settings.google_redirect_uri,
  allow_insecure_http=True,  # local dev only — require HTTPS in production
)


@router.get("/google/login")
async def google_login() -> RedirectResponse:
  """Redirect the user to Google's OAuth consent screen."""
  async with google_sso:
    return await google_sso.get_login_redirect()


@router.get("/google/callback")
async def google_callback(
  request: Request,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str | None]:
  """Handle Google's callback: verify, then persist (find-or-create) the user.

  TODO: set the session cookie and redirect to the frontend — see the auth plan.
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

  return {
    "id": str(user.id),
    "handle": user.handle,
    "email": user.email,
    "name": user.name,
  }
