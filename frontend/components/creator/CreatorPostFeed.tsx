"use client";

import { usePathname, useRouter } from "next/navigation";
import JoinTierDialog, {
  type JoinVerb,
} from "@/components/creator/JoinTierDialog";
import MembershipChangeModal from "@/components/creator/MembershipChangeModal";
import PostCard from "@/components/creator/PostCard";
import { useJoinTier } from "@/lib/hooks/useJoinTier";
import type { Post } from "@/types/post";
import type { Tier } from "@/types/tier";

/**
 * The post feed as a visitor sees it: one {@link PostCard} per published
 * post, with each locked post's unlock CTA opening {@link JoinTierDialog} on
 * the required tier — the same confirm-then-join flow as the Memberships tab.
 * Signed-out viewers (`creatorId` null) are sent to the login page instead;
 * after a successful join `onMembershipChange` lets the parent refetch the
 * feed so the post unlocks in place.
 */
export default function CreatorPostFeed({
  posts,
  tiers,
  creatorId = null,
  heldTierId = null,
  onMembershipChange,
}: {
  posts: Post[];
  /** The creator's ladder — decides Join vs Upgrade/Downgrade labels. */
  tiers: Tier[];
  /** The creator to join when a CTA is clicked; null when signed out. */
  creatorId?: string | null;
  /** The tier the viewer holds on this creator, if any (active membership). */
  heldTierId?: string | null;
  /** Called after the viewer joins or changes tier, to refetch. */
  onMembershipChange?: () => void;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const join = useJoinTier(creatorId, onMembershipChange);
  // Signed-out viewers go sign in, then land back on this creator's page.
  const loginUrl = `/login?next=${encodeURIComponent(pathname)}`;

  // The viewer's held tier — `heldTierId` is the active membership, so a paid
  // held tier means a live subscription.
  const heldTier = tiers.find((tier) => tier.id === heldTierId);
  const heldRank = heldTier?.rank;
  const holdsPaidSub = (heldTier?.price_cents ?? 0) > 0;

  function verbFor(tier: Tier): JoinVerb {
    if (heldRank === undefined) return "Join";
    return tier.rank > heldRank ? "Upgrade" : "Downgrade";
  }

  // A paid target redirects to Checkout only for a first-time subscription; an
  // upgrade/downgrade from a live paid subscription is modified in place.
  function willRedirect(tier: Tier): boolean {
    return tier.price_cents > 0 && !holdsPaidSub;
  }

  if (posts.length === 0) {
    return (
      <div className="border-border bg-background rounded-xl border border-dashed p-8 text-center">
        <b className="text-foreground block text-sm font-semibold">
          No posts yet
        </b>
        <p className="text-foreground-soft mx-auto mt-1.5 max-w-sm text-sm">
          This creator hasn&apos;t published anything yet — check back soon.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          onUnlock={creatorId ? join.request : () => router.push(loginUrl)}
        />
      ))}
      <JoinTierDialog
        tier={join.confirming}
        verb={join.confirming ? verbFor(join.confirming) : "Join"}
        pending={join.pending}
        error={join.error}
        willRedirect={join.confirming ? willRedirect(join.confirming) : false}
        onConfirm={join.confirm}
        onClose={join.close}
      />
      <MembershipChangeModal
        status={join.status}
        tier={join.activeTier}
        onDismiss={join.dismiss}
      />
    </div>
  );
}
