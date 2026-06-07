"""Google OAuth sign-in routes (via fastapi-sso)."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.google import GoogleSSO

from backend.config import settings

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
async def google_callback(request: Request) -> dict[str, str | None]:
  """Handle Google's callback and return the verified user.

  TODO: persist the user (find-or-create by ``google_sub``), set the session
  cookie, and redirect to the frontend — see the auth plan.
  """
  async with google_sso:
    try:
      user = await google_sso.verify_and_process(request)
    except Exception as exc:
      raise HTTPException(
        status_code=400, detail=f"Authentication failed: {exc}"
      ) from exc

  return {
    "id": user.id,
    "email": user.email,
    "display_name": user.display_name,
    "picture": user.picture,
  }
