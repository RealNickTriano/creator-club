import type { ReactNode } from "react";

/**
 * Shared wrapper for the single-color, stroked line icons used across the app.
 * Each icon in this folder supplies only its `<path>`/`<circle>` children; this
 * component standardizes the viewBox, stroke styling and the `className` sizing
 * hook so the set stays visually consistent.
 */
export default function StrokeIcon({
  className,
  strokeWidth = 2,
  children,
}: {
  className?: string;
  strokeWidth?: number;
  children: ReactNode;
}) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className}
    >
      {children}
    </svg>
  );
}
