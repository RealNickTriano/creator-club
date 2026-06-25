import { apiFetch } from "@/lib/api/client";

/** A redirect to the signed-in user's Stripe Customer Portal. */
export interface PortalSession {
  portal_url: string;
}

/**
 * Opens a Stripe Customer Portal session for the signed-in user and returns its
 * hosted URL — the Stripe-hosted page where a fan manages payment methods,
 * cancels, or views invoices. Redirect the browser to `portal_url`.
 *
 * 400s if the user has no Stripe Customer yet (they've never subscribed to a
 * paid tier), so only call this for fans who have at least one subscription.
 */
export function createPortalSession(): Promise<PortalSession> {
  return apiFetch<PortalSession>("/billing/portal", { method: "POST" });
}
