"use client";

import Link from "next/link";
import { useCurrentUser } from "@/lib/hooks/useCurrentUser";

/**
 * Landing-page nav auth state: a "Sign in" link when signed out, or the user's
 * avatar + name (linking to /home) when signed in. Renders nothing while the
 * session check is in flight to avoid flashing the wrong state.
 */
export default function AuthNav() {
  const { user, loading } = useCurrentUser();

  if (loading) return null;

  if (!user) {
    return (
      <Link
        href="/login"
        className="text-foreground-soft hover:text-foreground text-sm font-medium transition-colors"
      >
        Sign in
      </Link>
    );
  }

  return (
    <Link
      href="/home"
      className="hover:bg-foreground/5 flex items-center gap-2.5 rounded-full py-1 pr-3 pl-1 text-sm font-medium transition-colors"
    >
      {user.google_avatar_url ? (
        // eslint-disable-next-line @next/next/no-img-element -- remote avatar, no next/image domain config
        <img
          src={user.google_avatar_url}
          alt=""
          className="h-7 w-7 rounded-full object-cover"
        />
      ) : (
        <span className="bg-foreground/10 flex h-7 w-7 items-center justify-center rounded-full text-xs">
          {user.google_name.charAt(0).toUpperCase()}
        </span>
      )}
      <span className="hidden sm:inline">{user.google_name}</span>
    </Link>
  );
}
