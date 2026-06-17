# Creator Club

A small, focused service that answers the central question behind any
membership-driven creator platform (think Patreon, Substack, or YouTube
Memberships):

> **Given this fan and this post, can they see it?**

A creator publishes posts. Some are free, some are reserved for paying members
at a particular tier. A user subscribes to another user at a given tier. The job
of this service is to make a single, authoritative entitlement decision — for
any viewer/post pair — and to drive a creator page where content visibly
**locks and unlocks** based on who is logged in.

There is one kind of account: a **user**. Any user can act as a *creator* (by
defining tiers and publishing posts) and as a *fan* (by holding a membership to
another user). "Creator" and "fan" are roles a user plays, not separate records.

<img width="1440" height="1166" alt="creator-club-thumbnail" src="https://github.com/user-attachments/assets/c877b3df-3ae5-4e00-91cc-b0d71267224d" />


## How it works

Membership platforms all reduce to the same access-control shape:

- A **creator** offers a ladder of ranked **tiers** (e.g. Free → Supporter →
  Insider → All-Access), where higher ranks are strictly more privileged.
- A **fan** holds at most one active **membership** to a creator, at one tier —
  and can never be a member of themselves.
- A **post** declares the minimum tier required to view its full content:
  - **public** — `required_tier_id` is NULL; any signed-in user sees it.
  - **members** — requires a tier at that `rank` or above; non-members and
    under-tier viewers get a teaser, not the full body.
- An **entitlement decision** compares the viewer's tier against the post's
  requirement and returns *whether they can view it, and if not, what's missing.*

The decision lives in **one pure function** — `decide_post_access` in
[`backend/src/backend/entitlements.py`](./backend/src/backend/entitlements.py) —
that returns a `PostAccessDecision { allowed, reason }`. The `reason` is
machine-readable (`creator`, `public`, `member_ok`, `no_membership`,
`membership_expired`, `tier_too_low`) so the UI renders the right locked/unlocked
state and call to action. The API calls this function; the frontend never
duplicates it and only renders what the backend has already decided.

## Tech stack

**Backend** — Python 3.14, [FastAPI](https://fastapi.tiangolo.com/) with async
SQLAlchemy 2.0 over PostgreSQL (`asyncpg`), Pydantic schemas behind a thin
repository layer, Google OAuth via `fastapi-sso` with a signed session cookie,
time-sortable UUIDv7 primary keys, and `pytest` for the entitlement matrix.
Managed with [uv](https://docs.astral.sh/uv/).

**Frontend** — [Next.js 16](https://nextjs.org/) (App Router) with React 19,
TypeScript, and Tailwind CSS v4. Renders the creator page — tier ladder and a
feed of posts shown unlocked (full content) or locked (teaser + the right CTA,
"join free" vs. "subscribe"), driven entirely by the API's decision.

```
        ┌────────────────────────────────────────┐
        │            Next.js + React + TS          │
        │   creator page · tier ladder · feed      │
        │   Google sign-in                         │
        └───────────────────┬──────────────────────┘
                            │  HTTP / JSON (session cookie)
                            ▼
        ┌────────────────────────────────────────┐
        │                 FastAPI                  │
        │   routes → entitlement engine → schemas  │
        │                                          │
        │   decide_post_access(viewer, post) →     │
        │      { allowed, reason }                 │
        └───────────────────┬──────────────────────┘
                            ▼
        ┌────────────────────────────────────────┐
        │      Repository layer (SQLAlchemy)       │
        │                  │                       │
        │                  ▼                       │
        │   PostgreSQL (seeded demo data)          │
        │   users · tiers · memberships · posts    │
        └────────────────────────────────────────┘
```

## Project layout

```
backend/    FastAPI service — entitlement engine, REST API, persistence, tests
frontend/   Next.js creator page
overview.md Design doc: full scope, decision matrix, and what's out of scope
```

Each domain lives in its own module under `backend/src/backend/`
(`user`, `tier`, `post`, `membership`, `auth`), each with `router`, `service`,
`repository`, `models`, and `schemas`.

## Getting started

### Backend

```bash
cd backend
uv sync                          # install dependencies
cp .env.example .env             # fill in required settings (fails fast if missing)
docker compose up -d db          # start PostgreSQL
uv run python scripts/seed.py    # populate demo creators, tiers, posts, memberships
uv run backend                   # dev server with autoreload → http://127.0.0.1:8000
```

- Health check: <http://127.0.0.1:8000/health> → `{"status": "ok"}`
- Interactive API docs (Swagger UI): <http://127.0.0.1:8000/docs>

Run the tests with `uv run pytest`. See
[`backend/README.md`](./backend/README.md) for database and test details.

### Frontend

```bash
cd frontend
npm install
npm run dev                      # → http://localhost:3000
```

## API at a glance

| Method | Path                      | Purpose                                            |
| ------ | ------------------------- | -------------------------------------------------- |
| GET    | `/health`                 | Liveness check                                     |
| GET    | `/auth/google/login`      | Begin Google OAuth                                 |
| GET    | `/auth/google/callback`   | OAuth callback; establishes the session            |
| GET    | `/auth/me`                | The current authenticated user                     |
| POST   | `/auth/logout`            | Clear the session                                  |
| PATCH  | `/user`                   | Update the current user's profile                  |
| GET    | `/user/{handle}`          | A user's public creator profile                    |
| GET    | `/tiers`                  | A creator's tier ladder                            |
| POST   | `/tiers`                  | Create a tier                                      |
| PATCH  | `/tiers/{tier_id}`        | Update a tier                                      |
| DELETE | `/tiers/{tier_id}`        | Delete a tier                                      |
| GET    | `/posts`                  | A creator's posts with entitlements applied        |
| GET    | `/posts/drafts`           | The current creator's unpublished drafts           |
| POST   | `/posts`                  | Create a post                                      |
| GET    | `/posts/{post_id}`        | A single post (locked posts return a teaser)       |
| GET    | `/posts/{post_id}/access` | The entitlement decision for the viewer/post pair  |
| PATCH  | `/posts/{post_id}`        | Update a post                                      |
| DELETE | `/posts/{post_id}`        | Delete a post                                      |
| GET    | `/memberships`            | The current user's memberships                     |
| POST   | `/memberships`            | Join a creator at a tier                           |

See the live OpenAPI schema at `/docs` for request/response shapes.
