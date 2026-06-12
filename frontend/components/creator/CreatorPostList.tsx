"use client";

import { useState } from "react";
import DeletePostDialog from "@/components/creator/DeletePostDialog";
import PostCard from "@/components/creator/PostCard";
import { deletePost } from "@/lib/api/posts";
import type { Post } from "@/types/post";

/**
 * The owner's manageable post list (the "Posts" and "Drafts" tabs), or an
 * empty-state nudge to compose one when there are none — pass `emptyTitle` /
 * `emptyHint` to fit the copy to what the list holds. Each card's Delete
 * opens {@link DeletePostDialog} to confirm; a confirmed delete calls
 * `onPostsChange` so the parent refetches the feed.
 */
export default function CreatorPostList({
  posts,
  onNewPost,
  onPostsChange,
  emptyTitle = "No posts yet",
  emptyHint = "Publish your first post to start sharing with members.",
}: {
  posts: Post[];
  /** Opens the new-post composer (the empty state's CTA). */
  onNewPost?: () => void;
  /** Called after a post is deleted, to refetch the feed. */
  onPostsChange?: () => void;
  emptyTitle?: string;
  emptyHint?: string;
}) {
  const [deleting, setDeleting] = useState<Post | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState(false);

  async function confirmDelete() {
    if (!deleting) return;
    setError(false);
    setPending(true);
    try {
      await deletePost(deleting.id);
      setDeleting(null);
      onPostsChange?.();
    } catch {
      setError(true);
    } finally {
      setPending(false);
    }
  }

  if (posts.length === 0) {
    return (
      <div className="border-border bg-background rounded-xl border border-dashed p-8 text-center">
        <b className="text-foreground block text-sm font-semibold">
          {emptyTitle}
        </b>
        <p className="text-foreground-soft mx-auto mt-1.5 max-w-sm text-sm">
          {emptyHint}
        </p>
        <button
          type="button"
          onClick={onNewPost}
          className="bg-foreground text-background mt-4 inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-sm font-medium transition-opacity hover:opacity-90"
        >
          New post
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          manageable
          onDelete={(target) => {
            setError(false);
            setDeleting(target);
          }}
        />
      ))}
      <DeletePostDialog
        post={deleting}
        pending={pending}
        error={error}
        onConfirm={confirmDelete}
        onClose={() => setDeleting(null)}
      />
    </div>
  );
}
