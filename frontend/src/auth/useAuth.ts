import { useContext } from 'react'

import { AuthContext } from './auth-context'

/** Access the auth session. Throws if used outside an <AuthProvider>. */
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (ctx === null) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}
