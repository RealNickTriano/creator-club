"""Stripe billing integration (test mode only — see stripe-billing-plan.html).

The Stripe-facing operations behind the app's billing:

* **Tier pricing** (Phase 1) — keep paid tiers in sync with Stripe **Products**
  and **Prices** so a tier can be sold. A tier maps to one Product (its
  name/description) carrying one active recurring Price (its ``price_cents``).
  Prices are **immutable** in Stripe: changing a tier's price never edits the
  old Price, it creates a new one and archives the old (existing subscriptions
  keep the price they signed up on — exactly the behavior we want).

* **Checkout** (Phase 2) — a fan subscribing to a paid tier is sent to a
  Stripe-hosted Checkout page (:func:`create_subscription_checkout`), each fan
  backed by one Stripe **Customer** (:func:`create_customer`). The membership
  itself is provisioned later, from the resulting webhook (Phase 3).

* **Self-service** (:func:`create_billing_portal_session`) — a fan manages
  their own subscriptions through the hosted Stripe Customer Portal.
"""

import stripe

from backend.config import settings
from backend.stripe_client import get_stripe
from backend.tier.models import Tier
from backend.user.models import User


def _subscription_metadata(member: User, tier: Tier, creator: User) -> dict:
  """Ids the webhook needs to map a Subscription back to our rows.

  Set on both the Checkout-created Subscription and on an in-place tier change,
  so :mod:`backend.webhooks` always provisions the membership onto the right
  tier. ``tier_id`` is the one that moves when a fan changes tiers.
  """
  return {
    "member_id": str(member.id),
    "creator_id": str(creator.id),
    "tier_id": str(tier.id),
  }


def _creator_label(creator: User) -> str:
  """How the creator is named in customer-facing Stripe text.

  Mirrors the "name shown to other users" fallback (display → personal → Google
  name), then the ``@handle``, and only "Creator" as a last resort — so a
  receipt or Checkout line never reads as a bare, anonymous tier.
  """
  name = creator.display_name or creator.personal_name or creator.google_name
  if name:
    return name
  if creator.handle:
    return f"@{creator.handle}"
  return "Creator"


def _product_params(tier: Tier, creator: User) -> dict:
  """Stripe Product fields for a tier — named for *who* and *what* it is.

  The Product name is what the buyer sees on Checkout, on their receipt/invoice
  and in the customer portal (and what we see in the Dashboard), so it carries
  the creator and the word "membership" rather than a bare ``tier.name`` that
  collides across every creator's "Gold". The description falls back to a
  generated line when the tier sets none, since it surfaces in those places too.
  """
  label = _creator_label(creator)
  description = tier.description or (
    f"Monthly {tier.name} membership for {label} on Creator Club."
  )
  return {
    "name": f"{label} – {tier.name} membership",
    "description": description,
    "metadata": {"tier_id": str(tier.id), "creator_id": str(creator.id)},
  }


def _price_params(tier: Tier) -> dict:
  """A monthly recurring Price, in cents, under the tier's Product."""
  return {
    "product": tier.stripe_product_id,
    "currency": "usd",
    "unit_amount": tier.price_cents,
    "recurring": {"interval": "month"},
    "metadata": {"tier_id": str(tier.id)},
  }


async def sync_tier_pricing(tier: Tier, creator: User) -> bool:
  """Ensure a paid tier has a Stripe Product + active recurring Price.

  Creates the Product and/or Price when their ids are missing, and keeps the
  Product's display fields in sync otherwise. ``creator`` names the Product
  (see :func:`_product_params`). A missing ``stripe_price_id`` always means
  "create a Price at the current ``price_cents``" — to *reprice*, the caller
  nulls ``stripe_price_id`` first and archives the old one (see
  :func:`archive_price`), since Prices are immutable.

  Free tiers (``price_cents == 0``) carry no Stripe objects, so this is a no-op.
  Mutates ``tier``'s ``stripe_*`` ids in place and returns True if any changed,
  so the caller knows to persist.
  """
  if tier.price_cents <= 0:
    return False

  client = get_stripe()
  changed = False

  if tier.stripe_product_id is None:
    product = await client.v1.products.create_async(
      _product_params(tier, creator)
    )
    tier.stripe_product_id = product.id
    changed = True
  else:
    await client.v1.products.update_async(
      tier.stripe_product_id, _product_params(tier, creator)
    )

  if tier.stripe_price_id is None:
    price = await client.v1.prices.create_async(_price_params(tier))
    tier.stripe_price_id = price.id
    changed = True

  return changed


async def archive_price(price_id: str) -> None:
  """Deactivate a Price so it's no longer offered.

  Prices can't be deleted; archiving (``active=False``) hides it from new
  checkouts while leaving any existing subscriptions on it untouched.
  """
  client = get_stripe()
  await client.v1.prices.update_async(price_id, {"active": False})


