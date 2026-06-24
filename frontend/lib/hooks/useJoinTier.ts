"use client";

import { useState } from "react";
import { isCheckoutSession, setMembership } from "@/lib/api/memberships";
import type { Tier } from "@/types/tier";

type JoinTier = {
  /** The tier awaiting confirmation — feed it to `JoinTierDialog`. */
  confirming: Tier | null;
  /** True while the membership call runs (and stays true while redirecting). */
  pending: boolean;
  /** Set when the membership call fails; cleared on the next `request`. */
  error: boolean;
  /** Open the confirmation for this tier. */
  request: (tier: Tier) => void;
  /** Run the membership change for the tier being confirmed. */
  confirm: () => void;
  /** Dismiss the confirmation without joining. */
  close: () => void;
};

/**
 * The join/upgrade/downgrade flow behind `JoinTierDialog`: pick a tier to
 * confirm, then `POST /memberships` against `creatorId` on confirm. The
 * response forks by tier:
 *
 * - **Free tier** → the membership is set; the dialog closes and `onJoined`
 *   fires so the caller can refetch whatever it unlocks.
 * - **Paid tier** → the backend returns a Stripe Checkout URL; we redirect the
 *   browser there to collect payment. `pending` stays true through the
 *   navigation so the button keeps its loading state.
 *
 * No-ops when `creatorId` is null (signed out).
 */
export function useJoinTier(
  creatorId: string | null,
  onJoined?: () => void,
): JoinTier {
  const [confirming, setConfirming] = useState<Tier | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState(false);

  function request(tier: Tier) {
    setError(false);
    setConfirming(tier);
  }

  async function confirm() {
    if (!creatorId || !confirming) return;
    setError(false);
    setPending(true);
    try {
      const result = await setMembership(creatorId, confirming.id);
      if (isCheckoutSession(result)) {
        // Paid tier: hand off to Stripe. Leave `pending` set and the dialog
        // open — the browser is navigating away to the hosted checkout page.
        window.location.assign(result.checkout_url);
        return;
      }
      onJoined?.();
      setConfirming(null);
      setPending(false);
    } catch {
      setError(true);
      setPending(false);
    }
  }

  return {
    confirming,
    pending,
    error,
    request,
    confirm,
    close: () => setConfirming(null),
  };
}
