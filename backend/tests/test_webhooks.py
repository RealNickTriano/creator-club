"""Tests for the Stripe webhook handling.

The provisioning logic runs against the isolated Postgres ``db_session`` with
**canned Stripe event payloads** (no network): we assert the membership row a
given event produces. The route's signature handling goes through the
``TestClient`` with ``billing.construct_event`` stubbed, since the real verify
needs a signing secret.
"""

import time
import uuid
from datetime import UTC, datetime

import pytest
import stripe
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from stripe import StripeObject

from backend import billing
from backend.entitlements import membership_is_active_now
from backend.membership import repository as membership_repository
from backend.tier import repository as tier_repository
from backend.tier.schemas import NewTier
from backend.user import repository as user_repository
from backend.user.models import User
from backend.webhooks import service as webhook_service

ONE_MONTH = 30 * 24 * 3600


def _to_dt(epoch: int) -> datetime:
  """Match how the service stores Stripe timestamps (tz-aware UTC)."""
  return datetime.fromtimestamp(epoch, tz=UTC)


async def _create_user(db_session: AsyncSession) -> User:
  token = uuid.uuid4().hex
  from backend.user.schemas import NewUser

  return await user_repository.create_user(
    db_session,
    NewUser(google_sub=f"sub-{token}", google_email=f"{token}@example.com"),
  )


async def _create_paid_tier(db_session: AsyncSession, owner: User):
  return await tier_repository.create_tier(
    db_session,
    owner.id,
    NewTier(name=f"tier-{uuid.uuid4().hex[:8]}", rank=1, price_cents=500),
  )


def _subscription(
  member: User,
  creator: User,
  tier,
  *,
  sub_id: str = "sub_test123",
  status: str = "active",
  period_end: int | None = None,
  canceled_at: int | None = None,
  ended_at: int | None = None,
  metadata: dict | None = None,
) -> StripeObject:
  """A canned Stripe Subscription object, shaped like the dahlia API."""
  if metadata is None:
    metadata = {
      "member_id": str(member.id),
      "creator_id": str(creator.id),
      "tier_id": str(tier.id),
    }
  return StripeObject.construct_from(
    {
      "id": sub_id,
      "object": "subscription",
      "status": status,
      "canceled_at": canceled_at,
      "ended_at": ended_at,
      "metadata": metadata,
      "items": {
        "object": "list",
        "data": [
          {"id": "si_1", "current_period_end": period_end or int(time.time()) + ONE_MONTH}
        ],
      },
    },
    "sk_test",
  )


def _event(
  event_type: str, obj: StripeObject, created: int | None = None
) -> StripeObject:
  payload: dict = {"id": "evt_test", "type": event_type, "data": {"object": obj}}
  if created is not None:
    payload["created"] = created
  return StripeObject.construct_from(payload, "sk_test")


async def _membership(db_session: AsyncSession, member: User, creator: User):
  return await membership_repository.get_membership_by_member_and_creator(
    db_session, member.id, creator.id
  )


async def test_checkout_completed_provisions_membership(
  db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
  """checkout.session.completed creates the paid membership from the subscription."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_paid_tier(db_session, creator)
  subscription = _subscription(member, creator, tier, status="active")

  async def _fake_get(subscription_id: str) -> StripeObject:
    assert subscription_id == "sub_test123"
    return subscription

  monkeypatch.setattr(billing, "get_subscription", _fake_get)

  session_obj = StripeObject.construct_from(
    {"id": "cs_1", "object": "checkout.session", "subscription": "sub_test123"},
    "sk_test",
  )
  await webhook_service.handle_event(
    db_session, _event("checkout.session.completed", session_obj)
  )

  membership = await _membership(db_session, member, creator)
  assert membership is not None
  assert membership.tier_id == tier.id
  assert membership.stripe_subscription_id == "sub_test123"
  assert membership.status == "active"
  assert membership.current_period_end is not None
  assert membership_is_active_now(membership.current_period_end) is True


async def test_subscription_updated_advances_period_and_is_idempotent(
  db_session: AsyncSession,
) -> None:
  """A renewal pushes current_period_end forward; repeats don't duplicate rows."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_paid_tier(db_session, creator)

  first_end = int(time.time()) + ONE_MONTH
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.updated",
      _subscription(member, creator, tier, period_end=first_end),
    ),
  )
  before = await _membership(db_session, member, creator)
  assert before is not None and before.current_period_end is not None
  # Capture the value now — `before` is the same identity-mapped row the renewal
  # below mutates in place.
  before_id = before.id
  before_end = before.current_period_end

  # Same subscription, a month later (renewal) — delivered twice for good measure.
  renewed_end = first_end + ONE_MONTH
  renewed = _event(
    "customer.subscription.updated",
    _subscription(member, creator, tier, period_end=renewed_end),
  )
  await webhook_service.handle_event(db_session, renewed)
  await webhook_service.handle_event(db_session, renewed)

  after = await _membership(db_session, member, creator)
  assert after is not None
  assert after.id == before_id  # upserted, not duplicated
  assert after.current_period_end > before_end
  # Exactly one membership exists for this pair.
  rows = await membership_repository.list_memberships_by_member(
    db_session, member.id
  )
  assert len(rows) == 1


