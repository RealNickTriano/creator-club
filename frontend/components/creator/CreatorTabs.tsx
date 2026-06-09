"use client";

import { useState } from "react";
import CreatorMembershipsList from "@/components/creator/CreatorMembershipsList";
import CreatorPostList from "@/components/creator/CreatorPostList";
import CreatorProfileForm from "@/components/creator/CreatorProfileForm";
import CreatorViewerPostCard from "@/components/creator/CreatorViewerPostCard";
import type { CreatorPost } from "@/types/creator";
import type { Tier } from "@/types/tier";
import type { PublicUser } from "@/types/user";

const TABS = ["Posts", "Memberships", "Profile"] as const;
type Tab = (typeof TABS)[number];

const VIEWER_TABS: readonly Tab[] = ["Posts", "Memberships"];

/**
 * The creator page's tab switcher, shared by both audiences: "Posts" shows the
 * feed, "Memberships" the tier list. With `isOwner` the posts are manageable
 * (drafts included), the tiers gain edit/add controls, and a "Profile" tab
 * holds the profile editor; viewers get the published feed and read-only
 * tiers. Holds its own active-tab state client-side.
 */
export default function CreatorTabs({
  creator,
  posts,
  tiers,
  isOwner,
}: {
  creator: PublicUser;
  posts: CreatorPost[];
  tiers: Tier[];
  isOwner: boolean;
}) {
  const [active, setActive] = useState<Tab>("Posts");
  const tabs = isOwner ? TABS : VIEWER_TABS;
  // Drafts are owner-only; viewers see the published feed.
  const visiblePosts = isOwner
    ? posts
    : posts.filter((post) => post.publishedAt !== null);

  return (
    <div>
      <div
        role="tablist"
        aria-label="Creator sections"
        className="border-border flex gap-6 border-b"
      >
        {tabs.map((tab) => {
          const selected = tab === active;
          return (
            <button
              key={tab}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => setActive(tab)}
              className={`-mb-px cursor-pointer border-b-2 px-1 pb-3 text-sm font-medium transition-colors ${
                selected
                  ? "border-foreground text-foreground"
                  : "text-muted hover:text-foreground border-transparent"
              }`}
            >
              {tab}
            </button>
          );
        })}
      </div>

      <div role="tabpanel" className="mt-5">
        {active === "Posts" &&
          (isOwner ? (
            <CreatorPostList posts={visiblePosts} />
          ) : (
            <div className="space-y-3">
              {visiblePosts.map((post) => (
                <CreatorViewerPostCard key={post.id} post={post} />
              ))}
            </div>
          ))}
        {active === "Memberships" && (
          <CreatorMembershipsList tiers={tiers} canManage={isOwner} />
        )}
        {active === "Profile" && isOwner && (
          <CreatorProfileForm creator={creator} />
        )}
      </div>
    </div>
  );
}
