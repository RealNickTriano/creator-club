"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import CreatorTiersEmpty from "@/components/creator/CreatorTiersEmpty";
import JoinTierDialog, {
  type JoinVerb,
} from "@/components/creator/JoinTierDialog";
import MembershipChangeModal from "@/components/creator/MembershipChangeModal";
import MembershipTierCard from "@/components/creator/MembershipTierCard";
import TierForm from "@/components/creator/TierForm";
import Modal from "@/components/ui/Modal";
import { useJoinTier } from "@/lib/hooks/useJoinTier";
import type { Tier } from "@/types/tier";

/**
 * The Memberships tab: each tier with its price. With `canManage` (the owner)
 * it adds edit / add-tier controls — or the {@link CreatorTiersEmpty} nudge
 * when there are no tiers yet. "Add tier" and "Edit" open the same
 * {@link TierForm} in a modal (blank or prefilled); on success the route is
 * refreshed so the server-fetched ladder picks up the change.
 *
 * Without `canManage` (a viewer) the tiers render read-only, with
 * `heldTierId` marking the tier the viewer currently holds. With `creatorId`
 * (a signed-in non-owner) each other tier gets a join / upgrade / downgrade
 * button, which opens {@link JoinTierDialog} to confirm before the call; a
 * successful change calls `onMembershipChange` so the parent can refetch the
 * viewer's memberships.
 */
export default function CreatorMembershipsList({
  tiers,
  canManage = false,
  heldTierId = null,
  creatorId = null,
  holdsPaidSubscription,
  onMembershipChange,
}: {
  tiers: Tier[];
  canManage?: boolean;
  heldTierId?: string | null;
  creatorId?: string | null;
  /** Whether the viewer holds an active paid subscription with this creator —
   * decides in-place change vs Checkout redirect, and whether free is reachable.
   * Defaults to "the held tier is paid"; pass explicitly when `heldTierId` may
   * point at an inactive membership (e.g. the Billing modal). */
  holdsPaidSubscription?: boolean;
  onMembershipChange?: () => void;
}) {
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<Tier | null>(null);
  const join = useJoinTier(creatorId, onMembershipChange);
  const router = useRouter();

  // The viewer's held tier — its rank decides Upgrade vs Downgrade labels.
  const heldTier = tiers.find((tier) => tier.id === heldTierId);
  const heldRank = heldTier?.rank;
  const holdsPaidSub =
    holdsPaidSubscription ?? (heldTier?.price_cents ?? 0) > 0;

  function verbFor(tier: Tier): JoinVerb {
    if (heldRank === undefined) return "Join";
    return tier.rank > heldRank ? "Upgrade" : "Downgrade";
  }

  // A paid target redirects to Checkout only for a first-time subscription; an
  // upgrade/downgrade from a live paid subscription is modified in place.
  function willRedirect(tier: Tier): boolean {
    return tier.price_cents > 0 && !holdsPaidSub;
  }

  // New tiers slot in above the current top rung.
  const nextRank =
    tiers.length === 0 ? 0 : Math.max(...tiers.map((tier) => tier.rank)) + 1;

  function closeForm() {
    setAdding(false);
    setEditing(null);
  }

  function onSaved() {
    closeForm();
    router.refresh();
  }

  if (!canManage) {
    return tiers.length === 0 ? (
      <div className="border-border bg-background rounded-xl border border-dashed p-8 text-center">
        <b className="text-foreground block text-sm font-semibold">
          No membership tiers yet
        </b>
        <p className="text-foreground-soft mx-auto mt-1.5 max-w-sm text-sm">
          This creator hasn&apos;t set up memberships yet — check back soon.
        </p>
      </div>
    ) : (
      <div className="space-y-3">
        {tiers.map((tier) => {
          const isHeld = tier.id === heldTierId;
          // On a paid tier, moving to free isn't a tier change — the fan must
          // cancel first (the API returns 409). Offer no button for it; the
          // free tier simply has no action while a paid tier is held.
          const cancelToGoFree =
            holdsPaidSub && !isHeld && tier.price_cents === 0;
          return (
            <MembershipTierCard
              key={tier.id}
              tier={tier}
              held={isHeld}
              action={
                creatorId && !isHeld && !cancelToGoFree
                  ? {
                      label:
                        verbFor(tier) === "Join" ? "Join Tier" : verbFor(tier),
                      onClick: () => join.request(tier),
                    }
                  : undefined
              }
            />
          );
        })}
        <JoinTierDialog
          tier={join.confirming}
          verb={join.confirming ? verbFor(join.confirming) : "Join"}
          pending={join.pending}
          error={join.error}
          willRedirect={join.confirming ? willRedirect(join.confirming) : false}
          onConfirm={join.confirm}
          onClose={join.close}
        />
        <MembershipChangeModal
          status={join.status}
          tier={join.activeTier}
          onDismiss={join.dismiss}
        />
      </div>
    );
  }

  return (
    <div>
      {tiers.length === 0 ? (
        <CreatorTiersEmpty onAddTier={() => setAdding(true)} />
      ) : (
        <>
          <div className="space-y-3">
            {tiers.map((tier) => (
              <MembershipTierCard
                key={tier.id}
                tier={tier}
                onEdit={setEditing}
              />
            ))}
          </div>
          <button
            type="button"
            onClick={() => setAdding(true)}
            className="border-border text-muted hover:border-foreground/30 hover:text-foreground mt-3 flex w-full cursor-pointer items-center justify-center rounded-xl border border-dashed p-4 text-sm font-medium transition-colors"
          >
            + Add tier
          </button>
        </>
      )}

      <Modal
        open={adding || editing !== null}
        onClose={closeForm}
        labelledBy="tier-form-title"
        maxWidth="max-w-lg"
      >
        <TierForm
          key={editing?.id ?? "new"}
          tier={editing ?? undefined}
          defaultRank={nextRank}
          onSaved={onSaved}
          onCancel={closeForm}
        />
      </Modal>
    </div>
  );
}
