"""Post ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from backend.db import Base


class Post(Base):
  """A creator's gated content (see db-schema.html).

  ``required_tier_id`` declares the minimum tier needed to view ``body``:
  ``None`` means public, pointing at a ``price_cents = 0`` tier means "free
  members only". ``teaser`` is always visible. ``published_at = None`` marks a
  draft, hidden from everyone but the author.
  """

  __tablename__ = "posts"

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), primary_key=True, default=uuid7
  )
  user_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), ForeignKey("users.id")
  )
  title: Mapped[str] = mapped_column(String(200))
  teaser: Mapped[str] = mapped_column(Text)
  body: Mapped[str] = mapped_column(Text)
  required_tier_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True), ForeignKey("tiers.id")
  )
  published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
