"""Membership ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import (
  CheckConstraint,
  DateTime,
  ForeignKey,
  String,
  UniqueConstraint,
  func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from backend.db import Base


class Membership(Base):
  """One user's membership to another — fan holds a tier of a creator.

  Status is derived, not stored: active when ``current_period_end`` is NULL
  (open-ended, e.g. a free tier) or still in the future — see
  :mod:`backend.entitlements`. ``canceled_at`` is an audit stamp; it does not
  itself revoke access.
  """

  __tablename__ = "memberships"
  __table_args__ = (
    UniqueConstraint("member_id", "creator_id"),
    CheckConstraint("member_id <> creator_id", name="member_is_not_creator"),
  )

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), primary_key=True, default=uuid7
  )
  member_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), ForeignKey("users.id")
  )
  creator_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), ForeignKey("users.id")
  )
  tier_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), ForeignKey("tiers.id")
  )
  started_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
  current_period_end: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True)
  )
  canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
  # Stripe Subscription id (sub_…) backing a paid membership; NULL for free
  # tiers. ``status`` mirrors Stripe's subscription status (active, past_due,
  # canceled, …) for UI/debugging — current_period_end stays the access
  # boundary the entitlement check reads. See stripe-billing-plan.html.
  stripe_subscription_id: Mapped[str | None] = mapped_column(
    String(255), unique=True
  )
  status: Mapped[str | None] = mapped_column(String(40))
  # The ``created`` time of the most recent Stripe event applied to this row.
  # Stripe gives no delivery-order guarantee, so the webhook handler uses this
  # as a monotonic marker: an event older than what we've already applied is
  # ignored, which keeps a late/redelivered event from truncating or resurrecting
  # access. NULL until the first webhook stamps it. See webhook-reliability-review.html.
  last_event_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
