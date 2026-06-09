import PostBadge from "@/components/creator/PostBadge";
import type { CreatorPost } from "@/types/creator";

/**
 * One post as a visitor sees it: title, visibility badge, date, and body — no
 * owner controls. Entitlement-based locking (teaser + upsell for tiered posts)
 * comes later; for now the body is shown.
 */
export default function CreatorViewerPostCard({ post }: { post: CreatorPost }) {
  const dateLabel = post.publishedAt
    ? new Date(post.publishedAt).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      })
    : "";

  return (
    <article className="border-border bg-background rounded-xl border p-4">
      <div className="flex items-center gap-2">
        <h3 className="text-foreground min-w-0 flex-1 truncate text-base font-semibold tracking-tight">
          {post.title}
        </h3>
        {post.requiredTier ? (
          <PostBadge tone="members">{post.requiredTier}</PostBadge>
        ) : (
          <PostBadge tone="public">Public</PostBadge>
        )}
      </div>
      {dateLabel && <p className="text-muted mt-1 text-xs">{dateLabel}</p>}
      <p className="text-foreground-soft mt-2 text-sm">{post.body}</p>
    </article>
  );
}
