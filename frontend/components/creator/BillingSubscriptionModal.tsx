"use client";

import { useEffect, useState } from "react";
import UserAvatar from "@/components/auth/UserAvatar";
import CreatorMembershipsList from "@/components/creator/CreatorMembershipsList";
import Modal from "@/components/ui/Modal";
import { cancelMembership } from "@/lib/api/memberships";
import { getTiersByHandle } from "@/lib/api/tiers";
import { displayName } from "@/lib/utils/names";
import { renewalDate } from "@/lib/utils/renewalDate";
import type { Membership } from "@/types/membership";
import type { Tier } from "@/types/tier";

/**
 * Manage one subscription from the Billing page. Shows the creator's tier
 * ladder (reusing {@link CreatorMembershipsList} in viewer mode, so the held
 * tier is marked and the others get upgrade/downgrade buttons), plus a cancel
 * control. Open whenever `membership` is set; `onChanged` fires after a tier
 * change or cancellation so the page can refetch and close.
 */
export default function BillingSubscriptionModal({
  membership,
  onClose,
  onChanged,
}: {
  membership: Membership | null;
  onClose: () => void;
  onChanged: () => void;
}) {
  return (
    <Modal
      open={membership !== null}
      onClose={onClose}
      labelledBy="billing-sub-title"
      maxWidth="max-w-lg"
    >
      {membership && (
        // Keyed so each subscription gets fresh state (no effect resets).
        <SubscriptionManager
          key={membership.id}
          membership={membership}
          onChanged={onChanged}
        />
      )}
    </Modal>
  );
}

/** The modal body for a single subscription — its own fetch + cancel state. */
function SubscriptionManager({
  membership,
  onChanged,
}: {
  membership: Membership;
  onChanged: () => void;
}) {
  const handle = membership.creator.handle ?? null;
  const [tiers, setTiers] = useState<Tier[] | null>(handle ? null : []);
  const [confirmingCancel, setConfirmingCancel] = useState(false);
  const [canceling, setCanceling] = useState(false);
  const [cancelError, setCancelError] = useState(false);

  // Load the creator's ladder once on open (state is fresh per mount).
  useEffect(() => {
    if (!handle) return;
    let active = true;
    getTiersByHandle(handle)
      .then((loaded) => {
        if (active) setTiers(loaded ?? []);
      })
      .catch(() => {
        if (active) setTiers([]);
      });
    return () => {
      active = false;
    };
  }, [handle]);

  async function doCancel() {
    setCancelError(false);
    setCanceling(true);
    try {
      await cancelMembership(membership.creator_id);
      onChanged();
    } catch {
      setCancelError(true);
      setCanceling(false);
    }
  }

  return (
    <div className="space-y-5">
      <header className="flex items-center gap-3">
        <UserAvatar user={membership.creator} size={48} />
        <div className="min-w-0">
          <h2
            id="billing-sub-title"
            className="text-foreground truncate text-lg font-semibold tracking-tight"
          >
            {displayName(membership.creator) ?? "Creator"}
          </h2>
          {membership.creator.handle && (
            <p className="text-muted truncate text-sm">
              @{membership.creator.handle}
            </p>
          )}
        </div>
      </header>

      {tiers === null ? (
        <div className="flex justify-center py-6">
          <span
            aria-label="Loading tiers"
            className="border-foreground/20 border-t-foreground h-6 w-6 animate-spin rounded-full border-2"
          />
        </div>
      ) : (
        <CreatorMembershipsList
          tiers={tiers}
          heldTierId={membership.tier.id}
          creatorId={membership.creator_id}
          // This row may be an ended subscription, so derive "live paid" from
          // its status rather than letting the list infer it from the tier.
          holdsPaidSubscription={
            membership.active && membership.tier.price_cents > 0
          }
          onMembershipChange={onChanged}
        />
      )}

      <div className="border-border flex justify-center border-t pt-4">
        {!membership.active ? (
          <p className="text-muted text-sm">
            This membership ended on{" "}
            {renewalDate(membership.current_period_end)}. Pick a tier above to
            resubscribe.
          </p>
        ) : membership.canceled_at ? (
          <p className="text-muted text-sm">
            Your membership is set to end on{" "}
            {renewalDate(membership.current_period_end)}.
          </p>
        ) : confirmingCancel ? (
          <div className="space-y-3">
            <p className="text-foreground-soft text-sm text-center">
              Cancel your <b>{`${membership.tier.name} `}</b> membership? <br />{" "}
              You&apos;ll keep access until{" "}
              <b>{renewalDate(membership.current_period_end)}</b>
            </p>
            <div className="flex gap-2 justify-center">
              <button
                type="button"
                onClick={doCancel}
                disabled={canceling}
                className="inline-flex h-9 cursor-pointer items-center rounded-full bg-red-600 px-4 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:pointer-events-none disabled:opacity-50"
              >
                {canceling ? "Canceling…" : "Yes, cancel"}
              </button>
              <button
                type="button"
                onClick={() => setConfirmingCancel(false)}
                disabled={canceling}
                className="border-border text-foreground hover:bg-foreground/5 inline-flex h-9 cursor-pointer items-center rounded-full border px-4 text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50"
              >
                Keep membership
              </button>
            </div>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => setConfirmingCancel(true)}
            className="cursor-pointer text-sm font-medium text-red-600 hover:underline dark:text-red-400"
          >
            Cancel membership
          </button>
        )}
        {cancelError && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">
            Couldn&apos;t cancel — please try again.
          </p>
        )}
      </div>
    </div>
  );
}
