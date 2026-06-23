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


settings = Settings()
