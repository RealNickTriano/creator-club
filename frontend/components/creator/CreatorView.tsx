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
 * Renders a creator page inside the app shell, adapting to the viewer:
 * - signed out → the public viewer view, with a "Log in" CTA in the sidebar;
 * - signed in, owner → the manageable owner view;
 * - signed in, other → the viewer view, with the tier they hold on this
 *   creator (if any) marked in the Memberships tab.
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
  const {
    memberships,
    loading: membershipsLoading,
    refresh: refreshMemberships,
  } = useMemberships();

  if (loading || membershipsLoading) {
    return <BrandLoader />;
  }

  // The viewer's active membership with this creator, if they hold one.
  const heldTierId =
    memberships.find((m) => m.creator_id === creator.id && m.active)?.tier.id ??
    null;

  const isOwner = user?.id === creator.id;

  return (
    <HomeShell user={user}>
      {isOwner ? (
        <CreatorOwnerView creator={creator} tiers={tiers} />
      ) : (
        <CreatorViewerView
          creator={creator}
          tiers={tiers}
          heldTierId={heldTierId}
          canJoin={user !== null}
          onMembershipChange={refreshMemberships}
        />
      )}
    </HomeShell>
  );
}
