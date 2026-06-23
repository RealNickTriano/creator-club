"use client";

import { useEffect, useRef, useState } from "react";
import { createPost, updatePost } from "@/lib/api/posts";
import type { Post } from "@/types/post";
import type { Tier } from "@/types/tier";

const FIELD_CLASS =
  "border-border focus:border-foreground/30 placeholder:text-muted " +
  "text-foreground w-full rounded-xl border bg-transparent px-4 py-2.5 " +
  "text-sm outline-none transition-colors";

/**
 * The post composer, shown in a modal from the owner's page. Title, teaser
 * (the part everyone sees), body, and which tier unlocks it. Creates a post,
 * or edits the one passed via `post` (fields are prefilled; state initializes
 * on mount, so remount — e.g. with a `key` — to switch posts). On success the
 * saved post is handed to `onSaved`.
 *
 * Drafts (and new posts) offer "Save draft" or "Publish"; an already
 * published post just gets "Save changes" — unpublishing lives on the card.
 * If a save fails after the draft was created (e.g. publishing didn't go
 * through), retrying updates that draft instead of creating a duplicate.
 */
export default function PostForm({
  post,
  tiers,
  onSaved,
  onCancel,
}: {
  /** The post to edit; omit to compose a new one. */
  post?: Post;
  /** The owner's ladder, lowest rank first — the access choices. */
  tiers: Tier[];
  onSaved: (post: Post) => void;
  onCancel: () => void;
}) {
  const [title, setTitle] = useState(post?.title ?? "");
  const [teaser, setTeaser] = useState(post?.teaser ?? "");
  const [body, setBody] = useState(post?.body ?? "");
  // The unlocking tier's id; "" is the public option (no tier required).
  const [requiredTierId, setRequiredTierId] = useState(
    post?.required_tier_id ?? "",
  );
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState<"save" | "publish" | null>(null);
  // The post being edited, set once a new post's draft exists on the backend
  // so retries update it in place.
  const created = useRef<Post | null>(post ?? null);
  const titleRef = useRef<HTMLInputElement>(null);

  const isPublished = post?.published_at != null;

  // The form mounts when the modal opens, so focus the first field once.
  useEffect(() => {
    titleRef.current?.focus();
  }, []);

  async function save(publish: boolean) {
    const trimmedTitle = title.trim();
    if (!trimmedTitle || trimmedTitle.length > 200) {
      setError("Give the post a title (up to 200 characters).");
      return;
    }
    if (!body.trim()) {
      setError("Write the post body first.");
      return;
    }

    setError(null);
    setPending(publish ? "publish" : "save");
    const fields = {
      title: trimmedTitle,
      teaser: teaser.trim(),
      body,
      required_tier_id: requiredTierId || null,
    };
    try {
      let saved = created.current
        ? await updatePost(created.current.id, fields)
        : await createPost(fields);
      created.current = saved;
      if (publish) {
        saved = await updatePost(saved.id, {
          published_at: new Date().toISOString(),
        });
      }
      onSaved(saved);
    } catch {
      setError("Something went wrong. Please try again.");
      setPending(null);
    }
  }

  return (
    <div>
      <h2 id="post-form-title" className="text-lg font-semibold tracking-tight">
        {post ? "Edit post" : "New post"}
      </h2>
      <p className="text-muted mt-1 text-sm">
        The teaser is visible to everyone; the body unlocks with the tier you
        pick.
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          // Submit runs the primary action: publish, or for an already
          // published post, save in place.
          save(!isPublished);
        }}
        className="mt-4 space-y-3"
      >
        <label className="block">
          <span className="text-foreground mb-1 block text-xs font-medium">
            Title
          </span>
          <input
            ref={titleRef}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What's it about?"
            maxLength={200}
            className={FIELD_CLASS}
          />
        </label>

        <label className="block">
          <span className="text-foreground mb-1 block text-xs font-medium">
            Teaser <span className="text-muted font-normal">(optional)</span>
          </span>
          <textarea
            value={teaser}
            onChange={(e) => setTeaser(e.target.value)}
            placeholder="The preview everyone sees, even without access"
            rows={2}
            className={`${FIELD_CLASS} resize-none`}
          />
        </label>

        <label className="block">
          <span className="text-foreground mb-1 block text-xs font-medium">
            Body
          </span>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="The full post"
            rows={6}
            className={`${FIELD_CLASS} resize-none`}
          />
        </label>

        <label className="block">
          <span className="text-foreground mb-1 block text-xs font-medium">
            Who can read it
          </span>
          <select
            value={requiredTierId}
            onChange={(e) => setRequiredTierId(e.target.value)}
            className={`${FIELD_CLASS} cursor-pointer`}
          >
            <option value="">Everyone (public)</option>
            {tiers.map((tier) => (
              <option key={tier.id} value={tier.id}>
                {tier.name} members and up
              </option>
            ))}
          </select>
        </label>

        {error && (
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        )}

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onCancel}
            disabled={pending !== null}
            className="text-muted hover:text-foreground inline-flex h-9 cursor-pointer items-center px-2 text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50"
          >
            Cancel
          </button>
          {!isPublished && (
            <button
              type="button"
              onClick={() => save(false)}
              disabled={pending !== null}
              className="border-border text-foreground hover:bg-foreground/5 inline-flex h-9 cursor-pointer items-center rounded-full border px-4 text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50"
            >
              {pending === "save" ? "Saving…" : "Save draft"}
            </button>
          )}
          <button
            type="submit"
            disabled={pending !== null}
            className="bg-foreground text-background inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-sm font-medium transition-opacity hover:opacity-90 disabled:pointer-events-none disabled:opacity-50"
          >
            {isPublished
              ? pending === "save"
                ? "Saving…"
                : "Save changes"
              : pending === "publish"
                ? "Publishing…"
                : "Publish"}
          </button>
        </div>
      </form>
    </div>
  );
}
