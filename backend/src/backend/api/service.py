"""Service / liveness routes."""

from fastapi import APIRouter

router = APIRouter(tags=["service"])


@router.get("/health")
def health() -> dict[str, str]:
  """Liveness check. Returns ``{"status": "ok"}``."""
  return {"status": "ok"}
