"""Google OAuth sign-in routes (via fastapi-sso)."""

import uuid
from typing import Annotated

from fastapi import (
  APIRouter,
  Depends,
  HTTPException,
  Query,
  Request,
  Response,
  status,
)
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.state import generate_random_state
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db import get_db
from backend.demo import service as demo_service
from backend.user import service as user_service
from backend.user.models import User
from backend.user.schemas import NewUser, PrivateUser

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


async def get_current_user_or_none(
  request: Request,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
  """Resolve the signed-in user from the session, or ``None`` when signed out.

  For routes that any visitor may hit but that adapt to the viewer — e.g. a
  creator's post feed, where entitlements depend on who (if anyone) is asking.
  """
  try:
    return await get_current_user(request, db)
  except HTTPException:
    return None


def _safe_next_path(path: str | None) -> str:
  """Clamp a post-login destination to a same-app path.

  Only plain relative paths ("/c/maya") are honored — absolute URLs and
  protocol-relative forms ("//evil.example", "/\\evil.example") would let the
  callback become an open redirect. Anything suspect falls back to /home.
  """
  if path and path.startswith("/") and not path.startswith(("//", "/\\")):
    return path
  return "/home"


@router.get("/google/login")
async def google_login(
  next_path: Annotated[str, Query(alias="next")] = "/home",
) -> RedirectResponse:
  """Redirect to Google's consent screen, remembering where to land after.

  ``next`` (a same-app path, e.g. ``/c/mayamakes``) rides through the OAuth
  round trip inside the ``state`` parameter, after a random token that
  fastapi-sso checks against its ``sso_state`` cookie on callback — so the
  destination tags along without weakening the CSRF check.
  """
  state = f"{generate_random_state()}:{_safe_next_path(next_path)}"
  async with google_sso:
    return await google_sso.get_login_redirect(state=state)


@router.get("/google/callback")
async def google_callback(
  request: Request,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> RedirectResponse:
  """Handle Google's callback: verify, persist the user, start a session.

  Stores the user id in the signed session cookie and redirects to the
  destination stashed in the OAuth state by :func:`google_login` (validated
  again here), falling back to the frontend's /home.
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
    NewUser(
      google_sub=google_user.id,
      google_email=google_user.email or "",
      google_name=google_user.display_name,
      google_avatar_url=google_user.picture,
    ),
  )

  request.session["user_id"] = str(user.id)
  # The destination rides after the random token in the state param, which
  # fastapi-sso has already matched against its sso_state cookie.
  _, _, next_path = (request.query_params.get("state") or "").partition(":")
  return RedirectResponse(
    url=f"{settings.frontend_url.rstrip('/')}{_safe_next_path(next_path)}"
  )


@router.get("/demo/login")
async def demo_login(
  request: Request,
  db: Annotated[AsyncSession, Depends(get_db)],
  next_path: Annotated[str, Query(alias="next")] = "/home",
) -> RedirectResponse:
  """Start a demo session: mint a fresh, empty account and sign in as it.

  The no-Google counterpart to :func:`google_login` + :func:`google_callback`,
  collapsed into one hop — there's no consent round trip, so we create the
  account, stash its id in the session, and redirect straight into the app at
  the validated ``next`` path (defaulting to /home), exactly like the callback.

  Each call mints its own account, so concurrent demos never share state. The
  session is flagged ``is_demo`` so the app (and later, cleanup) can tell.
  """
  if not settings.demo_enabled:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

  demo = await demo_service.create_demo_user(db)
  await user_service.stamp_login(db, demo)
  request.session["user_id"] = str(demo.id)
  request.session["is_demo"] = True
  return RedirectResponse(
    url=f"{settings.frontend_url.rstrip('/')}{_safe_next_path(next_path)}"
  )


@router.get("/me", response_model=PrivateUser)
async def me(user: Annotated[User, Depends(get_current_user)]) -> User:
  """Return the currently signed-in user, or 401 if there's no session."""
  return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request) -> Response:
  """Clear the session cookie."""
  request.session.clear()
  return Response(status_code=status.HTTP_204_NO_CONTENT)