async def test_subscription_deleted_lapses_access(
  db_session: AsyncSession,
) -> None:
  """A canceled subscription stamps canceled_at and ends access immediately."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_paid_tier(db_session, creator)

  # Start active...
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.updated", _subscription(member, creator, tier)
    ),
  )
  # ...then it's deleted: ended in the past.
  now = int(time.time())
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.deleted",
      _subscription(
        member,
        creator,
        tier,
        status="canceled",
        canceled_at=now - 5,
        ended_at=now - 5,
      ),
    ),
  )

  membership = await _membership(db_session, member, creator)
  assert membership is not None
  assert membership.status == "canceled"
  assert membership.canceled_at is not None
  assert membership_is_active_now(membership.current_period_end) is False


async def test_subscription_without_metadata_is_skipped(
  db_session: AsyncSession,
) -> None:
  """A subscription we can't map (no linking metadata) writes nothing."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_paid_tier(db_session, creator)
  orphan = _subscription(member, creator, tier, metadata={})

  await webhook_service.handle_event(
    db_session, _event("customer.subscription.updated", orphan)
  )

  assert await _membership(db_session, member, creator) is None


async def _create_paid_tier_rank(db_session: AsyncSession, owner: User, rank: int):
  return await tier_repository.create_tier(
    db_session,
    owner.id,
    NewTier(name=f"tier-{uuid.uuid4().hex[:8]}", rank=rank, price_cents=500),
  )


async def test_superseded_subscription_event_is_ignored(
  db_session: AsyncSession,
) -> None:
  """An event from an old sub can't clobber a row active on a different sub.

  This is the guard against duplicate subscriptions left by the historical
  tier-change bug: while one subscription is live, a stray event from another
  must not rewrite the membership.
  """
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  current = await _create_paid_tier_rank(db_session, creator, rank=1)
  other = await _create_paid_tier_rank(db_session, creator, rank=2)

  # Row goes active on the current subscription.
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.updated",
      _subscription(member, creator, current, sub_id="sub_current"),
    ),
  )

  # A late event from a *different* subscription (e.g. a leftover duplicate)
  # pointing at another tier — must be ignored.
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.updated",
      _subscription(member, creator, other, sub_id="sub_old"),
    ),
  )

  membership = await _membership(db_session, member, creator)
  assert membership is not None
  assert membership.stripe_subscription_id == "sub_current"
  assert membership.tier_id == current.id


