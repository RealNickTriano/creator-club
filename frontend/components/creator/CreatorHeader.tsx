import CreatorIdentity from "@/components/creator/CreatorIdentity";
import type { PublicUser } from "@/types/user";

/**
 * The owner's creator-page header: the shared {@link CreatorIdentity} block
 * plus the owner controls — New post. (Profile editing lives in the Profile
 * tab and tier management in the Memberships tab, see {@link CreatorTabs}.)
 */
export default function CreatorHeader({ creator }: { creator: PublicUser }) {
  return (
    <CreatorIdentity creator={creator} handleSuffix=" · this is your page">
      <button
        type="button"
        className="bg-foreground text-background inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-sm font-medium transition-opacity hover:opacity-90"
      >
        New post
      </button>
    </CreatorIdentity>
  );
}
