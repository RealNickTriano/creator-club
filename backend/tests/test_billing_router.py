"""Tests for the billing route (Stripe Customer Portal)."""

import uuid

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend import billing
from backend.billing.router import PortalSession, create_portal_session
from backend.user.models import User


def _user(*, stripe_customer_id: str | None) -> User:
  return User(
    id=uuid.uuid4(),
    google_email="ada@example.com",
    handle=None,
    stripe_customer_id=stripe_customer_id,
  )


def test_portal_requires_auth(client: TestClient) -> None:
  """No session → 401, before any Stripe call."""
  assert client.post("/billing/portal").status_code == 401


async def test_portal_without_customer_returns_400() -> None:
  """A user who's never subscribed has no Customer to manage."""
  with pytest.raises(HTTPException) as exc_info:
    await create_portal_session(_user(stripe_customer_id=None))
  assert exc_info.value.status_code == 400


async def test_portal_returns_url(monkeypatch: pytest.MonkeyPatch) -> None:
  """With a Customer, the route returns the hosted portal URL."""
  captured: dict = {}

  async def _fake_portal(customer_id: str, return_url: str) -> str:
    captured["customer_id"] = customer_id
    captured["return_url"] = return_url
    return "https://billing.stripe.test/session"

  monkeypatch.setattr(billing, "create_billing_portal_session", _fake_portal)

  result = await create_portal_session(_user(stripe_customer_id="cus_123"))

  assert isinstance(result, PortalSession)
  assert result.portal_url == "https://billing.stripe.test/session"
  assert captured["customer_id"] == "cus_123"
  assert captured["return_url"].endswith("/billing")
