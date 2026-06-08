import Link from "next/link";
import { BRAND_GRADIENT } from "@/lib/brand";

/**
 * The "Your creator page" card shown once the signed-in user's page is live
 * (mockup A): their public URL plus tier/post counts, with View and Edit
 * actions. Before a page exists, {@link CreatorPageSetupCard} takes its place.
 */
export default function CreatorPageLiveCard({
  handle,
  tierCount,
  postCount,
  editHref = "/settings",
}: {
  handle: string;
  tierCount: number;
  postCount: number;
  editHref?: string;
}) {
  const viewHref = `/c/${handle}`;
  const meta = `creatorclub.com/c/${handle} · ${tierCount} ${
    tierCount === 1 ? "tier" : "tiers"
  } · ${postCount} ${postCount === 1 ? "post" : "posts"}`;

  return (
    <div className="border-border bg-background flex items-center gap-4 rounded-xl border p-4">
      <span
        aria-hidden="true"
        className="h-12 w-12 shrink-0 rounded-full shadow-sm"
        style={{ backgroundImage: BRAND_GRADIENT }}
      />
      <div className="min-w-0 flex-1">
        <b className="text-foreground text-sm font-semibold">
          Your page is live
        </b>
        <p className="text-foreground-soft mt-0.5 truncate text-sm">{meta}</p>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <Link
          href={viewHref}
          className="border-border text-foreground hover:bg-foreground/5 inline-flex h-9 items-center rounded-full border px-4 text-sm font-medium transition-colors"
        >
          View
        </Link>
        <Link
          href={editHref}
          className="bg-foreground text-background inline-flex h-9 items-center rounded-full px-4 text-sm font-medium transition-opacity hover:opacity-90"
        >
          Edit
        </Link>
      </div>
    </div>
  );
}
