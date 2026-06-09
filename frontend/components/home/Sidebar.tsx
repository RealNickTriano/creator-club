"use client";

import { useState } from "react";
import Wordmark from "@/components/brand/Wordmark";
import SidebarNav from "@/components/home/SidebarNav";
import UserMenu from "@/components/home/UserMenu";
import MenuIcon from "@/components/svg/MenuIcon";
import type { User } from "@/types/user";

/**
 * Desktop sidebar: brand + collapse toggle up top, navigation in the middle,
 * and the signed-in user pinned to the bottom. Collapses to an icon rail.
 * Hidden on mobile, where {@link MobileSidebar} takes over as a drawer.
 */
export default function Sidebar({ user }: { user: User }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`border-border hidden h-full shrink-0 flex-col border-r transition-[width] duration-300 ease-out md:flex ${collapsed ? "w-16" : "w-60"}`}
    >
      {/* Header: wordmark (when expanded) + collapse toggle. */}
      <div
        className={`flex h-16 items-center overflow-hidden px-3 ${collapsed ? "justify-center" : "justify-between"}`}
      >
        {!collapsed && <Wordmark />}
        <button
          type="button"
          onClick={() => setCollapsed((c) => !c)}
          aria-label="Toggle sidebar"
          aria-expanded={!collapsed}
          className="text-foreground-soft hover:bg-foreground/5 hover:text-foreground focus-visible:ring-foreground focus-visible:ring-offset-background inline-flex h-9 w-9 shrink-0 cursor-pointer items-center justify-center rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none"
        >
          <MenuIcon className="h-5 w-5" />
        </button>
      </div>

      <SidebarNav collapsed={collapsed} />

      {/* Footer: signed-in user + menu (theme, logout). */}
      <div className="border-border border-t p-3">
        <UserMenu user={user} collapsed={collapsed} />
      </div>
    </aside>
  );
}
