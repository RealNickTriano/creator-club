import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { AuthContext, type AuthContextValue, type User } from './auth-context'

// Backend API origin. Override with VITE_API_URL in the environment if needed.
const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

/**
 * Holds the user session for the app. Performs a /auth/me check on mount (the
 * session cookie identifies the user, if any) and exposes login/logout/refresh.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/auth/me`, { credentials: 'include' })
      setUser(res.ok ? await res.json() : null)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  // Resolve the current user once, when the provider mounts. The setState
  // happens in refresh()'s async callback (after the fetch resolves), not
  // synchronously during render — this is the canonical "sync with an external
  // system" effect, so the set-state-in-effect heuristic is a false positive.
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refresh()
  }, [refresh])

  const login = useCallback(() => {
    window.location.href = `${API_URL}/auth/google/login`
  }, [])

  const logout = useCallback(async () => {
    await fetch(`${API_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    })
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, login, logout, refresh }),
    [user, loading, login, logout, refresh],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
