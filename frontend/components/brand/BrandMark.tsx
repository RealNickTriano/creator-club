import { BRAND_GRADIENT } from "@/lib/brand";

/**
 * The Creator Club logo on its own — the gradient brand dot, no wordmark text.
 * Size it via `className` (defaults to the inline wordmark size). The {@link
 * Wordmark} pairs this with the name; on its own it's the standalone mark.
 */
export default function BrandMark({
  className = "h-4 w-4",
}: {
  className?: string;
}) {
  return (
    <span
      aria-hidden="true"
      className={`shrink-0 rounded-full shadow-sm ${className}`}
      style={{ backgroundImage: BRAND_GRADIENT }}
    />
  );
}
