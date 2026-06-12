import PostCard from "@/components/creator/PostCard";
import type { Post } from "@/types/post";

/**
 * The owner's manageable post list (the "Posts" and "Drafts" tabs), or an
 * empty-state nudge to compose one when there are none — pass `emptyTitle` /
 * `emptyHint` to fit the copy to what the list holds.
 */
export default function CreatorPostList({
  posts,
  onNewPost,
  emptyTitle = "No posts yet",
  emptyHint = "Publish your first post to start sharing with members.",
}: {
  posts: Post[];
  /** Opens the new-post composer (the empty state's CTA). */
  onNewPost?: () => void;
  emptyTitle?: string;
  emptyHint?: string;
}) {
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
        <PostCard key={post.id} post={post} manageable />
      ))}
    </div>
  );
}
