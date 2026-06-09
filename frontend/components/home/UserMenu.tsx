"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import UserAvatar from "@/components/auth/UserAvatar";
import LogOutIcon from "@/components/svg/LogOutIcon";
import ThemeToggle from "@/components/ui/ThemeToggle";
import { logout } from "@/lib/api/auth";
import type { User } from "@/types/user";

/**
 * The signed-in user at the bottom of the sidebar. Clicking opens the theme +
 * sign-out menu: an upward popover on desktop, a bottom sheet that slides up on
 * mobile. Closes on outside click / Escape / backdrop tap.
 */
export default function UserMenu({
  user,
  collapsed,
}: {
  user: User;
  collapsed: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    if (!open) return;
    function onPointerDown(e: PointerEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  async function onLogout() {
    setPending(true);
    try {
      await logout();
    } finally {
      router.replace("/login");
    }
  }

  const menuItems = (
    <>
      <div className="flex items-center justify-between gap-3 px-3 py-2 text-sm font-medium">
        <span>Theme</span>
        <ThemeToggle />
      </div>

      <div className="bg-border my-1 h-px" />

      <button
        type="button"
        role="menuitem"
        onClick={onLogout}
        disabled={pending}
        className="hover:bg-foreground/5 flex w-full cursor-pointer items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50"
      >
        <LogOutIcon className="h-4 w-4 shrink-0" />
        {pending ? "Logging out…" : "Log out"}
      </button>
    </>
  );

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="menu"
        aria-expanded={open}
        title={collapsed ? user.google_name : undefined}
        className={`hover:bg-foreground/5 flex w-full cursor-pointer items-center gap-3 rounded-lg p-2 text-left transition-colors ${collapsed ? "justify-center" : ""}`}
      >
        <UserAvatar user={user} size={32} />
        {!collapsed && (
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{user.google_name}</p>
            <p className="text-muted truncate text-xs">{user.google_email}</p>
          </div>
        )}
      </button>

      {/* Desktop: upward popover. */}
      <div
        role="menu"
        inert={!open}
        className={`border-border bg-background absolute bottom-full left-0 z-50 mb-2 hidden w-56 origin-bottom rounded-xl border p-1 shadow-lg transition duration-150 ease-out md:block ${
          open
            ? "translate-y-0 scale-100 opacity-100"
            : "pointer-events-none translate-y-1 scale-95 opacity-0"
        }`}
      >
        {menuItems}
      </div>

      {/* Mobile: bottom sheet with a dimmed backdrop. */}
      <div className="md:hidden" inert={!open}>
        <div
          onClick={() => setOpen(false)}
          className={`fixed inset-0 z-50 bg-black/40 transition-opacity duration-200 ease-out ${
            open ? "opacity-100" : "pointer-events-none opacity-0"
          }`}
        />
        <div
          role="menu"
          className={`border-border bg-background fixed inset-x-0 bottom-0 z-50 rounded-t-2xl border-t p-2 pb-4 shadow-lg transition-transform duration-300 ease-out ${
            open ? "translate-y-0" : "translate-y-full"
          }`}
        >
          <div className="bg-border mx-auto mb-2 h-1.5 w-10 rounded-full" />
          {menuItems}
        </div>
      </div>
    </div>
  );
}
