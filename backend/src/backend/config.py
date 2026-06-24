"""Application configuration, loaded from the environment.

Required fields have no default, so :data:`settings` raises a ``ValidationError``
at import time — i.e. the app fails to start — if any are missing.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  """Settings sourced from environment variables (and an optional ``.env``)."""

  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
  )

  google_oauth_client_id: str
  google_oauth_client_secret: str
  google_redirect_uri: str

  database_url: str

  # Signs the session cookie; the frontend origin the callback redirects back to.
  session_secret: str
  frontend_url: str

  # Gates the "continue as demo" sign-in path (GET /auth/demo/login). Set to
  # false to hide the demo entirely (the route then 404s).
  demo_enabled: bool = True

  # Stripe (test mode only — see stripe-billing-plan.html). Optional so the app
  # still boots before keys are configured; billing code fails loudly if used
  # without them. The "secret" key may be a restricted key (rk_…), which Stripe
  # recommends over a full secret key (sk_…). The publishable key (pk_…) is the
  # only one safe to expose to the browser. The webhook secret (whsec_…) comes
  # from `stripe listen` / the Dashboard and verifies event signatures.
  stripe_secret_key: str | None = None
  stripe_publishable_key: str | None = None
  stripe_webhook_secret: str | None = None
  # Pin the Stripe API version so object shapes (e.g. where
  # current_period_end lives) don't shift under us on a Stripe upgrade.
  stripe_api_version: str = "2026-05-27.dahlia"


settings = Settings()
