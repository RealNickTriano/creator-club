"use client";

import UserAvatar from "@/components/auth/UserAvatar";
import SubscriptionStatusBadge from "@/components/creator/SubscriptionStatusBadge";
import TierPill from "@/components/home/TierPill";
import { displayName } from "@/lib/utils/names";
import { formatPrice } from "@/lib/utils/price";
import { renewalDate } from "@/lib/utils/renewalDate";
import type { Membership } from "@/types/membership";

/**
 * The signed-in user's subscriptions as a five-column table — creator, tier,
 * cost, status and renewal. Wide by design, so the billing page only renders it
 * at `md` and up (mobile gets {@link SubscriptionCard}s instead). Selecting a
 * row opens the manage modal.
 */
export default function SubscriptionsTable({
  subscriptions,
  onSelect,
}: {
  subscriptions: Membership[];
  onSelect: (membership: Membership) => void;
}) {
  return (
    <div className="border-border overflow-hidden rounded-xl border">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-border text-muted border-b text-xs font-semibold tracking-wider uppercase">
            <th className="px-4 py-3">Creator</th>
            <th className="px-4 py-3">Tier</th>
            <th className="px-4 py-3">Cost / month</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Renews / ends</th>
          </tr>
        </thead>
        <tbody className="divide-border divide-y">
          {subscriptions.map((membership) => {
            const { creator, tier } = membership;
            const name =
              displayName(creator) ??
              (creator.handle ? `@${creator.handle}` : "Creator");
            return (
              <tr
                key={membership.id}
                role="button"
                tabIndex={0}
                onClick={() => onSelect(membership)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onSelect(membership);
                  }
                }}
                className="hover:bg-foreground/5 focus-visible:bg-foreground/5 cursor-pointer transition-colors focus-visible:outline-none"
              >
                <td className="px-4 py-3">
                  <span className="flex items-center gap-3">
                    <UserAvatar user={creator} size={32} />
                    <span className="min-w-0">
                      <b className="text-foreground block truncate font-semibold">
                        {name}
                      </b>
                      {creator.handle && (
                        <span className="text-muted block truncate text-xs">
                          @{creator.handle}
                        </span>
                      )}
                    </span>
                  </span>
                </td>
                <td className="px-4 py-3">
                  <TierPill name={tier.name} rank={tier.rank} />
                </td>
                <td className="text-foreground px-4 py-3 whitespace-nowrap">
                  {formatPrice(tier.price_cents)}
                </td>
                <td className="px-4 py-3">
                  <SubscriptionStatusBadge membership={membership} />
                </td>
                <td className="text-foreground-soft px-4 py-3 whitespace-nowrap">
                  {renewalDate(membership.current_period_end)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
