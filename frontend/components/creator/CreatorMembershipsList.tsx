"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import CreatorTiersEmpty from "@/components/creator/CreatorTiersEmpty";
import MembershipTierCard from "@/components/creator/MembershipTierCard";
import TierForm from "@/components/creator/TierForm";
import Modal from "@/components/ui/Modal";
import type { Tier } from "@/types/tier";

/**
 * The Memberships tab: each tier with its price. With `canManage` (the owner)
 * it adds edit / add-tier controls — or the {@link CreatorTiersEmpty} nudge
 * when there are no tiers yet. "Add tier" and "Edit" open the same
 * {@link TierForm} in a modal (blank or prefilled); on success the route is
 * refreshed so the server-fetched ladder picks up the change. Without
 * `canManage` (a viewer) the tiers render read-only, with `heldTierId`
 * marking the tier the viewer currently holds.
 */
export default function CreatorMembershipsList({
  tiers,
  canManage = false,
  heldTierId = null,
}: {
  tiers: Tier[];
  canManage?: boolean;
  heldTierId?: string | null;
}) {
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<Tier | null>(null);
  const router = useRouter();

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
        {tiers.map((tier) => (
          <MembershipTierCard
            key={tier.id}
            tier={tier}
            held={tier.id === heldTierId}
          />
        ))}
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
