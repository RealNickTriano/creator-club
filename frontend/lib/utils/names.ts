import type { PublicUser, User } from "@/types/user";

/**
 * The name a user is shown as to other users: their chosen display name,
 * falling back to their Google name. `null` when they have neither — callers
 * pick a context-appropriate fallback (handle, "Creator", …).
 */
export function displayName(user: User | PublicUser): string | null {
  return user.display_name ?? user.google_name;
}
