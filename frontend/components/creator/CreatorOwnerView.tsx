import CreatorHeader from "@/components/creator/CreatorHeader";
import CreatorOwnerTabs from "@/components/creator/CreatorOwnerTabs";
import { PLACEHOLDER_POSTS } from "@/lib/placeholders/creator";
import type { Tier } from "@/types/tier";
import type { PublicUser } from "@/types/user";

/**
 * The creator's own page: the header with owner controls, then tabs switching
 * between the manageable post feed and the membership tiers. Shown when the
 * signed-in user is this creator.
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
        <CreatorOwnerTabs posts={PLACEHOLDER_POSTS} tiers={tiers} />
      </div>
    </div>
  );
}
