import PostBadge from "@/components/creator/PostBadge";
import PostLockPanel from "@/components/creator/PostLockPanel";
import type { Post } from "@/types/post";
import type { Tier } from "@/types/tier";

const SMALL_BTN =
  "border-border text-foreground hover:bg-foreground/5 inline-flex h-8 cursor-pointer items-center rounded-full border px-3 text-xs font-medium transition-colors";
const SMALL_BTN_PRIMARY =
  "bg-foreground text-background inline-flex h-8 cursor-pointer items-center rounded-full px-3 text-xs font-medium transition-opacity hover:opacity-90";
const SMALL_BTN_DANGER =
  "border-red-600/30 text-red-600 hover:bg-red-600/10 dark:border-red-400/30 dark:text-red-400 inline-flex h-8 cursor-pointer items-center rounded-full border px-3 text-xs font-medium transition-colors";

/**
 * One post, rendered however the backend decided: unlocked posts show the full
 * body; locked ones show the teaser fading into a lock panel whose call to
 * action follows `access.reason`. With `manageable` (the owner's own page) the
 * card adds edit/publish/delete controls and a Draft badge for unpublished
 * posts — the owner is always entitled, so manageable cards never lock.
 */
export default function PostCard({
  post,
  manageable = false,
  onUnlock,
}: {
  post: Post;
  /** Owner view: show the management actions and draft state. */
  manageable?: boolean;
  /** Called with the unlocking tier when a locked post's CTA is clicked. */
  onUnlock?: (tier: Tier) => void;
}) {
  const isDraft = post.published_at === null;
  const locked = !post.access.allowed;
  const dateLabel = post.published_at
    ? new Date(post.published_at).toLocaleDateString("en-US", {
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
        {manageable && isDraft && <PostBadge tone="draft">Draft</PostBadge>}
        {post.access.required_tier ? (
          <PostBadge tone="members">{post.access.required_tier.name}</PostBadge>
        ) : (
          <PostBadge tone="public">Public</PostBadge>
        )}
      </div>
      <p className="text-muted mt-1 text-xs">{dateLabel}</p>

      {locked ? (
        <>
          <p className="text-foreground-soft relative mt-2 text-sm">
            {post.teaser}
            {/* Fade the teaser out to hint there's more under the lock. */}
            <span
              aria-hidden
              className="to-background absolute inset-x-0 bottom-0 h-5 bg-linear-to-b from-transparent"
            />
          </p>
          <PostLockPanel access={post.access} onUnlock={onUnlock} />
        </>
      ) : (
        <p className="text-foreground-soft mt-2 text-sm">
          {post.body ?? post.teaser}
        </p>
      )}

      {manageable && (
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
              Unpublish
            </button>
          )}
          <button type="button" className={SMALL_BTN_DANGER}>
            Delete
          </button>
        </div>
      )}
    </article>
  );
}
