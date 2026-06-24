import type { Membership } from "@/types/membership";

export type SubscriptionStatusKey =
  | "active"
  | "trial"
  | "past_due"
  | "canceling"
  | "ended";

export interface SubscriptionStatus {
  key: SubscriptionStatusKey;
  label: string;
  /** Sort order for the billing table — lower sorts first. */
  rank: number;
}

/**
 * The human-facing state of a subscription, derived from the membership. A
 * lapsed membership reads "Ended"; a scheduled cancellation reads "Canceling"
 * (still active until the period ends); otherwise we surface the Stripe status.
 * `rank` groups the billing table: subs needing attention (past due) first,
 * then healthy ones, ended last.
 */
export function subscriptionStatus(membership: Membership): SubscriptionStatus {
  if (!membership.active) {
    return { key: "ended", label: "Ended", rank: 4 };
  }
  if (membership.canceled_at) {
    return { key: "canceling", label: "Canceling", rank: 3 };
  }
  switch (membership.status) {
    case "past_due":
    case "unpaid":
      return { key: "past_due", label: "Past due", rank: 0 };
    case "trialing":
      return { key: "trial", label: "Trial", rank: 2 };
    default:
      return { key: "active", label: "Active", rank: 1 };
  }
}
