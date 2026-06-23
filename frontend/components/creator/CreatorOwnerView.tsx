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
 * editor. Shown when the signed-in user is this creator. Owns the post
 * composer modal — blank from the header's "New post" or the empty feed's
 * nudge, prefilled from a card's Edit; a saved post closes it and fires
 * `onPostsChange` so the feed refetches.
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
  /** Called after a post is created, edited, or deleted, to refetch the feed. */
  onPostsChange?: () => void;
}) {
  const [composing, setComposing] = useState(false);
  const [editing, setEditing] = useState<Post | null>(null);

  function closeComposer() {
    setComposing(false);
    setEditing(null);
  }

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
          onEditPost={setEditing}
          onPostsChange={onPostsChange}
        />
      </div>
      <Modal
        open={composing || editing !== null}
        onClose={closeComposer}
        labelledBy="post-form-title"
        maxWidth="max-w-lg"
      >
        <PostForm
          key={editing?.id ?? "new"}
          post={editing ?? undefined}
          tiers={tiers}
          onSaved={() => {
            closeComposer();
            onPostsChange?.();
          }}
          onCancel={closeComposer}
        />
      </Modal>
    </div>
  );
}
