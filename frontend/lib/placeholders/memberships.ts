import type { Membership } from "@/types/membership";

/**
 * Stand-in memberships for the home page until the backend exposes the real
 * list. Mirrors mockup A in the `/home` design.
 *
 * TODO: replace with a `lib/api/memberships` call once that endpoint exists.
 */
export const PLACEHOLDER_MEMBERSHIPS: Membership[] = [
  {
    handle: "mayamakes",
    creatorName: "Maya Lin",
    tier: "Insider",
    tierRank: 3,
  },
  {
    handle: "longgame",
    creatorName: "The Long Game",
    tier: "All-Access",
    tierRank: 4,
  },
  {
    handle: "devdiaries",
    creatorName: "Dev Diaries",
    tier: "Free",
    tierRank: 0,
  },
  {
    handle: "quietstudio",
    creatorName: "Quiet Studio",
    tier: "Supporter",
    tierRank: 1,
  },
];
