"""Service endpoint tests."""

from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
  """GET /health returns 200 with the liveness payload."""
  response = client.get("/health")

  assert response.status_code == 200
  assert response.json() == {"status": "ok"}
