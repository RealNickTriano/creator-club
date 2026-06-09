import CreatorIdentity from "@/components/creator/CreatorIdentity";
import CreatorTabs from "@/components/creator/CreatorTabs";
import { PLACEHOLDER_POSTS } from "@/lib/placeholders/creator";
import type { Tier } from "@/types/tier";
import type { PublicUser } from "@/types/user";

/**
 * The creator's page as seen by a visitor (non-owner): the identity header,
 * then the same tabs as the owner view minus the Profile tab — the published
 * post feed and the read-only tier list. No subscribe/membership controls and
 * no entitlement locking yet. Drafts are hidden from non-owners.
 */
export default function CreatorViewerView({
  creator,
  tiers,
}: {
  creator: PublicUser;
  tiers: Tier[];
}) {
  return (
    <div className="mx-auto max-w-2xl">
      <CreatorIdentity creator={creator} />
      <div className="mt-8">
        <CreatorTabs
          creator={creator}
          posts={PLACEHOLDER_POSTS}
          tiers={tiers}
          isOwner={false}
        />
      </div>
    </div>
  );
}
