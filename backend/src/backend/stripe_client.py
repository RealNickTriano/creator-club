"""Shared Stripe SDK client.

A single, lazily-built :class:`stripe.StripeClient` for the whole backend, with
the API version pinned (see :mod:`backend.config`) so object shapes stay stable
across Stripe upgrades. Stay in **test mode**: this project never goes live, so
the configured key is always a test key (``sk_test_…`` / ``rk_test_…``).

Calls go through the ``.v1`` namespace, e.g.
``client.v1.checkout.sessions.create_async(...)``. Resource methods have async
variants (``*_async``) — prefer those from FastAPI's async routes so a blocking
HTTP round-trip never stalls the event loop.
"""

import stripe

from backend.config import settings

_client: stripe.StripeClient | None = None


def get_stripe() -> stripe.StripeClient:
  """Return the shared Stripe client, building it on first use.

  Raises ``RuntimeError`` if no key is configured, so a missing
  ``STRIPE_SECRET_KEY`` surfaces as a clear error at the call site rather than a
  confusing Stripe auth failure deeper in.
  """
  global _client
  if _client is None:
    if not settings.stripe_secret_key:
      raise RuntimeError(
        "Stripe is not configured: set STRIPE_SECRET_KEY (a test key) in the "
        "backend environment. See stripe-billing-plan.html."
      )
    _client = stripe.StripeClient(
      settings.stripe_secret_key,
      stripe_version=settings.stripe_api_version,
    )
  return _client
