"""Tests for the membership route.

Auth gating and request validation go through the ``TestClient`` without a
database; the route's validation chain (404/400/402) and the 201-vs-200 upsert
answer call the route function directly against the isolated Postgres
``db_session``, like the tier router tests.
"""

import uuid
from collections.abc import Iterator

import pytest
from fastapi import HTTPException, Response
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend import billing
from backend.auth.router import get_current_user
from backend.main import app
from backend.membership import repository as membership_repository
from backend.membership import router as membership_router
from backend.membership.schemas import (
  CancelMembership,
  CheckoutSession,
  NewMembership,
  PublicMembership,
)
from backend.tier import repository as tier_repository
from backend.tier.models import Tier
from backend.tier.schemas import NewTier
from backend.user import repository as user_repository
from backend.user.models import User
from backend.user.schemas import NewUser


async def _create_user(db_session: AsyncSession) -> User:
  """A persisted user, unique per call to avoid UNIQUE clashes."""
  token = uuid.uuid4().hex
  return await user_repository.create_user(
    db_session,
    NewUser(google_sub=f"sub-{token}", google_email=f"{token}@example.com"),
  )


async def _create_tier(
  db_session: AsyncSession, owner: User, rank: int = 0, price_cents: int = 0
) -> Tier:
  """A persisted tier owned by ``owner`` (free by default)."""
  return await tier_repository.create_tier(
    db_session,
    owner.id,
    NewTier(
      name=f"tier-{uuid.uuid4().hex[:8]}",
      rank=rank,
      price_cents=price_cents,
      description=None,
    ),
  )


async def _post(
  db_session: AsyncSession, user: User, creator_id: uuid.UUID, tier_id: uuid.UUID
) -> tuple[PublicMembership | CheckoutSession, Response]:
  """Call the route function directly, returning (payload, response)."""
  response = Response()
  payload = await membership_router.set_membership(
    NewMembership(creator_id=creator_id, tier_id=tier_id),
    user,
    db_session,
    response,
  )
  return payload, response


def _fake_user() -> User:
  """A minimal authenticated user (no session needed)."""
  return User(id=uuid.uuid4(), google_email="ada@example.com", handle=None)


@pytest.fixture
def authed() -> Iterator[None]:
  """Treat requests as signed in, regardless of session cookie."""
  app.dependency_overrides[get_current_user] = _fake_user
  yield
  app.dependency_overrides.clear()


def test_list_memberships_requires_auth(client: TestClient) -> None:
  """No session → 401, before any read happens."""
  response = client.get("/memberships")
  assert response.status_code == 401


async def test_list_memberships_returns_only_yours(
  db_session: AsyncSession,
) -> None:
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)
  joined, _ = await _post(db_session, member, creator.id, tier.id)
  # Another member's membership must not appear in the listing.
  other = await _create_user(db_session)
  await _post(db_session, other, creator.id, tier.id)

  payload = await membership_router.list_my_memberships(member, db_session)

  assert [m.id for m in payload] == [joined.id]
  assert payload[0].tier.id == tier.id
  assert payload[0].creator.id == creator.id
  assert payload[0].active is True


async def test_list_memberships_empty_for_new_user(
  db_session: AsyncSession,
) -> None:
  member = await _create_user(db_session)

  assert await membership_router.list_my_memberships(member, db_session) == []


def test_set_membership_requires_auth(client: TestClient) -> None:
  """No session → 401, before any write happens."""
  response = client.post(
    "/memberships",
    json={"creator_id": str(uuid.uuid4()), "tier_id": str(uuid.uuid4())},
  )
  assert response.status_code == 401


def test_set_membership_rejects_invalid_body(
  client: TestClient, authed: None
) -> None:
  """A non-UUID id fails validation (422) rather than reaching the db."""
  response = client.post(
    "/memberships", json={"creator_id": "not-a-uuid", "tier_id": "also-not"}
  )
  assert response.status_code == 422


