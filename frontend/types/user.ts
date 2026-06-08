/** The current authenticated user, as returned by `GET /auth/me`. */
export interface User {
  id: string;
  /** Chosen handle; null until the user picks one. */
  handle: string | null;
  google_name: string;
  bio: string | null;
  google_avatar_url: string | null;
  google_email: string;
  last_logged_in_at: string;
  created_at: string;
}
