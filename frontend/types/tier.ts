/**
 * One rung of a creator's membership ladder, as returned by `GET /tiers`.
 * `rank` orders the ladder (higher = more access); `price_cents: 0` marks a
 * free tier.
 */
export interface Tier {
  id: string;
  user_id: string;
  name: string;
  rank: number;
  price_cents: number;
  description: string | null;
  created_at: string;
  updated_at: string;
}

/** What a creator supplies to add a rung to their ladder (`POST /tiers`). */
export interface NewTier {
  name: string;
  rank: number;
  price_cents: number;
  description: string | null;
}

/**
 * Owner-editable fields for `PATCH /tiers/{tierId}` — omitted fields are left
 * unchanged.
 */
export type UpdateTier = Partial<NewTier>;
