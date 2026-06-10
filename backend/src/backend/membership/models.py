"""Membership ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, UniqueConstraint, func
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
