import { formatTierPrice } from "@/lib/utils/price";
import type { Tier } from "@/types/tier";

/**
 * One tier in the Memberships tab: name, price, and description (when set).
 * Pass `onEdit` to show the owner's Edit control, which hands the tier back;
 * without it the card is read-only (the viewer side).
 */
export default function MembershipTierCard({
  tier,
  onEdit,
}: {
  tier: Tier;
  onEdit?: (tier: Tier) => void;
}) {
  return (
    <div className="border-border bg-background flex items-center gap-4 rounded-xl border p-4">
      <div className="min-w-0 flex-1">
        <p className="flex items-baseline gap-2">
          <span className="text-muted text-xs">
            {formatTierPrice(tier.price_cents)}
          </span>
          <span className="text-foreground text-sm font-semibold">
            {tier.name}
          </span>
        </p>
        {tier.description && (
          <p className="text-foreground-soft mt-1.5 text-xs whitespace-pre-line">
            {tier.description}
          </p>
        )}
      </div>
      {onEdit && (
        <button
          type="button"
          onClick={() => onEdit(tier)}
          className="border-border text-foreground hover:bg-foreground/5 inline-flex h-8 cursor-pointer items-center rounded-full border px-3 text-xs font-medium transition-colors"
        >
          Edit
        </button>
      )}
    </div>
  );
}
