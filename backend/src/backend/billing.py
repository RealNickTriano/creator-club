"""Stripe billing integration (test mode only — see stripe-billing-plan.html).

Two jobs live here:

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
"""

from backend.config import settings
from backend.stripe_client import get_stripe
from backend.tier.models import Tier
from backend.user.models import User


def _checkout_metadata(member: User, tier: Tier, creator: User) -> dict:
  """Ids the webhook needs to map a completed Checkout back to our rows."""
  return {
    "member_id": str(member.id),
    "creator_id": str(creator.id),
    "tier_id": str(tier.id),
  }


def _product_params(tier: Tier) -> dict:
  """Stripe Product fields mirrored from the tier (description only if set)."""
  params: dict = {"name": tier.name, "metadata": {"tier_id": str(tier.id)}}
  if tier.description:
    params["description"] = tier.description
  return params


def _price_params(tier: Tier) -> dict:
  """A monthly recurring Price, in cents, under the tier's Product."""
  return {
    "product": tier.stripe_product_id,
    "currency": "usd",
    "unit_amount": tier.price_cents,
    "recurring": {"interval": "month"},
    "metadata": {"tier_id": str(tier.id)},
  }


async def sync_tier_pricing(tier: Tier) -> bool:
  """Ensure a paid tier has a Stripe Product + active recurring Price.

  Creates the Product and/or Price when their ids are missing, and keeps the
  Product's display fields in sync otherwise. A missing ``stripe_price_id``
  always means "create a Price at the current ``price_cents``" — to *reprice*,
  the caller nulls ``stripe_price_id`` first and archives the old one (see
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
    product = await client.v1.products.create_async(_product_params(tier))
    tier.stripe_product_id = product.id
    changed = True
  else:
    await client.v1.products.update_async(
      tier.stripe_product_id, _product_params(tier)
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
  metadata = _checkout_metadata(member, tier, creator)
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
