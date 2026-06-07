"""Unit tests for the pure entitlement logic.

These touch no database and no HTTP — just functions over plain values — so they
run in microseconds and read as a decision table.
"""

from datetime import UTC, datetime, timedelta

import pytest

from backend.entitlements import membership_is_active

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
