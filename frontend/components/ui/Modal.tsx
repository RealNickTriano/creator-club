"use client";

import { useEffect } from "react";

/**
 * Generic modal: dimmed overlay with a centered card, closed by Escape or an
 * overlay click. Children supply the card content; pass `labelledBy` the id of
 * the heading inside so the dialog is announced correctly. `maxWidth` takes a
 * Tailwind max-width class to size the card.
 */
export default function Modal({
  open,
  onClose,
  labelledBy,
  maxWidth = "max-w-sm",
  children,
}: {
  open: boolean;
  onClose: () => void;
  labelledBy: string;
  maxWidth?: string;
  children: React.ReactNode;
}) {
  // Close on Escape while open.
  useEffect(() => {
    if (!open) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        onClick={onClose}
        aria-hidden="true"
        className="absolute inset-0 bg-black/40"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledBy}
        className={`border-border bg-background relative w-full rounded-2xl border p-6 shadow-lg ${maxWidth}`}
      >
        {children}
      </div>
    </div>
  );
}
