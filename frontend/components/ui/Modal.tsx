"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Generic modal: dimmed overlay with a centered card, closed by Escape or an
 * overlay click. Children supply the card content; pass `labelledBy` the id of
 * the heading inside so the dialog is announced correctly. `maxWidth` takes a
 * Tailwind max-width class to size the card.
 *
 * Opening and closing are animated: when `open` flips off, the modal stays
 * mounted playing the exit animation and leaves the DOM on `animationend`.
 * The exit shows a snapshot of the last open content, since callers typically
 * clear the state driving `children` in the same update that closes them.
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
  const [prevOpen, setPrevOpen] = useState(open);
  const [closing, setClosing] = useState(false);
  // The last children rendered while open — what the exit animation shows.
  // Deliberate render-time ref use: callers clear the state driving
  // `children` in the same update that closes the modal, so the snapshot
  // must be taken every open render, and staleness during the exit is
  // exactly what we want.
  const frozenChildren = useRef<React.ReactNode>(null);
  // eslint-disable-next-line react-hooks/refs
  if (open) frozenChildren.current = children;

  // Adjust state during render (not in an effect): when `open` flips off,
  // hold the modal in its closing state until the exit animation finishes.
  if (open !== prevOpen) {
    setPrevOpen(open);
    setClosing(!open);
  }

  // Close on Escape while open.
  useEffect(() => {
    if (!open) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open && !closing) return null;

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center p-4 ${
        closing ? "pointer-events-none" : ""
      }`}
    >
      <div
        onClick={onClose}
        aria-hidden="true"
        className={`absolute inset-0 bg-black/40 ${
          closing ? "animate-modal-fade-out" : "animate-modal-fade"
        }`}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledBy}
        onAnimationEnd={(e) => {
          // Unmount once the card's own exit animation ends (children may
          // bubble their own animationend events up — ignore those).
          if (closing && e.target === e.currentTarget) setClosing(false);
        }}
        className={`border-border bg-background relative w-full rounded-2xl border p-6 shadow-lg ${
          closing ? "animate-modal-pop-out" : "animate-modal-pop"
        } ${maxWidth}`}
      >
        {/* eslint-disable-next-line react-hooks/refs -- see snapshot note above */}
        {open ? children : frozenChildren.current}
      </div>
    </div>
  );
}
