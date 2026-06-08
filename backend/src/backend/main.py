"""Creator Club API — application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from backend.api import register_routes
from backend.config import settings
from backend.db import Base, engine
from backend.user import models  # noqa: F401  (register models on Base.metadata)


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Create tables on startup (dev convenience; Alembic comes later)."""
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  yield


app = FastAPI(title="Creator Club API", version="0.1.0", lifespan=lifespan)

# Signed session cookie carries the logged-in user id (see auth/router.py).
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)
# Allow the Vite frontend to call the API with the session cookie.
app.add_middleware(
  CORSMiddleware,
  allow_origins=[settings.frontend_url],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

register_routes(app)
