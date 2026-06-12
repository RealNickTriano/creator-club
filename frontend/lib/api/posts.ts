import { apiFetch, ApiError } from "@/lib/api/client";
import type { NewPost, Post, UpdatePost } from "@/types/post";

/**
 * Creates a post (as a draft) authored by the signed-in user and returns it.
 * Rejects with a 400 `ApiError` when `required_tier_id` isn't one of the
 * author's own tiers.
 */
export function createPost(newPost: NewPost): Promise<Post> {
  return apiFetch<Post>("/posts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(newPost),
  });
}

/**
 * Updates one of the signed-in user's own posts and returns it — also how a
 * draft is published (set `published_at`) or reverted (null it).
 */
export function updatePost(postId: string, update: UpdatePost): Promise<Post> {
  return apiFetch<Post>(`/posts/${encodeURIComponent(postId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(update),
  });
}

/** Deletes one of the signed-in user's own posts, members' access included. */
export function deletePost(postId: string): Promise<void> {
  return apiFetch<void>(`/posts/${encodeURIComponent(postId)}`, {
    method: "DELETE",
  });
}

/**
 * Fetches a creator's published feed by handle, newest first, with the
 * current viewer's entitlement already applied per post (`body` is `null` on
 * locked posts). Returns `null` if no user has this handle — mirroring
 * `getUserByHandle` so callers can treat both lookups the same way.
 * `no-store` keeps the entitlements fresh per request.
 */
export async function getPostsByHandle(handle: string): Promise<Post[] | null> {
  try {
    return await apiFetch<Post[]>(
      `/posts?handle=${encodeURIComponent(handle)}`,
      { cache: "no-store" },
    );
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

/**
 * Fetches the signed-in user's own drafts, newest first, with full body.
 * Rejects with a 401 `ApiError` when not signed in.
 */
export function listMyDrafts(): Promise<Post[]> {
  return apiFetch<Post[]>("/posts/drafts", { cache: "no-store" });
}
