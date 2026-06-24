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
  /** Stripe-mirrored status (active, trialing, past_due, …); null for free tiers. */
  status: string | null;
  tier: Tier;
  creator: PublicUser;
  active: boolean;
}

/**
 * Returned by `POST /memberships` for a **paid** tier instead of a `Membership`:
 * a Stripe Checkout URL to redirect the browser to. The membership itself is
 * created once payment completes (via the backend's Stripe webhook), so there's
 * no row to return yet.
 */
export interface CheckoutSession {
  checkout_url: string;
}
