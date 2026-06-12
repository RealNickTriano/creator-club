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
 * Fields to create a post via `POST /posts` — always created as a draft;
 * publish by patching `published_at`. `required_tier_id: null` makes the post
 * public; otherwise it must be one of the author's own tiers.
 */
export interface NewPost {
  title: string;
  teaser: string;
  body: string;
  required_tier_id: string | null;
}

/**
 * Author-editable fields for `PATCH /posts/{id}` — omitted fields are left
 * unchanged. Setting `published_at` publishes a draft; nulling it reverts to
 * draft. Likewise `required_tier_id: null` makes the post public.
 */
export interface UpdatePost {
  title?: string;
  teaser?: string;
  body?: string;
  required_tier_id?: string | null;
  published_at?: string | null;
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
