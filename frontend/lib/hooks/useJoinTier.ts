"use client";

import { useState } from "react";
import { setMembership } from "@/lib/api/memberships";
import type { Tier } from "@/types/tier";

type JoinTier = {
  /** The tier awaiting confirmation — feed it to `JoinTierDialog`. */
  confirming: Tier | null;
  /** True while the membership call runs (paid tiers simulate billing ~2s). */
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
 * confirm, then run `PUT /memberships` against `creatorId` on confirm. On
 * success the dialog closes and `onJoined` fires so the caller can refetch
 * whatever the new membership unlocks. No-ops when `creatorId` is null
 * (signed out).
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
      await setMembership(creatorId, confirming.id);
      onJoined?.();
      setConfirming(null);
    } catch {
      setError(true);
    } finally {
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
