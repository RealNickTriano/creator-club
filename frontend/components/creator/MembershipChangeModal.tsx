"use client";

import CheckIcon from "@/components/svg/CheckIcon";
import Modal from "@/components/ui/Modal";
import type { ChangeStatus } from "@/lib/hooks/useJoinTier";
import type { Tier } from "@/types/tier";

const NOOP = () => {};

/**
 * The in-place tier change (upgrade / downgrade / free join), as a modal — the
 * in-app counterpart to {@link CheckoutReturnModal}. While the change settles it
 * shows a spinner; once the new tier is reflected it morphs into a
 * congratulatory confirmation naming the tier. Driven by {@link useJoinTier};
 * renders nothing when idle.
 */
export default function MembershipChangeModal({
  status,
  tier,
  onDismiss,
}: {
  status: ChangeStatus;
  tier: Tier | null;
  onDismiss: () => void;
}) {
  const finalizing = status === "finalizing";

  return (
    <Modal
      open={status !== "idle"}
      // The loading state resolves on its own — don't let it be dismissed.
      onClose={finalizing ? NOOP : onDismiss}
      labelledBy="membership-change-title"
      maxWidth="max-w-sm"
    >
      <div className="space-y-4 text-center">
        {finalizing ? (
          <>
            <span
              aria-hidden
              className="border-foreground/20 border-t-foreground mx-auto block h-9 w-9 animate-spin rounded-full border-[3px]"
            />
            <h2
              id="membership-change-title"
              className="text-lg font-semibold tracking-tight"
            >
              Updating your membership
            </h2>
            <p className="text-muted text-sm">
              Hang tight while we confirm the change…
            </p>
          </>
        ) : (
          <>
            <span
              aria-hidden
              className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400"
            >
              <CheckIcon className="h-6 w-6" />
            </span>
            <h2
              id="membership-change-title"
              className="text-lg font-semibold tracking-tight"
            >
              You&apos;re on {tier?.name} now 🎉
            </h2>
            <p className="text-muted text-sm">
              Your membership has been updated — enjoy the perks.
            </p>
            <button
              type="button"
              onClick={onDismiss}
              className="bg-foreground text-background inline-flex h-9 cursor-pointer items-center rounded-full px-5 text-sm font-medium transition-opacity hover:opacity-90"
            >
              Done
            </button>
          </>
        )}
      </div>
    </Modal>
  );
}
