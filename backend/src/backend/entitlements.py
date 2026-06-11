"""Pure entitlement logic — no database, no HTTP.

Keeping these decisions as plain functions over plain values is what makes the
bulk of the test suite fast and fixture-free (see ``tests/test_entitlements.py``).
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

PostAccessReason = Literal[
  "public",
  "creator",
  "member_ok",
  "no_membership",
  "membership_expired",
  "tier_too_low",
]


@dataclass(frozen=True)
class PostAccessDecision:
  """The answer to "can this viewer see this post's body?".

  ``reason`` is machine-readable so clients can render the right state (and
  the right upsell) without re-deriving the logic.
  """

  allowed: bool
  reason: PostAccessReason


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


def decide_post_access(
  *,
  viewer_is_author: bool,
  required_rank: int | None,
  held_rank: int | None,
  current_period_end: datetime | None,
  now: datetime,
) -> PostAccessDecision:
  """The core entitlement decision, over plain values (pure — inject the clock).

  ``required_rank`` is the rank of the post's required tier (``None`` = public).
  ``held_rank`` is the rank of the tier the viewer's membership to the post's
  author holds (``None`` = no membership; a signed-out viewer is simply a
  viewer with no membership). ``current_period_end`` belongs to that membership
  and only matters when one exists.

  Checks, in order: the author always sees their own work; a public post is
  open to everyone; otherwise the viewer needs an active membership whose tier
  rank meets the post's required rank.
  """
  if viewer_is_author:
    return PostAccessDecision(allowed=True, reason="creator")
  if required_rank is None:
    return PostAccessDecision(allowed=True, reason="public")
  if held_rank is None:
    return PostAccessDecision(allowed=False, reason="no_membership")
  if not membership_is_active(current_period_end, now):
    return PostAccessDecision(allowed=False, reason="membership_expired")
  if held_rank >= required_rank:
    return PostAccessDecision(allowed=True, reason="member_ok")
  return PostAccessDecision(allowed=False, reason="tier_too_low")
