"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import CreatorTiersEmpty from "@/components/creator/CreatorTiersEmpty";
import MembershipTierCard from "@/components/creator/MembershipTierCard";
import TierForm from "@/components/creator/TierForm";
import Modal from "@/components/ui/Modal";
import type { Tier } from "@/types/tier";

/**
 * The owner's Memberships tab: each tier with its price, plus edit / add-tier
 * controls — or the {@link CreatorTiersEmpty} nudge when there are no tiers
 * yet. "Add tier" and "Edit" open the same {@link TierForm} in a modal (blank
 * or prefilled); on success the route is refreshed so the server-fetched
 * ladder picks up the change.
 */
export default function CreatorMembershipsList({ tiers }: { tiers: Tier[] }) {
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
