import type { Tier } from "@/types/tier";
import type { PublicUser } from "@/types/user";

/**
 * A membership as returned by `GET /memberships` and `POST /memberships`:
 * the row fields with the held tier and the creator's public profile
 * embedded, plus the derived `active` status so clients never re-derive it.
 */
export interface Membership {
  id: string;
  member_id: string;
  creator_id: string;
  started_at: string;
  current_period_end: string | null;
  canceled_at: string | null;
  tier: Tier;
  creator: PublicUser;
  active: boolean;
}
