"use client";

import UserAvatar from "@/components/auth/UserAvatar";
import SubscriptionStatusBadge from "@/components/creator/SubscriptionStatusBadge";
import TierPill from "@/components/home/TierPill";
import { displayName } from "@/lib/utils/names";
import { formatPrice } from "@/lib/utils/price";
import { renewalDate } from "@/lib/utils/renewalDate";
import type { Membership } from "@/types/membership";

/**
 * One subscription as a stacked card — the mobile counterpart to a
 * {@link SubscriptionsTable} row, so the billing list never needs a horizontal
 * scroll on narrow screens. Selecting it opens the same manage modal.
 */
export default function SubscriptionCard({
  membership,
  onSelect,
}: {
  membership: Membership;
  onSelect: (membership: Membership) => void;
}) {
  const { creator, tier } = membership;
  const name =
    displayName(creator) ?? (creator.handle ? `@${creator.handle}` : "Creator");

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => onSelect(membership)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(membership);
        }
      }}
      className="border-border hover:bg-foreground/5 focus-visible:bg-foreground/5 cursor-pointer rounded-xl border p-4 transition-colors focus-visible:outline-none"
    >
      <div className="flex items-start justify-between gap-3">
        <span className="flex min-w-0 items-center gap-3">
          <UserAvatar user={creator} size={36} />
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
        <SubscriptionStatusBadge membership={membership} />
      </div>

      <div className="mt-3 flex items-center justify-between gap-3 text-sm">
        <TierPill name={tier.name} rank={tier.rank} />
        <span className="text-foreground whitespace-nowrap">
          {formatPrice(tier.price_cents)} / mo
        </span>
      </div>

      <p className="text-foreground-soft mt-2 text-right text-xs">
        {renewalDate(membership.current_period_end)}
      </p>
    </div>
  );
}
