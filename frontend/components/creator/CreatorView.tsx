"use client";

import BrandLoader from "@/components/brand/BrandLoader";
import CheckoutReturnModal from "@/components/creator/CheckoutReturnModal";
import CreatorOwnerView from "@/components/creator/CreatorOwnerView";
import CreatorViewerView from "@/components/creator/CreatorViewerView";
import HomeShell from "@/components/home/HomeShell";
import { useCheckoutReturn } from "@/lib/hooks/useCheckoutReturn";
import { useCreatorPosts } from "@/lib/hooks/useCreatorPosts";
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

  const isOwner = !loading && user?.id === creator.id;
  // Owner: include drafts. Held off until the user resolves so the feed isn't
  // fetched once without drafts and again with them.
  const {
    posts,
    loading: postsLoading,
    refresh: refreshPosts,
  } = useCreatorPosts(loading ? null : creator.handle, isOwner);

  // Handle the return from Stripe Checkout: poll until the webhook provisions
  // the membership, then refetch so the new tier's posts unlock.
  const checkout = useCheckoutReturn(creator.id, () => {
    refreshMemberships();
    refreshPosts();
  });
  const checkoutModal = (
    <CheckoutReturnModal
      status={checkout.status}
      onDismiss={checkout.dismiss}
    />
  );

  if (loading || membershipsLoading || postsLoading) {
    return (
      <>
        {checkoutModal}
        <BrandLoader />
      </>
    );
  }

  // The viewer's active membership with this creator, if they hold one.
  const heldTierId =
    memberships.find((m) => m.creator_id === creator.id && m.active)?.tier.id ??
    null;

  return (
    <HomeShell user={user}>
      {checkoutModal}
      {isOwner ? (
        <CreatorOwnerView
          creator={creator}
          posts={posts}
          tiers={tiers}
          onPostsChange={refreshPosts}
        />
      ) : (
        <CreatorViewerView
          creator={creator}
          posts={posts}
          tiers={tiers}
          heldTierId={heldTierId}
          canJoin={user !== null}
          onMembershipChange={() => {
            refreshMemberships();
            // A new or changed tier can unlock posts — refetch the feed too.
            refreshPosts();
          }}
        />
      )}
    </HomeShell>
  );
}
