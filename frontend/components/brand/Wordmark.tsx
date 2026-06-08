import Link from "next/link";
import { BRAND_GRADIENT } from "@/lib/brand";

/** The Creator Club wordmark: gradient brand dot + name. Links home. */
export default function Wordmark() {
  return (
    <Link
      href="/"
      className="flex items-center gap-3 text-lg font-semibold tracking-tight whitespace-nowrap"
    >
      <span
        aria-hidden="true"
        className="h-4 w-4 shrink-0 rounded-full shadow-sm"
        style={{ backgroundImage: BRAND_GRADIENT }}
      />
      Creator Club
    </Link>
  );
}
