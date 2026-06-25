"""Webhook idempotency ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.db import Base


class ProcessedWebhookEvent(Base):
  """One row per Stripe event we have already handled.

  The webhook handler claims an event's id here *before* applying it, in the
  **same transaction** as the membership write, so each event is processed at
  most once: a redelivery (Stripe retries on any non-200 and can deliver an
  event more than once) finds the id already present and short-circuits. Because
  the claim and the membership write commit together, a crash mid-handling rolls
  back both — the event is simply reprocessed on the next delivery rather than
  marked done but never applied. See webhook-reliability-review.html (finding #2).
  """

  __tablename__ = "processed_webhook_events"

  event_id: Mapped[str] = mapped_column(String(255), primary_key=True)
  processed_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
