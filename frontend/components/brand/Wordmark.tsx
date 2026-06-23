import Link from "next/link";
import BrandMark from "@/components/brand/BrandMark";

/** The Creator Club wordmark: gradient brand dot + name. Links home. */
export default function Wordmark() {
  return (
    <Link
      href="/"
      className="flex items-center gap-3 text-lg font-semibold tracking-tight whitespace-nowrap"
    >
      <BrandMark />
      Creator Club
    </Link>
  );
}
