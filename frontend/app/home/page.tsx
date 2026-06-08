"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import LogoutButton from "@/components/auth/LogoutButton";
import UserCard from "@/components/auth/UserCard";
import { useCurrentUser } from "@/lib/hooks/useCurrentUser";

export default function HomePage() {
  const { user, loading, error } = useCurrentUser();
  const router = useRouter();

  // Bounce signed-out visitors (no session / 401) back to login.
  useEffect(() => {
    if (!loading && (error || !user)) router.replace("/login");
  }, [loading, error, user, router]);

  if (loading || !user) {
    return (
      <main className="flex min-h-dvh items-center justify-center px-6">
        <p className="text-muted text-sm">Loading…</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-8 px-6">
      <div className="space-y-1 text-center">
        <p className="text-muted text-sm">Signed in as</p>
        <h1 className="text-2xl font-semibold tracking-tight">Home</h1>
      </div>
      <UserCard user={user} />
      <LogoutButton />
    </main>
  );
}
