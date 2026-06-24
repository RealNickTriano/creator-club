"use client";

import { useState } from "react";
import { logout } from "@/lib/api/auth";
import { useCurrentUser } from "@/lib/hooks/useCurrentUser";

/**
 * A floating pill fixed to the bottom of the viewport, shown only while signed
 * in as a demo account, reminding the visitor they're in a sandbox. Fixed (not
 * in flow) so it never adds page height or scroll. "Exit demo" clears the
 * session and returns to the login screen, fully leaving the demo. Renders
 * nothing for real accounts and signed-out visitors.
 */
export default function DemoBanner() {
  const { user } = useCurrentUser();
  const [exiting, setExiting] = useState(false);
  if (!user?.is_demo) return null;

  async function exitDemo() {
    setExiting(true);
    try {
      await logout();
    } finally {
      // Full navigation so the cleared session is reflected everywhere; lands
      // on /login even if the logout request itself failed.
      window.location.href = "/login";
    }
  }

  return (
    <div className="border-border bg-background text-foreground/80 fixed bottom-4 left-1/2 z-50 flex max-w-[calc(100%-2rem)] -translate-x-1/2 flex-col items-center gap-2 rounded-2xl border px-4 py-2 text-center text-xs shadow-lg sm:flex-row sm:gap-3 sm:rounded-full">
      <span>
        You&rsquo;re in <span className="font-semibold">demo mode</span> — a
        sandbox account.
      </span>
      <button
        type="button"
        onClick={exitDemo}
        disabled={exiting}
        className="border-border text-foreground hover:bg-foreground/10 focus-visible:ring-foreground focus-visible:ring-offset-background shrink-0 cursor-pointer rounded-full border px-3 py-0.5 font-medium transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50"
      >
        {exiting ? "Exiting…" : "Exit demo"}
      </button>
    </div>
  );
}
