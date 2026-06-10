"use client";

import BrandLoader from "@/components/brand/BrandLoader";
import CreatorOwnerView from "@/components/creator/CreatorOwnerView";
import CreatorViewerView from "@/components/creator/CreatorViewerView";
import HomeShell from "@/components/home/HomeShell";
import { useCurrentUser } from "@/lib/hooks/useCurrentUser";
import { useMemberships } from "@/lib/hooks/useMemberships";
import type { Tier } from "@/types/tier";
import type { PublicUser } from "@/types/user";

/**
 * Renders a creator page, adapting to the viewer:
 * - signed out → the public viewer view as a standalone page (no app sidebar);
 * - signed in, owner → the manageable owner view inside the app shell;
 * - signed in, other → the viewer view inside the app shell, with the tier
 *   they hold on this creator (if any) marked in the Memberships tab.
 *
 * The current user is loaded client-side (cookie auth), so this gating — and
 * the owner check — live here rather than in the server page.
 */
export default function CreatorView({
  creator,
  tiers,
}: {
  creator: PublicUser;
  tiers: Tier[];
}) {
  const { user, loading } = useCurrentUser();
  const { memberships, loading: membershipsLoading } = useMemberships();

  if (loading || membershipsLoading) {
    return <BrandLoader />;
  }

  // The viewer's active membership with this creator, if they hold one.
  const heldTierId =
    memberships.find((m) => m.creator_id === creator.id && m.active)?.tier.id ??
    null;

  // Signed out: keep it public — show the creator page on its own, no sidebar.
  if (!user) {
    return (
      <main className="min-h-dvh px-6 py-10">
        <CreatorViewerView creator={creator} tiers={tiers} />
      </main>
    );
  }

  // Signed in: wrap in the app shell, owner or viewer view.
  const isOwner = user.id === creator.id;

  return (
    <HomeShell user={user}>
      {isOwner ? (
        <CreatorOwnerView creator={creator} tiers={tiers} />
      ) : (
        <CreatorViewerView
          creator={creator}
          tiers={tiers}
          heldTierId={heldTierId}
        />
      )}
    </HomeShell>
  );
}
