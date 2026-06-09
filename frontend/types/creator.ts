/** A post in a creator's feed. */
export interface CreatorPost {
  id: string;
  title: string;
  body: string;
  /** Name of the minimum tier required to view, or `null` when public. */
  requiredTier: string | null;
  /** ISO publish date, or `null` for a draft (owner-only). */
  publishedAt: string | null;
}
