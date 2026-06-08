import { createContext } from 'react'

// Mirrors the backend's PrivateUser schema (what /auth/me returns to the owner).
export type User = {
  id: string
  handle: string | null
  google_name: string | null
  bio: string | null
  google_avatar_url: string | null
  google_email: string
  last_logged_in_at: string | null
  created_at: string
}

export type AuthContextValue = {
  /** The signed-in user, or null when signed out. */
  user: User | null
  /** True until the initial /auth/me check resolves. */
  loading: boolean
  /** Redirect to Google's OAuth consent screen. */
  login: () => void
  /** Clear the server session and local user state. */
  logout: () => Promise<void>
  /** Re-fetch the current user from the server (e.g. after sign-in). */
  refresh: () => Promise<void>
}

// `null` means "no provider above me" — useAuth() turns that into a clear error.
export const AuthContext = createContext<AuthContextValue | null>(null)
