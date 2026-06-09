"use client";

import { useEffect, useRef, useState } from "react";
import { ApiError } from "@/lib/api/client";
import { createTier, updateTier } from "@/lib/api/tiers";
import type { Tier } from "@/types/tier";

const FIELD_CLASS =
  "border-border focus:border-foreground/30 placeholder:text-muted " +
  "text-foreground w-full rounded-xl border bg-transparent px-4 py-2.5 " +
  "text-sm outline-none transition-colors";

/**
 * The tier form, shown in a modal from the owner's Memberships tab. Name and
 * monthly price (in dollars, 0 = free); the tier's rank — its access level —
 * defaults to the next rung and stays editable. Creates a tier, or edits the
 * one passed via `tier` (fields are prefilled; state initializes on mount, so
 * remount — e.g. with a `key` — to switch tiers). On success the saved tier is
 * handed to `onSaved`.
 */
export default function TierForm({
  tier,
  defaultRank,
  onSaved,
  onCancel,
}: {
  tier?: Tier;
  defaultRank: number;
  onSaved: (tier: Tier) => void;
  onCancel: () => void;
}) {
  const [name, setName] = useState(tier?.name ?? "");
  const [price, setPrice] = useState(
    tier ? String(tier.price_cents / 100) : "0",
  );
  const [rank, setRank] = useState(String(tier?.rank ?? defaultRank));
  const [description, setDescription] = useState(tier?.description ?? "");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const nameRef = useRef<HTMLInputElement>(null);

  // The form mounts when the modal opens, so focus the first field once.
  useEffect(() => {
    nameRef.current?.focus();
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();

    const trimmedName = name.trim();
    const priceDollars = Number(price);
    const rankValue = Number(rank);

    if (!trimmedName || trimmedName.length > 80) {
      setError("Give the tier a name (up to 80 characters).");
      return;
    }
    if (!Number.isFinite(priceDollars) || priceDollars < 0) {
      setError("Price must be 0 or more — 0 makes the tier free.");
      return;
    }
    if (!Number.isInteger(rankValue) || rankValue < 0) {
      setError("Rank must be a whole number, 0 or higher.");
      return;
    }

    setError(null);
    setPending(true);
    const fields = {
      name: trimmedName,
      rank: rankValue,
      price_cents: Math.round(priceDollars * 100),
      description: description.trim() || null,
    };
    try {
      const saved = tier
        ? await updateTier(tier.id, fields)
        : await createTier(fields);
      onSaved(saved);
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 409
          ? "You already have a tier with that name or rank."
          : "Something went wrong. Please try again.",
      );
      setPending(false);
    }
  }

  return (
    <div>
      <h2 id="tier-form-title" className="text-lg font-semibold tracking-tight">
        {tier ? "Edit tier" : "New tier"}
      </h2>
      <p className="text-muted mt-1 text-sm">
        A rung on your membership ladder — higher ranks unlock more of your
        posts.
      </p>

      <form onSubmit={onSubmit} className="mt-4 space-y-3">
        <label className="block">
          <span className="text-foreground mb-1 block text-xs font-medium">
            Name
          </span>
          <input
            ref={nameRef}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Supporter"
            maxLength={80}
            className={FIELD_CLASS}
          />
        </label>

        <div className="flex gap-3">
          <label className="block flex-1">
            <span className="text-foreground mb-1 block text-xs font-medium">
              Price ($ / month)
            </span>
            <input
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              inputMode="decimal"
              placeholder="0"
              aria-describedby="tier-price-hint"
              className={FIELD_CLASS}
            />
          </label>
          <label className="block w-24">
            <span className="text-foreground mb-1 block text-xs font-medium">
              Rank
            </span>
            <input
              value={rank}
              onChange={(e) => setRank(e.target.value)}
              inputMode="numeric"
              className={FIELD_CLASS}
            />
          </label>
        </div>
        <p id="tier-price-hint" className="text-muted text-xs">
          Price 0 makes a free tier; rank is its access level.
        </p>

        <label className="block">
          <span className="text-foreground mb-1 block text-xs font-medium">
            Description{" "}
            <span className="text-muted font-normal">(optional)</span>
          </span>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What members at this tier get"
            rows={3}
            className={`${FIELD_CLASS} resize-none`}
          />
        </label>

        {error && (
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        )}

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onCancel}
            className="border-border text-foreground hover:bg-foreground/5 inline-flex h-9 cursor-pointer items-center rounded-full border px-4 text-sm font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={pending}
            className="bg-foreground text-background inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-sm font-medium transition-opacity hover:opacity-90 disabled:pointer-events-none disabled:opacity-50"
          >
            {pending ? "Saving…" : tier ? "Save changes" : "Create tier"}
          </button>
        </div>
      </form>
    </div>
  );
}
