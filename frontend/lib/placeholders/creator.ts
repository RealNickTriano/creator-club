import type { CreatorPost } from "@/types/creator";

/**
 * Stand-in creator-page post data until the posts endpoints exist. Mirrors the
 * owner-view mockup in `creator-page-design.html`. (Tiers now come from the
 * backend via `lib/api/tiers`.)
 *
 * TODO: replace with `lib/api/posts` calls once those endpoints land.
 */
export const PLACEHOLDER_POSTS: CreatorPost[] = [
  {
    id: "p3",
    title: "Kiln rebuild — part one",
    body: "Tearing the old kiln down to the brick. Only you can see this while it's a draft — publish to add it to the feed.",
    requiredTier: "Insider",
    publishedAt: null,
  },
  {
    id: "p2",
    title: "Full glaze recipe + firing schedule",
    body: "The exact percentages, the kiln ramp, and the cooling curve I use for the speckled matte. As the owner you always see the full body, regardless of the required tier.",
    requiredTier: "Insider",
    publishedAt: "2026-05-30",
  },
  {
    id: "p1",
    title: "Why I switched to slower tools",
    body: "A year ago I ripped the automation out of my workflow. Here's what it cost me, what it gave back, and the one thing I'd never do again.",
    requiredTier: null,
    publishedAt: "2026-06-04",
  },
];
