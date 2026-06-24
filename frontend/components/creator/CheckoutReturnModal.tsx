"use client";

import CheckIcon from "@/components/svg/CheckIcon";
import Modal from "@/components/ui/Modal";
import type { CheckoutReturnStatus } from "@/lib/hooks/useCheckoutReturn";

const NOOP = () => {};

/**
 * The return from Stripe Checkout, as a modal. While the webhook provisions the
 * membership it shows a spinner with loading text; the moment the membership
 * goes active it morphs in place into a congratulatory confirmation. The
 * canceled return gets its own brief note. Driven by {@link useCheckoutReturn};
 * renders nothing when idle.
 */
export default function CheckoutReturnModal({
  status,
  onDismiss,
}: {
  status: CheckoutReturnStatus;
  onDismiss: () => void;
}) {
  const finalizing = status === "finalizing";

  return (
    <Modal
      open={status !== "idle"}
      // The loading state resolves on its own — don't let it be dismissed.
      onClose={finalizing ? NOOP : onDismiss}
      labelledBy="checkout-return-title"
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
              id="checkout-return-title"
              className="text-lg font-semibold tracking-tight"
            >
              Completing your subscription
            </h2>
            <p className="text-muted text-sm">
              Hang tight while we confirm your payment…
            </p>
          </>
        ) : status === "success" ? (
          <>
            <span
              aria-hidden
              className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400"
            >
              <CheckIcon className="h-6 w-6" />
            </span>
            <h2
              id="checkout-return-title"
              className="text-lg font-semibold tracking-tight"
            >
              You&apos;re subscribed! 🎉
            </h2>
            <p className="text-muted text-sm">
              Your membership is active — enjoy the perks.
            </p>
            <button
              type="button"
              onClick={onDismiss}
              className="bg-foreground text-background inline-flex h-9 cursor-pointer items-center rounded-full px-5 text-sm font-medium transition-opacity hover:opacity-90"
            >
              Done
            </button>
          </>
        ) : (
          <>
            <h2
              id="checkout-return-title"
              className="text-lg font-semibold tracking-tight"
            >
              Checkout canceled
            </h2>
            <p className="text-muted text-sm">
              No charge was made — you can subscribe any time.
            </p>
            <button
              type="button"
              onClick={onDismiss}
              className="border-border text-foreground hover:bg-foreground/5 inline-flex h-9 cursor-pointer items-center rounded-full border px-5 text-sm font-medium transition-colors"
            >
              Close
            </button>
          </>
        )}
      </div>
    </Modal>
  );
}
