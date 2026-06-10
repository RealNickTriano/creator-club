"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError } from "@/lib/api/client";
import { useCurrentUser } from "@/lib/hooks/useCurrentUser";
import { updateProfile } from "@/lib/api/users";
import type { PublicUser, UpdateUserProfile } from "@/types/user";

/** Handles are 3–30 chars: lowercase letters, numbers and underscores. */
const HANDLE_PATTERN = /^[a-z0-9_]{3,30}$/;

const FIELD_CLASS =
  "border-border focus:border-foreground/30 placeholder:text-muted " +
  "text-foreground w-full rounded-xl border bg-transparent px-4 py-2.5 " +
  "text-sm outline-none transition-colors";

/**
 * The owner's Profile tab: edit the display name, personal name, handle and
 * bio. Saving refreshes the route so the page picks up the new values — and
 * since the page lives at `/c/{handle}`, a handle change navigates to the new
 * address instead.
 *
 * `personal_name` is owner-only, so it isn't on the server-fetched
 * `PublicUser` — it's loaded from `/me` and the input fills in once that
 * resolves.
 */
export default function CreatorProfileForm({
  creator,
}: {
  creator: PublicUser;
}) {
  const { user: me } = useCurrentUser();
  const [name, setName] = useState(creator.display_name ?? "");
  // null = untouched: the input shows the /me value until the user edits it.
  const [personalNameEdit, setPersonalNameEdit] = useState<string | null>(null);
  const [handle, setHandle] = useState(creator.handle ?? "");
  const [bio, setBio] = useState(creator.bio ?? "");
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [pending, setPending] = useState(false);
  const router = useRouter();

  const personalName = personalNameEdit ?? me?.personal_name ?? "";

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();

    const cleaned = handle.trim().replace(/^@+/, "").toLowerCase();
    // Empty clears the display name, falling back to the Google name.
    const update: UpdateUserProfile = {
      bio: bio.trim() || null,
      display_name: name.trim() || null,
    };
    // Only send personal_name once /me has loaded, so a quick save can't
    // wipe the stored value with the empty placeholder state.
    if (me) {
      update.personal_name = personalName.trim() || null;
    }
    if (cleaned) {
      if (!HANDLE_PATTERN.test(cleaned)) {
        setError(
          "Handles are 3–30 characters: lowercase letters, numbers and underscores.",
        );
        return;
      }
      update.handle = cleaned;
    }

    setError(null);
    setPending(true);
    try {
      await updateProfile(update);
      if (cleaned && cleaned !== creator.handle) {
        router.push(`/c/${cleaned}`);
        return;
      }
      setSaved(true);
      setPending(false);
      router.refresh();
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 409
          ? "That handle is already taken. Try another."
          : "Something went wrong. Please try again.",
      );
      setPending(false);
    }
  }

  function onChange(set: (value: string) => void) {
    return (value: string) => {
      set(value);
      setSaved(false);
    };
  }

  return (
    <form onSubmit={onSubmit} className="max-w-md space-y-3">
      <label className="block">
        <span className="text-foreground mb-1 block text-xs font-medium">
          Display name
        </span>
        <input
          value={name}
          onChange={(e) => onChange(setName)(e.target.value)}
          placeholder={creator.google_name ?? "Your name"}
          className={FIELD_CLASS}
        />
        <span className="text-muted mt-1 block text-xs">
          How you appear to others.
        </span>
      </label>

      <label className="block">
        <span className="text-foreground mb-1 block text-xs font-medium">
          Personal name
        </span>
        <input
          value={personalName}
          onChange={(e) => onChange(setPersonalNameEdit)(e.target.value)}
          placeholder="Your full name"
          className={FIELD_CLASS}
        />
        <span className="text-muted mt-1 block text-xs">
          How Creator Club addresses you — never shown to other users.
        </span>
      </label>

      <label className="block">
        <span className="text-foreground mb-1 block text-xs font-medium">
          Handle
        </span>
        <div className="border-border focus-within:border-foreground/30 flex items-center gap-1 rounded-xl border px-4 transition-colors">
          <span className="text-muted text-sm">@</span>
          <input
            value={handle}
            onChange={(e) => onChange(setHandle)(e.target.value)}
            placeholder="yourname"
            aria-label="Handle"
            autoCapitalize="none"
            autoCorrect="off"
            spellCheck={false}
            className="placeholder:text-muted text-foreground w-full bg-transparent py-2.5 text-sm outline-none"
          />
        </div>
        <span className="text-muted mt-1 block text-xs">
          Your page address: creatorclub.com/c/{handle.trim() || "yourname"}
        </span>
      </label>

      <label className="block">
        <span className="text-foreground mb-1 block text-xs font-medium">
          Bio
        </span>
        <textarea
          value={bio}
          onChange={(e) => onChange(setBio)(e.target.value)}
          placeholder="Tell people what you make"
          rows={4}
          className={`${FIELD_CLASS} resize-none`}
        />
      </label>

      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      <div className="flex items-center justify-end gap-3 pt-2">
        {saved && <span className="text-muted text-sm">Saved</span>}
        <button
          type="submit"
          disabled={pending}
          className="bg-foreground text-background inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-sm font-medium transition-opacity hover:opacity-90 disabled:pointer-events-none disabled:opacity-50"
        >
          {pending ? "Saving…" : "Save changes"}
        </button>
      </div>
    </form>
  );
}
