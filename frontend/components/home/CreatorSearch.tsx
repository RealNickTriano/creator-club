"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

/**
 * The "find a creator" box. Submitting a handle routes to that creator's page
 * at `/c/{handle}` — leading `@` and surrounding whitespace are stripped first.
 * Empty input is a no-op. There's no live search yet; it just resolves a handle.
 */
export default function CreatorSearch() {
  const [value, setValue] = useState("");
  const router = useRouter();

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const handle = value.trim().replace(/^@+/, "");
    if (!handle) return;
    router.push(`/c/${handle}`);
  }

  return (
    <form
      onSubmit={handleSubmit}
      role="search"
      className="border-border focus-within:border-foreground/30 bg-background flex h-11 items-center gap-2 rounded-full border px-4 transition-colors"
    >
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
        className="text-muted h-4 w-4 shrink-0"
      >
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-3.5-3.5" />
      </svg>
      <input
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Find a creator by @handle…"
        aria-label="Find a creator by handle"
        className="placeholder:text-muted text-foreground w-full bg-transparent text-sm outline-none"
      />
    </form>
  );
}
