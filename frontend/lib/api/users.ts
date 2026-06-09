import { apiFetch } from "@/lib/api/client";
import type { User } from "@/types/user";

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
