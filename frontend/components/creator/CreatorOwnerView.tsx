"use client";

import { useState } from "react";
import CreatorHeader from "@/components/creator/CreatorHeader";
import CreatorTabs from "@/components/creator/CreatorTabs";
import PostForm from "@/components/creator/PostForm";
import Modal from "@/components/ui/Modal";
import type { Post } from "@/types/post";
import type { Tier } from "@/types/tier";
import type { PublicUser } from "@/types/user";

/**
 * The creator's own page: the header with owner controls, then tabs switching
 * between the published feed, drafts, the membership tiers, and the profile
 * editor. Shown when the signed-in user is this creator. Owns the "New post"
 * modal, opened from the header button or the empty feed's nudge; a saved
 * post closes it and fires `onPostsChange` so the feed refetches.
 */
export default function CreatorOwnerView({
  creator,
  posts,
  tiers,
  onPostsChange,
}: {
  creator: PublicUser;
  /** The owner's full feed: drafts included, everything unlocked. */
  posts: Post[];
  tiers: Tier[];
  /** Called after a post is created or deleted, to refetch the feed. */
  onPostsChange?: () => void;
}) {
  const [composing, setComposing] = useState(false);

  return (
    <div className="mx-auto max-w-2xl">
      <CreatorHeader creator={creator} onNewPost={() => setComposing(true)} />
      <div className="mt-8">
        <CreatorTabs
          creator={creator}
          posts={posts}
          tiers={tiers}
          isOwner
          onNewPost={() => setComposing(true)}
          onPostsChange={onPostsChange}
        />
      </div>
      <Modal
        open={composing}
        onClose={() => setComposing(false)}
        labelledBy="post-form-title"
        maxWidth="max-w-lg"
      >
        <PostForm
          tiers={tiers}
          onSaved={() => {
            setComposing(false);
            onPostsChange?.();
          }}
          onCancel={() => setComposing(false)}
        />
      </Modal>
    </div>
  );
}
