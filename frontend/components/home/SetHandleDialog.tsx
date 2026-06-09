"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError } from "@/lib/api/client";
import { setHandle } from "@/lib/api/users";

/** Handles are 3–30 chars: lowercase letters, numbers and underscores. */
const HANDLE_PATTERN = /^[a-z0-9_]{3,30}$/;

/**
 * Modal that prompts a handle-less user to pick one before setting up their
 * creator page. On success it persists the handle and sends them to their new
 * page at `/c/{handle}`. Opened from {@link CreatorPageSetupCard} when the user
 * has no handle yet.
 */
export default function SetHandleDialog({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  // Focus the field on open and close on Escape.
  useEffect(() => {
    if (!open) return;
    inputRef.current?.focus();
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  const handle = value.trim().replace(/^@+/, "").toLowerCase();
  const preview = handle || "yourname";

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!HANDLE_PATTERN.test(handle)) {
      setError(
        "Handles are 3–30 characters: lowercase letters, numbers and underscores.",
      );
      return;
    }
    setError(null);
    setPending(true);
    try {
      await setHandle(handle);
      router.push(`/c/${handle}`);
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 409
          ? "That handle is already taken. Try another."
          : "Something went wrong. Please try again.",
      );
      setPending(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        onClick={onClose}
        aria-hidden="true"
        className="absolute inset-0 bg-black/40"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="set-handle-title"
        className="border-border bg-background relative w-full max-w-sm rounded-2xl border p-6 shadow-lg"
      >
        <h2
          id="set-handle-title"
          className="text-lg font-semibold tracking-tight"
        >
          Choose your handle
        </h2>
        <p className="text-muted mt-1 text-sm">
          This becomes your page address — people will find you at
          creatorclub.com/c/{preview}.
        </p>

        <form onSubmit={onSubmit} className="mt-4">
          <div className="border-border focus-within:border-foreground/30 flex h-11 items-center gap-1 rounded-full border px-4 transition-colors">
            <span className="text-muted text-sm">@</span>
            <input
              ref={inputRef}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="yourname"
              aria-label="Handle"
              autoCapitalize="none"
              autoCorrect="off"
              spellCheck={false}
              className="placeholder:text-muted text-foreground w-full bg-transparent text-sm outline-none"
            />
          </div>

          {error && (
            <p className="mt-2 text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
          )}

          <div className="mt-5 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="border-border text-foreground hover:bg-foreground/5 inline-flex h-9 cursor-pointer items-center rounded-full border px-4 text-sm font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={pending}
              className="bg-foreground text-background inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-sm font-medium transition-opacity hover:opacity-90 disabled:pointer-events-none disabled:opacity-50"
            >
              {pending ? "Saving…" : "Continue"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
