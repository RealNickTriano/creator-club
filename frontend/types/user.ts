/**
 * A user as seen by anyone — the public profile returned by
 * `GET /user/{handle}` and shown on a creator page. A narrower view than
 * {@link User}: no email or timestamps.
 */
export interface PublicUser {
  id: string;
  handle: string | null;
  google_name: string | null;
  bio: string | null;
  google_avatar_url: string | null;
}

/** The current authenticated user, as returned by `GET /auth/me`. */
export interface User {
  id: string;
  /** Chosen handle; null until the user picks one. */
  handle: string | null;
  google_name: string | null;
  bio: string | null;
  google_avatar_url: string | null;
  google_email: string;
  last_logged_in_at: string;
  created_at: string;
}
