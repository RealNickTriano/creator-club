"""API route registry.

Each feature owns its router; list them here and they're attached to the app by
:func:`register_routes`. This keeps ``main.py`` free of per-endpoint wiring.
"""

from fastapi import FastAPI

from backend.auth.router import router as auth_router
from backend.health.router import router as health_router
from backend.membership.router import router as membership_router
from backend.post.router import router as post_router
from backend.tier.router import router as tier_router
from backend.user.router import router as user_router
from backend.webhooks.router import router as webhooks_router

_routers = (
  health_router,
  auth_router,
  user_router,
  tier_router,
  membership_router,
  post_router,
  webhooks_router,
)


def register_routes(app: FastAPI) -> None:
  """Attach all feature routers to the application."""
  for router in _routers:
    app.include_router(router)