async def create_customer(user: User) -> str:
  """Create a Stripe Customer for ``user`` and return its id (``cus_…``).

  One Customer per fan; the caller stores the id on the user (see
  :func:`backend.user.service.attach_stripe_customer`) so we reuse it on every
  later checkout instead of creating duplicates.
  """
  client = get_stripe()
  params: dict = {
    "email": user.google_email,
    "metadata": {"user_id": str(user.id)},
  }
  name = user.display_name or user.personal_name or user.google_name
  if name:
    params["name"] = name
  customer = await client.v1.customers.create_async(params)
  return customer.id


async def create_subscription_checkout(
  member: User, tier: Tier, creator: User
) -> str:
  """Create a subscription Checkout Session and return its hosted URL.

  The fan (``member``) must already have a Stripe Customer and the ``tier`` a
  synced Price. We deliberately omit ``payment_method_types`` so Stripe shows
  the payment methods enabled in the Dashboard. Linking ids ride along as
  metadata on both the session and the resulting Subscription so the webhook
  (Phase 3) can provision the membership; the membership is **not** created
  here.
  """
  if not tier.stripe_price_id:
    raise RuntimeError(
      f"Tier {tier.id} has no Stripe price; run the tier price sync first."
    )

  client = get_stripe()
  metadata = _subscription_metadata(member, tier, creator)
  base = settings.frontend_url.rstrip("/")
  creator_page = f"{base}/c/{creator.handle}"

  session = await client.v1.checkout.sessions.create_async(
    {
      "mode": "subscription",
      "customer": member.stripe_customer_id,
      "line_items": [{"price": tier.stripe_price_id, "quantity": 1}],
      "success_url": f"{creator_page}?sub=success&session_id={{CHECKOUT_SESSION_ID}}",
      "cancel_url": f"{creator_page}?sub=cancel",
      "metadata": metadata,
      # Copy the ids onto the Subscription too, so later events
      # (invoice.paid, subscription.updated) can also be mapped to our rows.
      "subscription_data": {"metadata": metadata},
    }
  )
  return session.url


async def change_subscription_tier(
  subscription_id: str, member: User, tier: Tier, creator: User
) -> None:
  """Swap a live subscription onto a different (paid) tier's Price, in place.

  Replaces the subscription's single item Price — Stripe prorates the change
  onto the next invoice (``create_prorations``) — refreshes the linking
  metadata so the resulting ``customer.subscription.updated`` webhook provisions
  the *new* tier, and clears any pending period-end cancellation, since
  re-tiering reactivates the subscription. No new Subscription is created, so the
  fan is never double-billed.
  """
  if not tier.stripe_price_id:
    raise RuntimeError(
      f"Tier {tier.id} has no Stripe price; run the tier price sync first."
    )

  client = get_stripe()
  subscription = await client.v1.subscriptions.retrieve_async(subscription_id)
  item_id = subscription["items"]["data"][0]["id"]
  await client.v1.subscriptions.update_async(
    subscription_id,
    {
      "items": [{"id": item_id, "price": tier.stripe_price_id}],
      "proration_behavior": "create_prorations",
      "cancel_at_period_end": False,
      "metadata": _subscription_metadata(member, tier, creator),
    },
  )


async def create_billing_portal_session(
  customer_id: str, return_url: str
) -> str:
  """Create a Stripe Customer Portal session and return its hosted URL.

  The portal is Stripe-hosted self-service: the fan can cancel, switch payment
  method, or view invoices, then return to ``return_url``. Requires the portal
  to be enabled once in the Dashboard (test mode: Settings → Billing → Customer
  portal); any resulting subscription changes flow back via the same webhooks.
  """
  client = get_stripe()
  session = await client.v1.billing_portal.sessions.create_async(
    {"customer": customer_id, "return_url": return_url}
  )
  return session.url


def construct_event(payload: bytes, sig_header: str | None) -> stripe.Event:
  """Verify a webhook payload's signature and return the parsed Event.

  The signature *is* the authentication for the webhook endpoint, so this must
  run on the raw request bytes. Raises ``ValueError`` (malformed payload) or
  ``stripe.SignatureVerificationError`` (bad/forged signature) — the caller
  turns either into a 400.
  """
  if not settings.stripe_webhook_secret:
    raise RuntimeError(
      "Stripe webhooks are not configured: set STRIPE_WEBHOOK_SECRET "
      "(from `stripe listen` or the Dashboard)."
    )
  return stripe.Webhook.construct_event(
    payload, sig_header, settings.stripe_webhook_secret
  )


async def get_subscription(subscription_id: str) -> stripe.Subscription:
  """Retrieve a Subscription — its items carry ``current_period_end``."""
  client = get_stripe()
  return await client.v1.subscriptions.retrieve_async(subscription_id)


async def cancel_subscription(subscription_id: str) -> None:
  """Schedule a subscription to end at the close of the current period.

  Access continues until then (the fan keeps what they paid for); when the
  period lapses Stripe ends the subscription and the resulting webhooks lapse
  the membership. Cancelling at period end — rather than immediately — is the
  friendly default for memberships.
  """
  client = get_stripe()
  await client.v1.subscriptions.update_async(
    subscription_id, {"cancel_at_period_end": True}
  )
