/** A creator the signed-in user supports, as shown on the home page. */
export interface Membership {
  /** Creator's handle, without the leading `@`; routes to `/c/{handle}`. */
  handle: string;
  /** Creator's display name. */
  creatorName: string;
  /** The user's current tier on this creator (e.g. "Insider", "Free"). */
  tier: string;
  /** Rank of the current tier; 0 is the free tier. Drives the tier pill color. */
  tierRank: number;
}
