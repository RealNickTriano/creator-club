import { apiFetch } from "@/lib/api/client";
import type { CheckoutSession, Membership } from "@/types/membership";

/**
 * Fetches the signed-in user's memberships, each with its held tier and the
 * creator's public profile embedded. Canceled/expired rows are included —
 * `active` distinguishes them. `no-store` keeps the list fresh per request.
 */
export function listMyMemberships(): Promise<Membership[]> {
  return apiFetch<Membership[]>("/memberships", { cache: "no-store" });
}

/**
 * Sets the signed-in user's membership with a creator to a tier. The response
 * depends on the tier:
 *
 * - **Free tier** → the upsert runs server-side (join / resume / downgrade) and
 *   the resulting `Membership` is returned.
 * - **Paid tier** → no membership is created yet; a {@link CheckoutSession} is
 *   returned and the caller should redirect to its `checkout_url` so the fan
 *   can pay. The membership is provisioned once payment completes.
 *
 * Use {@link isCheckoutSession} to tell the two apart.
 */
export function setMembership(
  creatorId: string,
  tierId: string,
): Promise<Membership | CheckoutSession> {
  return apiFetch<Membership | CheckoutSession>("/memberships", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ creator_id: creatorId, tier_id: tierId }),
  });
}

/** Narrow a {@link setMembership} result to the paid-tier checkout response. */
export function isCheckoutSession(
  result: Membership | CheckoutSession,
): result is CheckoutSession {
  return "checkout_url" in result;
}

/**
 * Cancels the signed-in user's membership with a creator. A paid membership's
 * Stripe subscription is scheduled to end at the period close, so access
 * continues until then; the returned membership carries the `canceled_at` stamp.
 */
export function cancelMembership(creatorId: string): Promise<Membership> {
  return apiFetch<Membership>("/memberships/cancel", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ creator_id: creatorId }),
  });
}
