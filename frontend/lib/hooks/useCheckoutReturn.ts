"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { listMyMemberships } from "@/lib/api/memberships";

export type CheckoutReturnStatus =
  | "idle"
  | "finalizing"
  | "success"
  | "canceled";

/** How long to wait for the webhook to provision the membership. */
const POLL_INTERVAL_MS = 1500;
const MAX_ATTEMPTS = 8;

/**
 * Handles the return from Stripe Checkout. The success/cancel URLs come back to
 * the creator page with a `?sub=success|cancel` marker (see the backend's
 * `create_subscription_checkout`):
 *
 * - **cancel** → surface a dismissible "canceled" note.
 * - **success** → the payment landed, but the membership is provisioned
 *   asynchronously by the Stripe webhook, which can lag the redirect by a
 *   beat. So we poll `/memberships` until this creator's membership is active
 *   (or we give up), then call `onActivated` to refetch the page's data so the
 *   feed unlocks.
 *
 * Either way the `?sub` param is stripped immediately so a refresh or Back
 * doesn't replay it.
 */
export function useCheckoutReturn(
  creatorId: string,
  onActivated: () => void,
): { status: CheckoutReturnStatus; dismiss: () => void } {
  const [status, setStatus] = useState<CheckoutReturnStatus>("idle");
  // Keep the latest callback without making it an effect dependency, so the
  // poll started on mount is never torn down and restarted.
  const onActivatedRef = useRef(onActivated);
  useEffect(() => {
    onActivatedRef.current = onActivated;
  });

  useEffect(() => {
    const sub = new URLSearchParams(window.location.search).get("sub");
    if (sub !== "success" && sub !== "cancel") return;

    // Strip the marker so the flow runs exactly once.
    window.history.replaceState(null, "", window.location.pathname);

    let live = true;
    void (async () => {
      if (sub === "cancel") {
        setStatus("canceled");
        return;
      }
      setStatus("finalizing");
      for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
        try {
          const memberships = await listMyMemberships();
          if (memberships.some((m) => m.creator_id === creatorId && m.active)) {
            break;
          }
        } catch {
          // Transient — keep polling.
        }
        await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
        if (!live) return;
      }
      if (!live) return;
      onActivatedRef.current();
      setStatus("success");
    })();

    return () => {
      live = false;
    };
  }, [creatorId]);

  const dismiss = useCallback(() => setStatus("idle"), []);
  return { status, dismiss };
}
