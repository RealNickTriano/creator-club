@AGENTS.md

# Frontend Architecture

Next.js (App Router) + React + TypeScript + Tailwind CSS v4. The import alias
`@/*` maps to the frontend root (e.g. `@/components/Button`, `@/lib/api/users`).

## Guiding principles

- **Small, single-purpose components.** Each component does one thing and is
  reusable. If a component is doing two jobs, split it. Prefer composing small
  components over adding props/flags to a big one.
- **API calls live in their own files**, never inline in components. This keeps
  data-fetching reusable, testable, and easy to find.
- **Readable over clever.** Code is optimized for the next person to maintain it.

## Directory layout

```
app/                 Routes only (App Router). Pages, layouts, route handlers.
components/          Reusable, presentational UI. One component per file.
  ui/                Generic primitives (Button, Input, Card, Modal).
  <feature>/         Components specific to a feature, when not generic.
lib/
  api/               API call functions, grouped by resource (one file each).
  hooks/             Reusable React hooks.
  utils/             Pure helper functions.
types/               Shared TypeScript types/interfaces.
```

Keep `app/` thin: route files wire data + components together. Real UI lives in
`components/`, real logic lives in `lib/`.

## Components

- One component per file; the filename matches the component name.
- A component renders UI and handles its own interaction — it should not contain
  raw `fetch`/API logic. Pass data in via props, or call a `lib/api` function
  from a hook.
- Keep props minimal and explicit. Lift shared markup into a smaller component
  rather than copy-pasting.
- Default to Server Components; add `"use client"` only when a component needs
  interactivity, state, or browser APIs.

## API calls

- Every call to the backend goes through a function in `lib/api/`, grouped by
  resource: `lib/api/users.ts`, `lib/api/posts.ts`, etc.
- One concern per function (`getUser`, `listPosts`, `createPost`). Components and
  hooks import these — they never build URLs or call `fetch` directly.
- Define request/response types in `types/` (or co-located) and reuse them across
  the API layer and components.
- Centralize shared concerns (base URL, headers, auth, error handling) in one
  place (e.g. `lib/api/client.ts`) so individual call files stay tiny.

## Tooling

- **Formatting:** Prettier (`.prettierrc.json`). Format on save is enabled in
  `.vscode/`; run `npm run format` to format everything.
- **Linting:** ESLint flat config (`eslint.config.mjs`); run `npm run lint`.
- **Pre-commit:** husky + lint-staged auto-run `eslint --fix` + `prettier` on
  staged files, so commits stay clean.
