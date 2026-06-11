"use client";

import { useEffect } from "react";
import Wordmark from "@/components/brand/Wordmark";
import SidebarLogin from "@/components/home/SidebarLogin";
import SidebarNav from "@/components/home/SidebarNav";
import UserMenu from "@/components/home/UserMenu";
import CloseIcon from "@/components/svg/CloseIcon";
import type { User } from "@/types/user";

/**
 * Mobile-only full-screen menu drawer. Stays mounted so it animates both open
 * and closed; `inert` makes it non-interactive while hidden. Shares the nav and
 * user menu (or the signed-out login CTA) with the desktop sidebar.
 */
export default function MobileSidebar({
  user,
  open,
  onClose,
}: {
  user: User | null;
  open: boolean;
  onClose: () => void;
}) {
  useEffect(() => {
    if (!open) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  return (
    <div
      inert={!open}
      className={`bg-background fixed inset-0 z-50 flex transform-gpu flex-col transition-opacity duration-200 ease-out md:hidden ${
        open ? "opacity-100" : "pointer-events-none opacity-0"
      }`}
    >
      <div className="border-border flex h-14 shrink-0 items-center justify-between border-b px-4">
        <Wordmark />
        <button
          type="button"
          onClick={onClose}
          aria-label="Close menu"
          className="text-foreground-soft hover:bg-foreground/5 hover:text-foreground focus-visible:ring-foreground focus-visible:ring-offset-background inline-flex h-9 w-9 cursor-pointer items-center justify-center rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none"
        >
          <CloseIcon className="h-5 w-5" />
        </button>
      </div>

      <SidebarNav onNavigate={onClose} />

      <div className="border-border border-t p-3">
        {user ? <UserMenu user={user} collapsed={false} /> : <SidebarLogin />}
      </div>
    </div>
  );
}
