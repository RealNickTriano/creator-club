"""Unit tests for the pure entitlement logic.

These touch no database and no HTTP — just functions over plain values — so they
run in microseconds and read as a decision table.
"""

from datetime import UTC, datetime, timedelta

import pytest

from backend.entitlements import (
  PostAccessReason,
  decide_post_access,
  membership_is_active,
)

NOW = datetime(2026, 6, 7, tzinfo=UTC)


@pytest.mark.parametrize(
  ("current_period_end", "expected"),
  [
    (None, True),  # open-ended (e.g. free tier) → always active
    (NOW + timedelta(days=1), True),  # period still in the future
    (NOW - timedelta(days=1), False),  # period has elapsed
    (NOW, False),  # exactly at the boundary → not active
  ],
)
def test_membership_is_active(current_period_end: datetime | None, expected: bool) -> None:
  assert membership_is_active(current_period_end, NOW) is expected


@pytest.mark.parametrize(
  ("viewer_is_author", "required_rank", "held_rank", "period_end", "allowed", "reason"),
  [
    # The author always sees their own work, even when the post is gated.
    (True, 2, None, None, True, "creator"),
    (True, None, None, None, True, "creator"),
    # Public posts (no required tier) are open to everyone — member or not.
    (False, None, None, None, True, "public"),
    (False, None, 1, None, True, "public"),
    # Gated posts need a membership at all…
    (False, 0, None, None, False, "no_membership"),
    (False, 2, None, None, False, "no_membership"),
    # …an *active* one (expiry trumps rank — even an over-ranked tier)…
    (False, 1, 2, NOW - timedelta(days=1), False, "membership_expired"),
    # …whose rank meets the bar: exact tier, over-tier, free tier opt-in.
    (False, 1, 1, None, True, "member_ok"),
    (False, 1, 3, NOW + timedelta(days=30), True, "member_ok"),
    (False, 0, 0, None, True, "member_ok"),
    # Under-tier: holding a membership isn't enough if the rank is too low.
    (False, 2, 1, None, False, "tier_too_low"),
    (False, 1, 0, NOW + timedelta(days=30), False, "tier_too_low"),
  ],
)
def test_decide_post_access(
  viewer_is_author: bool,
  required_rank: int | None,
  held_rank: int | None,
  period_end: datetime | None,
  allowed: bool,
  reason: PostAccessReason,
) -> None:
  decision = decide_post_access(
    viewer_is_author=viewer_is_author,
    required_rank=required_rank,
    held_rank=held_rank,
    current_period_end=period_end,
    now=NOW,
  )
  assert decision.allowed is allowed
  assert decision.reason == reason
