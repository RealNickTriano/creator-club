"""Tests for the demo sign-in route.

``demo_login`` mints an account and writes the session, so it needs real rows —
the cases here call the route function directly against the isolated Postgres
``db_session`` with a stand-in request, mirroring the post router tests.
"""

import uuid

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from backend.auth import router as auth_router
from backend.config import settings
from backend.demo.identity import is_demo
from backend.user import repository as user_repository


def _request_with_session() -> Request:
  """A minimal request whose ``.session`` is an inspectable dict."""
  return Request({"type": "http", "session": {}, "headers": []})


async def test_demo_login_creates_demo_and_signs_in(db_session) -> None:
  request = _request_with_session()

  response = await auth_router.demo_login(request, db_session)

  # Session now points at a freshly-minted demo account.
  user_id = request.session["user_id"]
  assert request.session["is_demo"] is True
  demo = await user_repository.get_user_by_id(db_session, uuid.UUID(user_id))
  assert demo is not None
  assert is_demo(demo)
  assert demo.last_logged_in_at is not None  # the login was stamped

  # Redirects into the app at the default landing path.
  assert response.status_code == 307
  assert response.headers["location"] == f"{settings.frontend_url.rstrip('/')}/home"


async def test_demo_login_honors_safe_next(db_session) -> None:
  request = _request_with_session()

  response = await auth_router.demo_login(request, db_session, next_path="/c/maya")

  assert response.headers["location"] == (
    f"{settings.frontend_url.rstrip('/')}/c/maya"
  )


async def test_demo_login_rejects_unsafe_next(db_session) -> None:
  """An open-redirect attempt falls back to /home, like the OAuth callback."""
  request = _request_with_session()

  response = await auth_router.demo_login(
    request, db_session, next_path="//evil.example"
  )

  assert response.headers["location"] == f"{settings.frontend_url.rstrip('/')}/home"


async def test_each_demo_login_is_a_distinct_account(db_session) -> None:
  first = _request_with_session()
  second = _request_with_session()

  await auth_router.demo_login(first, db_session)
  await auth_router.demo_login(second, db_session)

  assert first.session["user_id"] != second.session["user_id"]


async def test_demo_login_404s_when_disabled(
  db_session, monkeypatch: pytest.MonkeyPatch
) -> None:
  monkeypatch.setattr(settings, "demo_enabled", False)
  request = _request_with_session()

  with pytest.raises(HTTPException) as exc_info:
    await auth_router.demo_login(request, db_session)
  assert exc_info.value.status_code == 404
