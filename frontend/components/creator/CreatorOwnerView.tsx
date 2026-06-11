import CreatorHeader from "@/components/creator/CreatorHeader";
import CreatorTabs from "@/components/creator/CreatorTabs";
import { EXAMPLE_OWNER_POSTS } from "@/lib/placeholders/creator";
import type { Tier } from "@/types/tier";
import type { PublicUser } from "@/types/user";

/**
 * The creator's own page: the header with owner controls, then tabs switching
 * between the manageable post feed, the membership tiers, and the profile
 * editor. Shown when the signed-in user is this creator.
 */
export default function CreatorOwnerView({
  creator,
  tiers,
}: {
  creator: PublicUser;
  tiers: Tier[];
}) {
  return (
    <div className="mx-auto max-w-2xl">
      <CreatorHeader creator={creator} />
      <div className="mt-8">
        <CreatorTabs
          creator={creator}
          posts={EXAMPLE_OWNER_POSTS}
          tiers={tiers}
          isOwner
        />
      </div>
    </div>
  );
}
