"""Pure entitlement logic — no database, no HTTP.

Keeping these decisions as plain functions over plain values is what makes the
bulk of the test suite fast and fixture-free (see ``tests/test_entitlements.py``).
"""

from datetime import UTC, datetime


def membership_is_active(current_period_end: datetime | None, now: datetime) -> bool:
    """Whether a membership grants access at ``now`` (pure — inject the clock).

    Status is *derived, not stored*: a membership is active when its paid period
    is open-ended (``None`` — e.g. a free tier) or has not yet elapsed.
    """
    return current_period_end is None or now < current_period_end


def membership_is_active_now(current_period_end: datetime | None) -> bool:
    """Convenience wrapper around :func:`membership_is_active` using the wall clock.

    Thin impure adapter: it only supplies ``now``, so it carries no logic of its
    own and needs no separate test.
    """
    return membership_is_active(current_period_end, datetime.now(UTC))
