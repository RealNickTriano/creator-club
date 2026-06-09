import CreatorIdentity from "@/components/creator/CreatorIdentity";
import CreatorViewerPostCard from "@/components/creator/CreatorViewerPostCard";
import SectionHeading from "@/components/home/SectionHeading";
import { PLACEHOLDER_POSTS } from "@/lib/placeholders/creator";
import type { PublicUser } from "@/types/user";

/**
 * The creator's page as seen by a visitor (non-owner): the identity header and
 * the published post feed. Basic for now — no subscribe/membership controls and
 * no entitlement locking yet. Drafts are hidden from non-owners.
 */
export default function CreatorViewerView({
  creator,
}: {
  creator: PublicUser;
}) {
  const posts = PLACEHOLDER_POSTS.filter((post) => post.publishedAt !== null);

  return (
    <div className="mx-auto max-w-2xl">
      <CreatorIdentity creator={creator} />
      <div className="mt-8">
        <SectionHeading title="Posts" />
        <div className="mt-3 space-y-3">
          {posts.map((post) => (
            <CreatorViewerPostCard key={post.id} post={post} />
          ))}
        </div>
      </div>
    </div>
  );
}
