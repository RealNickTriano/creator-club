"use client";

import { usePathname, useRouter } from "next/navigation";
import JoinTierDialog, {
  type JoinVerb,
} from "@/components/creator/JoinTierDialog";
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
  /** The tier the viewer holds on this creator, if any. */
  heldTierId?: string | null;
  /** Called after the viewer joins or changes tier, to refetch. */
  onMembershipChange?: () => void;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const join = useJoinTier(creatorId, onMembershipChange);
  // Signed-out viewers go sign in, then land back on this creator's page.
  const loginUrl = `/login?next=${encodeURIComponent(pathname)}`;

  // Rank of the viewer's held tier, deciding Upgrade vs Downgrade labels.
  const heldRank = tiers.find((tier) => tier.id === heldTierId)?.rank;

  function verbFor(tier: Tier): JoinVerb {
    if (heldRank === undefined) return "Join";
    return tier.rank > heldRank ? "Upgrade" : "Downgrade";
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
        onConfirm={join.confirm}
        onClose={join.close}
      />
    </div>
  );
}
