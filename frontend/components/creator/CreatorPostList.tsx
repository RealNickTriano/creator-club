import CreatorPostCard from "@/components/creator/CreatorPostCard";
import type { CreatorPost } from "@/types/creator";

/**
 * The owner's post feed (the "Posts" tab): a manageable list of posts, or an
 * empty-state nudge to publish the first one when there are none.
 */
export default function CreatorPostList({ posts }: { posts: CreatorPost[] }) {
  if (posts.length === 0) {
    return (
      <div className="border-border bg-background rounded-xl border border-dashed p-8 text-center">
        <b className="text-foreground block text-sm font-semibold">
          No posts yet
        </b>
        <p className="text-foreground-soft mx-auto mt-1.5 max-w-sm text-sm">
          Publish your first post to start sharing with members.
        </p>
        <button
          type="button"
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
        <CreatorPostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
