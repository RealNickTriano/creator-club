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
