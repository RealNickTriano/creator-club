import Link from "next/link";
import { BRAND_GRADIENT } from "@/lib/brand";

/**
 * The "Your creator page" card shown when the signed-in user hasn't set up
 * their own page yet (mockup B). It's a dashed, gradient-washed CTA nudging
 * them to create one. Once their page is live, {@link CreatorPageLiveCard}
 * takes its place instead.
 */
export default function CreatorPageSetupCard({
  href = "/settings",
}: {
  href?: string;
}) {
  return (
    <div
      className="border-border flex items-center gap-4 rounded-xl border border-dashed p-4"
      style={{
        backgroundImage:
          "linear-gradient(120deg, rgba(194,207,250,0.16), rgba(247,181,196,0.16))",
      }}
    >
      <span
        aria-hidden="true"
        className="h-12 w-12 shrink-0 rounded-full shadow-sm"
        style={{ backgroundImage: BRAND_GRADIENT }}
      />
      <div className="min-w-0 flex-1">
        <b className="text-foreground text-sm font-semibold">
          Set up your creator page
        </b>
        <p className="text-foreground-soft mt-0.5 text-sm">
          Pick a handle, add tiers, and start sharing work with members.
        </p>
      </div>
      <Link
        href={href}
        className="bg-foreground text-background inline-flex h-9 shrink-0 items-center rounded-full px-4 text-sm font-medium transition-opacity hover:opacity-90"
      >
        Set up
      </Link>
    </div>
  );
}
