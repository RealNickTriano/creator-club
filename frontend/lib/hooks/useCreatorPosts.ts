"use client";

import { useCallback, useEffect, useState } from "react";
import { getPostsByHandle, listMyDrafts } from "@/lib/api/posts";
import type { Post } from "@/types/post";

type CreatorPosts = {
  /** Drafts first (owner only), then the published feed, newest first. */
  posts: Post[];
  /** True during the initial load only — `refresh` updates in place. */
  loading: boolean;
  /** Set when the feed fails to load. */
  error: boolean;
  /** Refetch the feed, e.g. after the viewer joins or changes a tier. */
  refresh: () => void;
};

/**
 * Loads a creator's post feed from `GET /posts?handle=...` on mount. With
 * `includeDrafts` (the owner viewing their own page) the owner's drafts are
 * fetched too and prepended to the feed. Loaded client-side so the session
 * cookie rides along and the entitlements reflect the actual viewer.
 *
 * A `null` handle defers the fetch (`loading` stays true) — pass it while the
 * caller is still resolving who the viewer is. `posts` stays `[]` until
 * loaded (and on error).
 */
export function useCreatorPosts(
  handle: string | null,
  includeDrafts = false,
): CreatorPosts {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [generation, setGeneration] = useState(0);

  useEffect(() => {
    if (handle === null) return;
    let active = true;
    const requests: [Promise<Post[]>, Promise<Post[] | null>] = [
      includeDrafts ? listMyDrafts() : Promise.resolve([]),
      getPostsByHandle(handle),
    ];
    Promise.all(requests)
      .then(([drafts, feed]) => {
        if (active) {
          setPosts([...drafts, ...(feed ?? [])]);
          setError(false);
        }
      })
      .catch(() => {
        if (active) setError(true);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [handle, includeDrafts, generation]);

  const refresh = useCallback(() => setGeneration((g) => g + 1), []);

  return { posts, loading, error, refresh };
}
