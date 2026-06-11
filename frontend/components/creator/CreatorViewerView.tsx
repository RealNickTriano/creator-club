import CreatorIdentity from "@/components/creator/CreatorIdentity";
import CreatorTabs from "@/components/creator/CreatorTabs";
import { EXAMPLE_VIEWER_POSTS } from "@/lib/placeholders/creator";
import type { Tier } from "@/types/tier";
import type { PublicUser } from "@/types/user";

/**
 * The creator's page as seen by a visitor (non-owner): the identity header,
 * then the same tabs as the owner view minus the Profile tab — the
 * entitlement-aware post feed (locked posts show teaser + upsell) and the
 * tier list. Drafts are hidden from non-owners.
 */
export default function CreatorViewerView({
  creator,
  tiers,
  heldTierId = null,
  canJoin = false,
  onMembershipChange,
}: {
  creator: PublicUser;
  tiers: Tier[];
  /** The tier the viewer holds on this creator, marked in the Memberships tab. */
  heldTierId?: string | null;
  /** Signed-in non-owner: tiers get join/upgrade/downgrade buttons. */
  canJoin?: boolean;
  /** Called after the viewer joins or changes tier, to refetch memberships. */
  onMembershipChange?: () => void;
}) {
  return (
    <div className="mx-auto max-w-2xl">
      <CreatorIdentity creator={creator} />
      <div className="mt-8">
        <CreatorTabs
          creator={creator}
          posts={EXAMPLE_VIEWER_POSTS}
          tiers={tiers}
          isOwner={false}
          heldTierId={heldTierId}
          canJoin={canJoin}
          onMembershipChange={onMembershipChange}
        />
      </div>
    </div>
  );
}
