"""Creator Club API — application entry point."""

from fastapi import FastAPI

from backend.api import register_routes

app = FastAPI(title="Creator Club API", version="0.1.0")
register_routes(app)
