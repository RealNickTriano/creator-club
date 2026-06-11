import LockIcon from "@/components/svg/LockIcon";
import { formatTierPrice } from "@/lib/utils/price";
import type { Tier } from "@/types/tier";
import type { PostAccess } from "@/types/post";

/** The lock panel's copy and call to action, derived from the access reason. */
function lockCopy(access: PostAccess, tier: Tier) {
  if (access.reason === "tier_too_low") {
    return {
      heading: `${tier.name} tier required`,
      detail: "Upgrade your membership to unlock this post.",
      cta: `Upgrade to ${tier.name}`,
    };
  }
  if (access.reason === "membership_expired") {
    return {
      heading: "Membership expired",
      detail: `Renew your membership to keep reading ${tier.name} posts.`,
      cta: "Renew",
    };
  }
  // no_membership — the CTA depends on whether the gate is the free tier.
  if (tier.price_cents === 0) {
    return {
      heading: "Free members only",
      detail: "Join the free tier to read the rest — no card required.",
      cta: "Join free",
    };
  }
  return {
    heading: `${tier.name} — ${formatTierPrice(tier.price_cents)}`,
    detail: `Subscribe to the ${tier.name} tier to unlock this post.`,
    cta: `Subscribe to ${tier.name}`,
  };
}

/**
 * The upsell strip at the bottom of a locked post card: a lock glyph, one line
 * naming what's required, and the single action that would unlock the post —
 * all derived from the backend's access decision, never re-derived here.
 */
export default function PostLockPanel({
  access,
  onUnlock,
}: {
  access: PostAccess;
  /** Called with the unlocking tier when the CTA is clicked. */
  onUnlock?: (tier: Tier) => void;
}) {
  const tier = access.required_tier;
  if (tier === null) return null;

  const { heading, detail, cta } = lockCopy(access, tier);

  return (
    <div className="border-border mt-3 flex items-center gap-3 border-t border-dashed pt-3">
      <span className="bg-foreground/5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full">
        <LockIcon className="text-muted h-4 w-4" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-foreground text-sm font-semibold">{heading}</p>
        <p className="text-muted text-xs">{detail}</p>
      </div>
      <button
        type="button"
        onClick={() => onUnlock?.(tier)}
        className="bg-foreground text-background inline-flex h-8 shrink-0 cursor-pointer items-center rounded-full px-3 text-xs font-medium transition-opacity hover:opacity-90"
      >
        {cta}
      </button>
    </div>
  );
}
