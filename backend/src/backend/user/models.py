"""User ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from backend.db import Base


class User(Base):
  """A person: creator and/or fan (see overview.md / db-schema.html)."""

  __tablename__ = "users"

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), primary_key=True, default=uuid7
  )
  google_sub: Mapped[str | None] = mapped_column(String(255), unique=True)
  google_email: Mapped[str] = mapped_column(String(254), unique=True)
  handle: Mapped[str | None] = mapped_column(String(255), unique=True)  # chosen later
  google_name: Mapped[str] = mapped_column(String(255))
  bio: Mapped[str | None] = mapped_column(Text)
  google_avatar_url: Mapped[str | None] = mapped_column(Text)
  last_logged_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