async def test_new_subscription_takes_over_lapsed_membership(
  db_session: AsyncSession,
) -> None:
  """A genuinely new subscription may claim a row whose old sub has lapsed."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_paid_tier(db_session, creator)

  # Old subscription lapsed: ended in the past, membership inactive.
  now = int(time.time())
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.deleted",
      _subscription(
        member,
        creator,
        tier,
        sub_id="sub_old",
        status="canceled",
        canceled_at=now - 5,
        ended_at=now - 5,
      ),
    ),
  )
  assert (await _membership(db_session, member, creator)) is not None

  # The fan re-subscribes — a new subscription provisions onto the same row.
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.updated",
      _subscription(member, creator, tier, sub_id="sub_new"),
    ),
  )

  membership = await _membership(db_session, member, creator)
  assert membership is not None
  assert membership.stripe_subscription_id == "sub_new"
  assert membership_is_active_now(membership.current_period_end) is True


async def test_out_of_order_event_does_not_truncate_access(
  db_session: AsyncSession,
) -> None:
  """A late, older renewal must not roll current_period_end backwards.

  Stripe gives no delivery-order guarantee. We apply a renewal (period far in
  the future), then deliver an *older* event (earlier `created`, nearer period
  end). The monotonic guard must reject the stale one.
  """
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_paid_tier(db_session, creator)

  base = int(time.time())
  far_end = base + 2 * ONE_MONTH
  near_end = base + ONE_MONTH

  # Newer event (created later) carrying the further period end.
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.updated",
      _subscription(member, creator, tier, period_end=far_end),
      created=base + 100,
    ),
  )
  # Older event (created earlier) arrives afterwards — must be ignored.
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.updated",
      _subscription(member, creator, tier, period_end=near_end),
      created=base + 50,
    ),
  )

  membership = await _membership(db_session, member, creator)
  assert membership is not None
  # The further (newer) period survived; the stale event did not truncate it.
  assert membership.current_period_end == _to_dt(far_end)


async def test_stale_active_event_does_not_resurrect_canceled(
  db_session: AsyncSession,
) -> None:
  """An old `active` update arriving after a cancel must not revive access."""
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_paid_tier(db_session, creator)

  base = int(time.time())

  # Cancellation lands (newer event): subscription ended in the past.
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.deleted",
      _subscription(
        member,
        creator,
        tier,
        status="canceled",
        canceled_at=base - 5,
        ended_at=base - 5,
      ),
      created=base + 100,
    ),
  )
  # A stale `active` update (older `created`) is delivered late — must be ignored.
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.updated",
      _subscription(
        member, creator, tier, status="active", period_end=base + ONE_MONTH
      ),
      created=base + 50,
    ),
  )

  membership = await _membership(db_session, member, creator)
  assert membership is not None
  assert membership.status == "canceled"
  assert membership_is_active_now(membership.current_period_end) is False


async def test_same_second_terminal_event_wins(
  db_session: AsyncSession,
) -> None:
  """When a cancel and an update share a `created` second, the cancel sticks.

  `created` is unix seconds, so two changes can tie. Delivering the non-terminal
  `update` *after* the terminal `delete` (same second) must not reopen access.
  """
  member = await _create_user(db_session)
  creator = await _create_user(db_session)
  tier = await _create_paid_tier(db_session, creator)

  base = int(time.time())

  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.deleted",
      _subscription(
        member,
        creator,
        tier,
        status="canceled",
        canceled_at=base - 5,
        ended_at=base - 5,
      ),
      created=base,
    ),
  )
  await webhook_service.handle_event(
    db_session,
    _event(
      "customer.subscription.updated",
      _subscription(
        member, creator, tier, status="active", period_end=base + ONE_MONTH
      ),
      created=base,  # same second as the cancel
    ),
  )

  membership = await _membership(db_session, member, creator)
  assert membership is not None
  assert membership.status == "canceled"
  assert membership_is_active_now(membership.current_period_end) is False


def test_webhook_rejects_bad_signature(
  client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
  """A failed signature check is a 400, before any handling."""

  def _raise(payload: bytes, sig: str | None):
    raise stripe.SignatureVerificationError("bad sig", sig)

  monkeypatch.setattr(billing, "construct_event", _raise)

  response = client.post(
    "/webhooks/stripe",
    content=b"{}",
    headers={"stripe-signature": "t=1,v1=nope"},
  )
  assert response.status_code == 400


def test_webhook_accepts_verified_event(
  client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
  """A verified (here, ignored-type) event returns 200."""
  event = StripeObject.construct_from(
    {"id": "evt_test", "type": "ping", "data": {"object": {}}}, "sk_test"
  )
  monkeypatch.setattr(billing, "construct_event", lambda payload, sig: event)

  response = client.post(
    "/webhooks/stripe",
    content=b"{}",
    headers={"stripe-signature": "t=1,v1=ok"},
  )
  assert response.status_code == 200
