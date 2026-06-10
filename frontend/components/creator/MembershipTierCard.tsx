import TierPill from "@/components/home/TierPill";
import { BRAND_GRADIENT } from "@/lib/brand";
import { formatTierPrice } from "@/lib/utils/price";
import type { Tier } from "@/types/tier";

/* The held card's brand-gradient border: the gradient fills the border box
   while the theme background covers the padding box, leaving only the border
   ring showing the gradient (theme-aware via `--background`). */
const HELD_BORDER_STYLE: React.CSSProperties = {
  backgroundImage: `linear-gradient(var(--background), var(--background)), ${BRAND_GRADIENT}`,
  backgroundOrigin: "border-box",
  backgroundClip: "padding-box, border-box",
};

/**
 * One tier in the Memberships tab: name, price, and description (when set).
 * Pass `onEdit` to show the owner's Edit control, which hands the tier back;
 * without it the card is read-only (the viewer side). `held` marks the tier
 * the viewer is currently subscribed to ("Your tier"), and `action` renders
 * the viewer's join/upgrade/downgrade button — the parent decides the label
 * and handles the call.
 */
export default function MembershipTierCard({
  tier,
  onEdit,
  held = false,
  action,
}: {
  tier: Tier;
  onEdit?: (tier: Tier) => void;
  held?: boolean;
  action?: { label: string; onClick: () => void; disabled?: boolean };
}) {
  return (
    <div
      className={`flex items-center gap-4 rounded-xl p-4 ${
        held
          ? "border-2 border-transparent"
          : "border-border bg-background border"
      }`}
      style={held ? HELD_BORDER_STYLE : undefined}
    >
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
      {held && <TierPill name="Your tier" rank={tier.rank} />}
      {action && (
        <button
          type="button"
          onClick={action.onClick}
          disabled={action.disabled}
          className="bg-foreground text-background inline-flex h-8 shrink-0 cursor-pointer items-center rounded-full px-3 text-xs font-medium transition-opacity hover:opacity-90 disabled:pointer-events-none disabled:opacity-50"
        >
          {action.label}
        </button>
      )}
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
