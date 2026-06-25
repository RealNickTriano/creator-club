"""Webhook repository — database access for idempotency bookkeeping."""

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.webhooks.models import ProcessedWebhookEvent


async def claim_event(session: AsyncSession, event_id: str) -> bool:
  """Claim a Stripe event id for processing, within the current transaction.

  Inserts the id with ``ON CONFLICT DO NOTHING`` and reports whether the insert
  won: ``True`` when this caller claimed the event (go process it), ``False``
  when it was already processed (a redelivery — skip). Two concurrent deliveries
  of the same event serialise on the primary key, so exactly one claims it.

  Does **not** commit — the claim is committed together with the membership
  write the caller makes, so "processed" and "applied" are atomic.
  """
  stmt = (
    pg_insert(ProcessedWebhookEvent)
    .values(event_id=event_id)
    .on_conflict_do_nothing(index_elements=["event_id"])
    .returning(ProcessedWebhookEvent.event_id)
  )
  result = await session.execute(stmt)
  return result.scalar_one_or_none() is not None
