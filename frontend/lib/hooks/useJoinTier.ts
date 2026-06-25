"use client";

import { useState } from "react";
import {
  isCheckoutSession,
  listMyMemberships,
  setMembership,
} from "@/lib/api/memberships";
import type { Tier } from "@/types/tier";

/** The post-confirmation state of an in-place membership change. */
export type ChangeStatus = "idle" | "finalizing" | "success";

/** How long to wait for the change to settle in the memberships list. */
const POLL_INTERVAL_MS = 1000;
const MAX_ATTEMPTS = 6;
/** Floor on the finalizing state so it reads as a step, not a flash. */
const MIN_FINALIZING_MS = 700;

type JoinTier = {
  /** The tier awaiting confirmation — feed it to `JoinTierDialog`. */
  confirming: Tier | null;
  /** True while the membership call runs (and stays true while redirecting). */
  pending: boolean;
  /** Set when the membership call fails; cleared on the next `request`. */
  error: boolean;
  /** Drives the finalize → congrats modal for an in-place change. */
  status: ChangeStatus;
  /** The tier the change landed on — names the congrats copy. */
  activeTier: Tier | null;
  /** Open the confirmation for this tier. */
  request: (tier: Tier) => void;
  /** Run the membership change for the tier being confirmed. */
  confirm: () => void;
  /** Dismiss the confirmation without joining. */
  close: () => void;
  /** Close the congrats screen (and refetch the page's data). */
  dismiss: () => void;
};

/**
 * The join/upgrade/downgrade flow behind `JoinTierDialog`: pick a tier to
 * confirm, then `POST /memberships` against `creatorId` on confirm. The
 * response forks by tier:
 *
 * - **Paid first-time join** → the backend returns a Stripe Checkout URL; we
 *   redirect the browser there. `pending` stays true through the navigation so
 *   the dialog button keeps its loading state. The congrats for this path is
 *   the Checkout return (see {@link useCheckoutReturn}).
 * - **In-place change** (paid↔paid, or a free join/downgrade) → the membership
 *   is updated synchronously and returned. We hand off to a finalize → congrats
 *   modal (mirroring the Checkout return): show a spinner, poll `/memberships`
 *   until the new tier is reflected, then a confirmation. `onJoined` refetches
 *   the page's data, deferred until the congrats is dismissed so the modal
 *   (which may be nested in the Billing modal) isn't torn down underneath it.
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
  const [status, setStatus] = useState<ChangeStatus>("idle");
  const [activeTier, setActiveTier] = useState<Tier | null>(null);

  function request(tier: Tier) {
    setError(false);
    setConfirming(tier);
  }

  // Wait for the memberships list to reflect the new tier (the optimistic write
  // is already persisted, so this usually settles on the first attempt).
  async function pollUntilHeld(tierId: string) {
    for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
      try {
        const memberships = await listMyMemberships();
        if (
          memberships.some(
            (m) =>
              m.creator_id === creatorId && m.tier.id === tierId && m.active,
          )
        ) {
          return;
        }
      } catch {
        // Transient — keep polling.
      }
      await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
    }
  }

  async function confirm() {
    if (!creatorId || !confirming) return;
    const tier = confirming;
    setError(false);
    setPending(true);
    try {
      const result = await setMembership(creatorId, tier.id);
      if (isCheckoutSession(result)) {
        // Paid tier: hand off to Stripe. Leave `pending` set and the dialog
        // open — the browser is navigating away to the hosted checkout page.
        window.location.assign(result.checkout_url);
        return;
      }
      // In-place change: swap the confirm dialog for the finalize → congrats
      // modal, then wait for it to settle (with a small floor on the spinner).
      setConfirming(null);
      setPending(false);
      setActiveTier(tier);
      setStatus("finalizing");
      await Promise.all([
        pollUntilHeld(tier.id),
        new Promise((resolve) => setTimeout(resolve, MIN_FINALIZING_MS)),
      ]);
      setStatus("success");
    } catch {
      setError(true);
      setPending(false);
    }
  }

  function dismiss() {
    setStatus("idle");
    setActiveTier(null);
    onJoined?.();
  }

  return {
    confirming,
    pending,
    error,
    status,
    activeTier,
    request,
    confirm,
    close: () => setConfirming(null),
    dismiss,
  };
}
