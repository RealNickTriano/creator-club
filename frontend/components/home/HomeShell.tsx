"use client";

import { useState } from "react";
import MobileSidebar from "@/components/home/MobileSidebar";
import MobileTopBar from "@/components/home/MobileTopBar";
import Sidebar from "@/components/home/Sidebar";
import type { User } from "@/types/user";

/**
 * Responsive home layout. On desktop it's a persistent left sidebar beside the
 * main content; on mobile the sidebar collapses to a top bar whose button opens
 * the menu as a full-screen drawer.
 */
export default function HomeShell({
  user,
  children,
}: {
  user: User;
  children?: React.ReactNode;
}) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex h-dvh flex-col overflow-hidden md:flex-row">
      <MobileTopBar onOpen={() => setMobileOpen(true)} />
      <Sidebar user={user} />
      <MobileSidebar
        user={user}
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
      />
      <main className="flex-1 overflow-y-auto p-6 sm:p-8">{children}</main>
    </div>
  );
}
