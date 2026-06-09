"""Tier ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import (
  DateTime,
  ForeignKey,
  Integer,
  String,
  Text,
  UniqueConstraint,
  func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from backend.db import Base


class Tier(Base):
  """One rung of a creator's membership ladder (see db-schema.html).

  ``rank`` is the value compared during entitlement checks — higher means more
  access. ``price_cents = 0`` marks a free tier (conventionally ``rank 0``),
  which is an ordinary tier in every other way.
  """

  __tablename__ = "tiers"
  __table_args__ = (
    UniqueConstraint("user_id", "name"),
    UniqueConstraint("user_id", "rank"),
  )

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), primary_key=True, default=uuid7
  )
  user_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), ForeignKey("users.id")
  )
  name: Mapped[str] = mapped_column(String(80))
  rank: Mapped[int] = mapped_column(Integer)
  price_cents: Mapped[int] = mapped_column(Integer)
  description: Mapped[str | None] = mapped_column(Text)
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  )
