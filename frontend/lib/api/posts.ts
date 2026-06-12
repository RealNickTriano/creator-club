import { apiFetch, ApiError } from "@/lib/api/client";
import type { Post } from "@/types/post";

/**
 * Fetches a creator's published feed by handle, newest first, with the
 * current viewer's entitlement already applied per post (`body` is `null` on
 * locked posts). Returns `null` if no user has this handle — mirroring
 * `getUserByHandle` so callers can treat both lookups the same way.
 * `no-store` keeps the entitlements fresh per request.
 */
export async function getPostsByHandle(handle: string): Promise<Post[] | null> {
  try {
    return await apiFetch<Post[]>(
      `/posts?handle=${encodeURIComponent(handle)}`,
      { cache: "no-store" },
    );
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

/**
 * Fetches the signed-in user's own drafts, newest first, with full body.
 * Rejects with a 401 `ApiError` when not signed in.
 */
export function listMyDrafts(): Promise<Post[]> {
  return apiFetch<Post[]>("/posts/drafts", { cache: "no-store" });
}
