import { useAuth } from './auth/useAuth'

function App() {
  const { user, loading, login, logout } = useAuth()

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center gap-6 px-6">
      <span className="rounded-full bg-violet-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-violet-300 ring-1 ring-violet-500/40">
        Creator Club
      </span>

      {loading ? (
        <p className="text-slate-400">Loading…</p>
      ) : user ? (
        <div className="flex items-center gap-4 rounded-2xl bg-slate-900 px-5 py-4 ring-1 ring-slate-800">
          {user.google_avatar_url ? (
            <img
              src={user.google_avatar_url}
              alt=""
              className="h-10 w-10 rounded-full"
            />
          ) : (
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-violet-500/20 text-sm font-semibold text-violet-200">
              {user.google_email[0]?.toUpperCase()}
            </div>
          )}
          <span className="text-sm text-slate-300">{user.google_email}</span>
          <button
            onClick={logout}
            className="rounded-lg bg-slate-800 px-3 py-1.5 text-sm font-medium text-slate-200 ring-1 ring-slate-700 transition hover:bg-slate-700"
          >
            Log out
          </button>
        </div>
      ) : (
        <button
          onClick={login}
          className="rounded-lg bg-violet-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-violet-500"
        >
          Sign in with Google
        </button>
      )}
    </div>
  )
}

export default App
