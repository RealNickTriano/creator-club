import type { Tier } from "@/types/tier";

/** Why the viewer can (or can't) see a post's body — from the backend, verbatim. */
export type PostAccessReason =
  | "public"
  | "creator"
  | "member_ok"
  | "no_membership"
  | "membership_expired"
  | "tier_too_low";

/**
 * The entitlement decision for one viewer/post pair. `required_tier` is the
 * tier that would unlock the post (the upsell); `null` for public posts.
 */
export interface PostAccess {
  allowed: boolean;
  reason: PostAccessReason;
  required_tier: Tier | null;
}

/**
 * A post as the current viewer sees it (`GET /posts?handle=...`), entitlement
 * already applied: `teaser` is always present, `body` is `null` unless
 * `access.allowed`. `published_at: null` marks a draft (owner-only).
 */
export interface Post {
  id: string;
  user_id: string;
  title: string;
  teaser: string;
  body: string | null;
  required_tier_id: string | null;
  published_at: string | null;
  created_at: string;
  access: PostAccess;
}
