"use client";

import Modal from "@/components/ui/Modal";
import type { Post } from "@/types/post";

/**
 * The confirmation step before deleting a post: names the post about to go
 * and warns it's permanent, with cancel / delete. Open whenever `post` is
 * set. While `pending` the buttons lock and the dialog can't be dismissed.
 */
export default function DeletePostDialog({
  post,
  pending,
  error,
  onConfirm,
  onClose,
}: {
  post: Post | null;
  pending: boolean;
  error: boolean;
  onConfirm: () => void;
  onClose: () => void;
}) {
  function close() {
    if (!pending) onClose();
  }

  return (
    <Modal
      open={post !== null}
      onClose={close}
      labelledBy="delete-post-title"
      maxWidth="max-w-md"
    >
      {post && (
        <div className="space-y-4">
          <h2
            id="delete-post-title"
            className="text-lg font-semibold tracking-tight"
          >
            Delete post
          </h2>

          <p className="text-foreground-soft text-sm">
            &ldquo;{post.title}&rdquo; will be permanently deleted. This
            can&apos;t be undone.
          </p>

          {error && (
            <p className="text-sm text-red-600 dark:text-red-400">
              Something went wrong — please try again.
            </p>
          )}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={close}
              disabled={pending}
              className="border-border text-foreground hover:bg-foreground/5 inline-flex h-9 cursor-pointer items-center rounded-full border px-4 text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={onConfirm}
              disabled={pending}
              className="inline-flex h-9 cursor-pointer items-center rounded-full bg-red-600 px-4 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:pointer-events-none disabled:opacity-50 dark:bg-red-500"
            >
              {pending ? "Deleting…" : "Delete post"}
            </button>
          </div>
        </div>
      )}
    </Modal>
  );
}
