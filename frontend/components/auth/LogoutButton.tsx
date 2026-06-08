"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/api/auth";

/** Ends the session on the backend, then returns to the login page. */
export default function LogoutButton() {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  async function onClick() {
    setPending(true);
    try {
      await logout();
    } finally {
      router.replace("/login");
    }
  }

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={pending}
      className="border-border text-foreground hover:bg-foreground/5 focus-visible:ring-foreground focus-visible:ring-offset-background inline-flex cursor-pointer items-center justify-center rounded-full border px-5 py-2.5 text-sm font-medium transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50"
    >
      {pending ? "Logging out…" : "Log out"}
    </button>
  );
}
