import { apiFetch } from "@/lib/api/client";
import type { Membership } from "@/types/membership";

/**
 * Fetches the signed-in user's memberships, each with its held tier and the
 * creator's public profile embedded. Canceled/expired rows are included —
 * `active` distinguishes them. `no-store` keeps the list fresh per request.
 */
export function listMyMemberships(): Promise<Membership[]> {
  return apiFetch<Membership[]>("/memberships", { cache: "no-store" });
}

/**
 * Sets the signed-in user's membership with a creator to a tier — one
 * upsert-style call covers join, resume, upgrade and downgrade. Paid tiers
 * run the backend's simulated billing (~2s), so callers should show a
 * pending state.
 */
export function setMembership(
  creatorId: string,
  tierId: string,
): Promise<Membership> {
  return apiFetch<Membership>("/memberships", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ creator_id: creatorId, tier_id: tierId }),
  });
}
