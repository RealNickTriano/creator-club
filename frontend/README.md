# Creator Club — Frontend

The creator page for Creator Club: it renders a creator's tier ladder and post
feed, showing each post as unlocked (full content) or locked (teaser + the call
to action needed to unlock it). All lock/unlock state is driven by the backend's
entitlement decision; the UI only renders what the API has already decided.

## Tech stack

- **Next.js 16** (App Router) with **React 19** and **TypeScript**
- **Tailwind CSS 4** for styling
- A small typed API layer over the native `fetch` API (`lib/api/`), talking to
  the FastAPI backend

## Getting started

Requires Node.js and the backend running locally (see `../backend/README.md`).

```bash
npm install
npm run dev
```

Set the backend URL via an env var (defaults aside, the app reads
`NEXT_PUBLIC_API_BASE_URL`):

```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Then open [http://localhost:3000](http://localhost:3000).

## Scripts

- `npm run dev` — start the dev server
- `npm run build` — production build
- `npm run start` — serve the production build
- `npm run lint` — ESLint
- `npm run format` — Prettier