async def test_unknown_creator_returns_404(db_session: AsyncSession) -> None:
  member = await _create_user(db_session)

  with pytest.raises(HTTPException) as exc_info:
    await _post(db_session, member, uuid.uuid4(), uuid.uuid4())
  assert exc_info.value.status_code == 404


async def test_unknown_tier_returns_404(db_session: AsyncSession) -> None:
  member = await _create_user(db_session)
  creator = await _create_user(db_session)

  with pytest.raises(HTTPException) as exc_info:
    await _post(db_session, member, creator.id, uuid.uuid4())
  assert exc_info.value.status_code == 404


async def test_other_creators_tier_returns_400(db_session: AsyncSession) -> None:
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  other = await _create_user(db_session)
  others_tier = await _create_tier(db_session, other)

  with pytest.raises(HTTPException) as exc_info:
    await _post(db_session, member, creator.id, others_tier.id)
  assert exc_info.value.status_code == 400


async def test_subscribing_to_yourself_returns_400(
  db_session: AsyncSession,
) -> None:
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)

  with pytest.raises(HTTPException) as exc_info:
    await _post(db_session, creator, creator.id, tier.id)
  assert exc_info.value.status_code == 400


async def test_paid_tier_returns_checkout_url_without_joining(
  db_session: AsyncSession,
) -> None:
  """A paid tier returns a Stripe Checkout URL and creates no membership yet.

  The membership is provisioned later by the webhook; posting a paid tier here
  only hands back the redirect (billing is stubbed in conftest).
  """
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  paid = await _create_tier(db_session, creator, price_cents=500)

  payload, _ = await _post(db_session, member, creator.id, paid.id)

  assert isinstance(payload, CheckoutSession)
  assert payload.checkout_url
  # Nothing was joined — that's the webhook's job.
  assert await membership_router.list_my_memberships(member, db_session) == []


async def test_join_returns_201_with_tier_and_status(
  db_session: AsyncSession,
) -> None:
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)

  payload, response = await _post(db_session, member, creator.id, tier.id)

  assert response.status_code == 201
  assert payload.member_id == member.id
  assert payload.creator_id == creator.id
  assert payload.tier.id == tier.id
  assert payload.active is True


async def test_cancel_unknown_membership_returns_404(
  db_session: AsyncSession,
) -> None:
  member = await _create_user(db_session)

  with pytest.raises(HTTPException) as exc_info:
    await membership_router.cancel_membership(
      CancelMembership(creator_id=uuid.uuid4()), member, db_session
    )
  assert exc_info.value.status_code == 404


async def test_cancel_stamps_canceled_at(db_session: AsyncSession) -> None:
  """Cancelling a (free) membership records the canceled timestamp."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)
  await _post(db_session, member, creator.id, tier.id)

  result = await membership_router.cancel_membership(
    CancelMembership(creator_id=creator.id), member, db_session
  )

  assert result.canceled_at is not None


async def test_cancel_paid_membership_cancels_stripe_subscription(
  db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
  """A paid membership's Stripe subscription is scheduled to cancel."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator, price_cents=500)
  membership = await membership_repository.create_membership(
    db_session, member.id, creator.id, tier.id
  )
  membership.stripe_subscription_id = "sub_123"
  await membership_repository.update_membership(db_session, membership)

  canceled: dict = {}

  async def _record(subscription_id: str) -> None:
    canceled["id"] = subscription_id

  monkeypatch.setattr(billing, "cancel_subscription", _record)

  result = await membership_router.cancel_membership(
    CancelMembership(creator_id=creator.id), member, db_session
  )

  assert canceled["id"] == "sub_123"
  assert result.canceled_at is not None


async def test_repeat_post_returns_200(db_session: AsyncSession) -> None:
  """The upsert answers 200 (not 409) once a membership exists."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_tier(db_session, creator)
  first, _ = await _post(db_session, member, creator.id, tier.id)

  payload, response = await _post(db_session, member, creator.id, tier.id)

  assert response.status_code == 200
  assert payload.id == first.id
