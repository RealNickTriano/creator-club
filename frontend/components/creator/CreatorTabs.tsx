"use client";

import { useState } from "react";
import CreatorMembershipsList from "@/components/creator/CreatorMembershipsList";
import CreatorPostFeed from "@/components/creator/CreatorPostFeed";
import CreatorPostList from "@/components/creator/CreatorPostList";
import CreatorProfileForm from "@/components/creator/CreatorProfileForm";
import type { Post } from "@/types/post";
import type { Tier } from "@/types/tier";
import type { PublicUser } from "@/types/user";

const TABS = ["Posts", "Drafts", "Memberships", "Profile"] as const;
type Tab = (typeof TABS)[number];

const VIEWER_TABS: readonly Tab[] = ["Posts", "Memberships"];

/**
 * The creator page's tab switcher, shared by both audiences: "Posts" shows the
 * published feed, "Memberships" the tier list. With `isOwner` the posts are
 * manageable and two more tabs appear — "Drafts" (with a count chip) holding
 * the unpublished posts, and "Profile" with the profile editor; viewers get
 * the published feed and read-only tiers. Holds its own active-tab state
 * client-side.
 */
export default function CreatorTabs({
  creator,
  posts,
  tiers,
  isOwner,
  heldTierId = null,
  canJoin = false,
  onMembershipChange,
  onNewPost,
  onPostsChange,
}: {
  creator: PublicUser;
  posts: Post[];
  tiers: Tier[];
  isOwner: boolean;
  /** The tier the viewer holds on this creator, marked in the Memberships tab. */
  heldTierId?: string | null;
  /** Signed-in non-owner: tiers get join/upgrade/downgrade buttons. */
  canJoin?: boolean;
  /** Called after the viewer joins or changes tier, to refetch memberships. */
  onMembershipChange?: () => void;
  /** Owner: opens the new-post composer (the empty feed's nudge). */
  onNewPost?: () => void;
  /** Owner: called after a post is deleted, to refetch the feed. */
  onPostsChange?: () => void;
}) {
  const [active, setActive] = useState<Tab>("Posts");
  const tabs = isOwner ? TABS : VIEWER_TABS;
  // Everyone's Posts tab shows the published feed; the owner's drafts live in
  // their own tab (drafts never reach non-owners — see the Drafts panel).
  const published = posts.filter((post) => post.published_at !== null);
  const drafts = posts.filter((post) => post.published_at === null);

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
              className={`-mb-px flex cursor-pointer items-center gap-1.5 border-b-2 px-1 pb-3 text-sm font-medium transition-colors ${
                selected
                  ? "border-foreground text-foreground"
                  : "text-muted hover:text-foreground border-transparent"
              }`}
            >
              {tab}
              {tab === "Drafts" && (
                <span className="bg-foreground/10 text-foreground-soft rounded-full px-1.5 py-0.5 text-xs font-semibold tabular-nums">
                  {drafts.length}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div role="tabpanel" className="mt-5">
        {active === "Posts" &&
          (isOwner ? (
            <CreatorPostList
              posts={published}
              onNewPost={onNewPost}
              onPostsChange={onPostsChange}
            />
          ) : (
            <CreatorPostFeed
              posts={published}
              tiers={tiers}
              creatorId={canJoin ? creator.id : null}
              heldTierId={heldTierId}
              onMembershipChange={onMembershipChange}
            />
          ))}
        {active === "Drafts" && isOwner && (
          <CreatorPostList
            posts={drafts}
            onNewPost={onNewPost}
            onPostsChange={onPostsChange}
            emptyTitle="No drafts"
            emptyHint="Posts you save without publishing wait here, visible only to you."
          />
        )}
        {active === "Memberships" && (
          <CreatorMembershipsList
            tiers={tiers}
            canManage={isOwner}
            heldTierId={heldTierId}
            creatorId={canJoin ? creator.id : null}
            onMembershipChange={onMembershipChange}
          />
        )}
        {active === "Profile" && isOwner && (
          <CreatorProfileForm creator={creator} />
        )}
      </div>
    </div>
  );
}
