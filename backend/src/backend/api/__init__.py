"""API route registration.

Each domain module exposes a ``router``; add it to ``_routers`` below and it is
attached to the app by :func:`register_routes`. This keeps ``main.py`` free of
per-endpoint wiring.
"""

from fastapi import FastAPI

from backend.api import service

_routers = (service.router,)


def register_routes(app: FastAPI) -> None:
  """Attach all API routers to the application."""
  for router in _routers:
    app.include_router(router)
