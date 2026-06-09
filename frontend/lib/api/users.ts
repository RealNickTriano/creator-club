import { apiFetch, ApiError } from "@/lib/api/client";
import type { PublicUser, UpdateUserProfile, User } from "@/types/user";

/**
 * Updates the signed-in user's profile (handle and/or bio) and returns the
 * updated user. Rejects with a 409 `ApiError` if the handle is already taken.
 */
export function updateProfile(update: UpdateUserProfile): Promise<User> {
  return apiFetch<User>("/user", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(update),
  });
}

/**
 * Sets the current user's handle — the `@name` that becomes their creator page
 * address (`/c/{handle}`). Returns the updated user. Rejects with a 409
 * `ApiError` if the handle is already taken.
 */
export function setHandle(handle: string): Promise<User> {
  return apiFetch<User>("/user", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ handle }),
  });
}

/**
 * Fetches the public profile for a handle, or `null` if no such user exists —
 * used to decide whether a creator page at `/c/{handle}` should render or 404.
 * `no-store` keeps the existence check fresh per request.
 */
export async function getUserByHandle(
  handle: string,
): Promise<PublicUser | null> {
  try {
    return await apiFetch<PublicUser>(`/user/${encodeURIComponent(handle)}`, {
      cache: "no-store",
    });
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}
