"""Creator Club API — application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api import register_routes
from backend.db import Base, engine
from backend.user import models  # noqa: F401  (register models on Base.metadata)


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Create tables on startup (dev convenience; Alembic comes later)."""
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  yield


app = FastAPI(title="Creator Club API", version="0.1.0", lifespan=lifespan)
register_routes(app)
