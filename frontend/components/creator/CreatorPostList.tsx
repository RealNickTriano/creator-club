"use client";

import { useState } from "react";
import DeletePostDialog from "@/components/creator/DeletePostDialog";
import PostCard from "@/components/creator/PostCard";
import { deletePost, updatePost } from "@/lib/api/posts";
import type { Post } from "@/types/post";

/**
 * The owner's manageable post list (the "Posts" and "Drafts" tabs), or an
 * empty-state nudge to compose one when there are none — pass `emptyTitle` /
 * `emptyHint` to fit the copy to what the list holds. Each card's Delete
 * opens {@link DeletePostDialog} to confirm, and Publish/Unpublish patches
 * `published_at` directly; either way `onPostsChange` fires after so the
 * parent refetches the feed (the post hops between the Posts and Drafts
 * tabs).
 */
export default function CreatorPostList({
  posts,
  onNewPost,
  onEditPost,
  onPostsChange,
  emptyTitle = "No posts yet",
  emptyHint = "Publish your first post to start sharing with members.",
}: {
  posts: Post[];
  /** Opens the new-post composer (the empty state's CTA). */
  onNewPost?: () => void;
  /** Opens the composer in edit mode on this post (each card's Edit). */
  onEditPost?: (post: Post) => void;
  /** Called after a post is deleted, to refetch the feed. */
  onPostsChange?: () => void;
  emptyTitle?: string;
  emptyHint?: string;
}) {
  const [deleting, setDeleting] = useState<Post | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState(false);
  // The post whose publish state is being flipped — locks that card's buttons.
  const [publishingId, setPublishingId] = useState<string | null>(null);
  const [publishError, setPublishError] = useState(false);

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

  async function setPublished(post: Post, published: boolean) {
    setPublishError(false);
    setPublishingId(post.id);
    try {
      await updatePost(post.id, {
        published_at: published ? new Date().toISOString() : null,
      });
      onPostsChange?.();
    } catch {
      setPublishError(true);
    } finally {
      setPublishingId(null);
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
      {publishError && (
        <p className="text-sm text-red-600 dark:text-red-400">
          Something went wrong — please try again.
        </p>
      )}
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          manageable
          busy={post.id === publishingId}
          onDelete={(target) => {
            setError(false);
            setDeleting(target);
          }}
          onEdit={onEditPost}
          onSetPublished={setPublished}
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
