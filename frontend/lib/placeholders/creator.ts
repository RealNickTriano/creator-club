import type { Post } from "@/types/post";
import type { Tier } from "@/types/tier";

/**
 * Stand-in creator-page post data, shaped exactly like `GET /posts?handle=...`
 * responses, exercising every state `PostCard` renders. The viewer list mixes
 * access reasons that couldn't co-occur for one real viewer — deliberately, so
 * every lock variant is visible while the page isn't wired to the API yet.
 *
 * TODO: replace with `lib/api/posts` calls now that the endpoints exist.
 */

function exampleTier(name: string, rank: number, price_cents: number): Tier {
  return {
    id: `example-tier-${rank}`,
    user_id: "example-creator",
    name,
    rank,
    price_cents,
    description: null,
    created_at: "2026-05-01T12:00:00Z",
    updated_at: "2026-05-01T12:00:00Z",
  };
}

const FREE_TIER = exampleTier("Free", 0, 0);
const SUPPORTER_TIER = exampleTier("Supporter", 1, 500);
const INSIDER_TIER = exampleTier("Insider", 2, 1200);

function examplePost(
  id: string,
  fields: Pick<Post, "title" | "teaser" | "body" | "published_at" | "access">,
): Post {
  return {
    id,
    user_id: "example-creator",
    required_tier_id: fields.access.required_tier?.id ?? null,
    created_at: "2026-05-20T12:00:00Z",
    ...fields,
  };
}

/** What a visitor sees: one card per access variant, locked and unlocked. */
export const EXAMPLE_VIEWER_POSTS: Post[] = [
  examplePost("p1", {
    title: "Why I switched to slower tools",
    teaser: "A year ago I ripped the automation out of my workflow.",
    body: "A year ago I ripped the automation out of my workflow. Here's what it cost me, what it gave back, and the one thing I'd never do again — no membership needed for this one.",
    published_at: "2026-06-04T09:00:00Z",
    access: { allowed: true, reason: "public", required_tier: null },
  }),
  examplePost("p2", {
    title: "Studio journal · week 22",
    teaser:
      "Three small breakthroughs and one expensive mistake. The glaze finally behaved, but only after…",
    body: null,
    published_at: "2026-06-02T09:00:00Z",
    access: {
      allowed: false,
      reason: "no_membership",
      required_tier: FREE_TIER,
    },
  }),
  examplePost("p3", {
    title: "Full glaze recipe + firing schedule",
    teaser:
      "The exact percentages, the kiln ramp, and the cooling curve I use for the speckled matte. Numbers and all…",
    body: null,
    published_at: "2026-05-30T09:00:00Z",
    access: {
      allowed: false,
      reason: "no_membership",
      required_tier: INSIDER_TIER,
    },
  }),
  examplePost("p4", {
    title: "Q&A — ask me anything about wood firing",
    teaser: "You asked, I answered. The long-burning questions first…",
    body: "You asked, I answered. The long-burning questions first: yes, the ash glaze is intentional; no, I won't sell the chamber kiln; and the full story about the cracked shelf is below.",
    published_at: "2026-05-26T09:00:00Z",
    access: {
      allowed: true,
      reason: "member_ok",
      required_tier: SUPPORTER_TIER,
    },
  }),
  examplePost("p5", {
    title: "Workshop tour — every station, every tool",
    teaser: "A room-by-room walkthrough of the studio, with sources…",
    body: null,
    published_at: "2026-05-22T09:00:00Z",
    access: {
      allowed: false,
      reason: "tier_too_low",
      required_tier: INSIDER_TIER,
    },
  }),
  examplePost("p6", {
    title: "The pricing letter",
    teaser:
      "What handmade work actually costs, and why I stopped apologizing for it…",
    body: null,
    published_at: "2026-05-18T09:00:00Z",
    access: {
      allowed: false,
      reason: "membership_expired",
      required_tier: SUPPORTER_TIER,
    },
  }),
];

/** What the owner sees: everything unlocked (`creator`), drafts included. */
export const EXAMPLE_OWNER_POSTS: Post[] = [
  examplePost("p7", {
    title: "Kiln rebuild — part one",
    teaser: "Tearing the old kiln down to the brick.",
    body: "Tearing the old kiln down to the brick. Only you can see this while it's a draft — publish to add it to the feed.",
    published_at: null,
    access: { allowed: true, reason: "creator", required_tier: INSIDER_TIER },
  }),
  examplePost("p8", {
    title: "Full glaze recipe + firing schedule",
    teaser: "The exact percentages, the kiln ramp, and the cooling curve…",
    body: "The exact percentages, the kiln ramp, and the cooling curve I use for the speckled matte. As the owner you always see the full body, regardless of the required tier.",
    published_at: "2026-05-30T09:00:00Z",
    access: { allowed: true, reason: "creator", required_tier: INSIDER_TIER },
  }),
  examplePost("p9", {
    title: "Why I switched to slower tools",
    teaser: "A year ago I ripped the automation out of my workflow.",
    body: "A year ago I ripped the automation out of my workflow. Here's what it cost me, what it gave back, and the one thing I'd never do again.",
    published_at: "2026-06-04T09:00:00Z",
    access: { allowed: true, reason: "creator", required_tier: null },
  }),
];
