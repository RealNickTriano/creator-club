import { apiFetch, apiUrl } from "@/lib/api/client";
import type { User } from "@/types/user";

/**
 * URL that begins the Google OAuth flow. This is a full-page navigation target
 * (an `<a href>` / `window.location`), not a fetch — the backend 302-redirects
 * the browser to Google's consent screen, then back to the app after callback.
 */
export function googleLoginUrl(): string {
  return apiUrl("/auth/google/login");
}

/** The current authenticated user. Rejects with a 401 `ApiError` if signed out. */
export function getCurrentUser(): Promise<User> {
  return apiFetch<User>("/auth/me");
}

/** Clears the session cookie on the backend. */
export function logout(): Promise<void> {
  return apiFetch<void>("/auth/logout", { method: "POST" });
}
