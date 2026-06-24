"use client";

import MembershipTierCard from "@/components/creator/MembershipTierCard";
import Modal from "@/components/ui/Modal";
import type { Tier } from "@/types/tier";

/** The membership change the viewer kicked off, deciding the dialog's labels. */
export type JoinVerb = "Join" | "Upgrade" | "Downgrade";

const PENDING_LABELS: Record<JoinVerb, string> = {
  Join: "Joining…",
  Upgrade: "Upgrading…",
  Downgrade: "Downgrading…",
};

/**
 * The confirmation step before a membership change: shows the tier the viewer
 * is about to hold (as a read-only card) with cancel / confirm. Open whenever
 * `tier` is set. While `pending` the buttons lock and the dialog can't be
 * dismissed. A **paid** tier confirms into a redirect to Stripe Checkout, so
 * its labels say so; a free tier updates the membership in place.
 */
export default function JoinTierDialog({
  tier,
  verb,
  pending,
  error,
  onConfirm,
  onClose,
}: {
  tier: Tier | null;
  verb: JoinVerb;
  pending: boolean;
  error: boolean;
  onConfirm: () => void;
  onClose: () => void;
}) {
  const isPaid = tier !== null && tier.price_cents > 0;

  function close() {
    if (!pending) onClose();
  }

  function confirmLabel(): string {
    if (pending) return isPaid ? "Redirecting…" : PENDING_LABELS[verb];
    if (isPaid) return "Continue to payment";
    return verb === "Join" ? "Join Tier" : verb;
  }

  return (
    <Modal
      open={tier !== null}
      onClose={close}
      labelledBy="join-tier-title"
      maxWidth="max-w-md"
    >
      {tier && (
        <div className="space-y-4">
          <h2
            id="join-tier-title"
            className="text-lg font-semibold tracking-tight"
          >
            {verb === "Join" ? `Join ${tier.name}` : `${verb} to ${tier.name}`}
          </h2>

          <MembershipTierCard tier={tier} />

          <p className="text-muted text-sm">
            {isPaid
              ? "You'll be taken to Stripe to complete payment. You can change tiers any time."
              : "Your membership updates immediately — you can change tiers any time."}
          </p>

          {error && (
            <p className="text-sm text-red-600 dark:text-red-400">
              Something went wrong — please try again.
            </p>
          )}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={close}
              disabled={pending}
              className="border-border text-foreground hover:bg-foreground/5 inline-flex h-9 cursor-pointer items-center rounded-full border px-4 text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={onConfirm}
              disabled={pending}
              className="bg-foreground text-background inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-sm font-medium transition-opacity hover:opacity-90 disabled:pointer-events-none disabled:opacity-50"
            >
              {confirmLabel()}
            </button>
          </div>
        </div>
      )}
    </Modal>
  );
}
