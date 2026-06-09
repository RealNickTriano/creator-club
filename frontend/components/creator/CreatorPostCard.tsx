import PostBadge from "@/components/creator/PostBadge";
import type { CreatorPost } from "@/types/creator";

const SMALL_BTN =
  "border-border text-foreground hover:bg-foreground/5 inline-flex h-8 cursor-pointer items-center rounded-full border px-3 text-xs font-medium transition-colors";
const SMALL_BTN_PRIMARY =
  "bg-foreground text-background inline-flex h-8 cursor-pointer items-center rounded-full px-3 text-xs font-medium transition-opacity hover:opacity-90";

/**
 * One post in the owner's feed. The owner always sees the full body (no lock),
 * including drafts, with edit/delete (or publish) controls.
 */
export default function CreatorPostCard({ post }: { post: CreatorPost }) {
  const isDraft = post.publishedAt === null;
  const dateLabel = post.publishedAt
    ? new Date(post.publishedAt).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      })
    : "Not published";

  return (
    <article className="border-border bg-background rounded-xl border p-4">
      <div className="flex items-center gap-2">
        <h3 className="text-foreground min-w-0 flex-1 truncate text-base font-semibold tracking-tight">
          {post.title}
        </h3>
        {isDraft && <PostBadge tone="draft">Draft</PostBadge>}
        {post.requiredTier ? (
          <PostBadge tone="members">{post.requiredTier}</PostBadge>
        ) : (
          <PostBadge tone="public">Public</PostBadge>
        )}
      </div>
      <p className="text-muted mt-1 text-xs">{dateLabel}</p>
      <p className="text-foreground-soft mt-2 text-sm">{post.body}</p>

      <div className="mt-3 flex gap-2">
        <button type="button" className={SMALL_BTN}>
          Edit
        </button>
        {isDraft ? (
          <button type="button" className={SMALL_BTN_PRIMARY}>
            Publish
          </button>
        ) : (
          <button type="button" className={SMALL_BTN}>
            Delete
          </button>
        )}
      </div>
    </article>
  );
}
