import { apiFetch, ApiError } from "@/lib/api/client";
import type { NewTier, Tier, UpdateTier } from "@/types/tier";

/**
 * Creates a tier on the signed-in user's own ladder and returns it. Rejects
 * with a 409 `ApiError` when they already have a tier with that name or rank.
 */
export function createTier(newTier: NewTier): Promise<Tier> {
  return apiFetch<Tier>("/tiers", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(newTier),
  });
}

/**
 * Updates one of the signed-in user's own tiers and returns it. Rejects with
 * a 409 `ApiError` when the new name or rank clashes with another tier.
 */
export function updateTier(tierId: string, update: UpdateTier): Promise<Tier> {
  return apiFetch<Tier>(`/tiers/${encodeURIComponent(tierId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(update),
  });
}

/**
 * Fetches a creator's tier ladder by handle, ordered by rank ascending, or
 * `null` if no user has this handle — mirroring `getUserByHandle` so the
 * creator page can treat both lookups the same way. `no-store` keeps the
 * ladder fresh per request.
 */
export async function getTiersByHandle(handle: string): Promise<Tier[] | null> {
  try {
    return await apiFetch<Tier[]>(
      `/tiers?handle=${encodeURIComponent(handle)}`,
      { cache: "no-store" },
    );
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}
