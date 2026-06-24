import {
  type SubscriptionStatusKey,
  subscriptionStatus,
} from "@/lib/utils/subscriptionStatus";
import type { Membership } from "@/types/membership";

const TONE: Record<SubscriptionStatusKey, string> = {
  active: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400",
  trial: "bg-sky-500/10 text-sky-700 dark:text-sky-400",
  past_due: "bg-red-500/10 text-red-700 dark:text-red-400",
  canceling: "bg-amber-500/10 text-amber-700 dark:text-amber-400",
  ended: "bg-foreground/10 text-muted",
};

/** A small colored pill showing a subscription's current state. */
export default function SubscriptionStatusBadge({
  membership,
}: {
  membership: Membership;
}) {
  const { key, label } = subscriptionStatus(membership);
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${TONE[key]}`}
    >
      {label}
    </span>
  );
}
