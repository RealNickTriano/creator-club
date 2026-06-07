# Creator Club — Backend

FastAPI service for the tier-based entitlements API. Managed with
[uv](https://docs.astral.sh/uv/); Python 3.14.

## Setup

```bash
uv sync
```

Copy `.env.example` to `.env` and fill in the values (the app fails to start if
any required setting is missing).

## Database

PostgreSQL runs in Docker. The app creates tables on startup (`create_all`).

```bash
# start postgres in the background
docker compose up -d db

# tail logs / check status
docker compose logs -f db
docker compose ps

# stop it (keep data)
docker compose down

# stop and wipe the data volume (fresh DB next start)
docker compose down -v
```

Connect with psql:

```bash
# via the container (no local psql needed)
docker compose exec db psql -U app -d creatorclub

# or from the host, if you have psql installed
psql postgresql://app:app@localhost:5432/creatorclub
```

## Run

```bash
# dev server with autoreload
uv run backend

# or directly
uv run uvicorn backend.main:app --reload
```

The API listens on http://127.0.0.1:8000.

- Health check: http://127.0.0.1:8000/health → `{"status": "ok"}`
- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs

## Test

```bash
# run the full suite
uv run pytest

# a single file or test
uv run pytest tests/test_health.py
uv run pytest tests/test_health.py::test_health_ok

# verbose, and stop at the first failure
uv run pytest -v -x
```
