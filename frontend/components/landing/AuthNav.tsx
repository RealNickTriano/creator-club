"use client";

import Link from "next/link";
import UserAvatar from "@/components/auth/UserAvatar";
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
      <UserAvatar user={user} size={28} />
      <span className="hidden sm:inline">{user.google_name}</span>
    </Link>
  );
}
