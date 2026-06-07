# Creator Club — Backend

FastAPI service for the tier-based entitlements API. Managed with
[uv](https://docs.astral.sh/uv/); Python 3.14.

## Setup

```bash
uv sync
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
