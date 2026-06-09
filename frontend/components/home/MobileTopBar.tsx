"use client";

import Wordmark from "@/components/brand/Wordmark";
import MenuIcon from "@/components/svg/MenuIcon";

/** Mobile-only top bar: brand + a button that opens the full-screen menu. */
export default function MobileTopBar({ onOpen }: { onOpen: () => void }) {
  return (
    <header className="border-border flex h-14 shrink-0 items-center justify-between border-b px-4 md:hidden">
      <Wordmark />
      <button
        type="button"
        onClick={onOpen}
        aria-label="Open menu"
        className="text-foreground-soft hover:bg-foreground/5 hover:text-foreground focus-visible:ring-foreground focus-visible:ring-offset-background inline-flex h-9 w-9 cursor-pointer items-center justify-center rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none"
      >
        <MenuIcon className="h-5 w-5" />
      </button>
    </header>
  );
}
