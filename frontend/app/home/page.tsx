"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import HomeShell from "@/components/home/HomeShell";
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

  return <HomeShell user={user}>{/* Main content goes here. */}</HomeShell>;
}
