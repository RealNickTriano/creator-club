"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ManagePaymentMethodsButton from "@/components/billing/ManagePaymentMethodsButton";
import SubscriptionCard from "@/components/billing/SubscriptionCard";
import SubscriptionsTable from "@/components/billing/SubscriptionsTable";
import BrandLoader from "@/components/brand/BrandLoader";
import BillingSubscriptionModal from "@/components/creator/BillingSubscriptionModal";
import HomeShell from "@/components/home/HomeShell";
import SectionHeading from "@/components/home/SectionHeading";
import CardIcon from "@/components/svg/CardIcon";
import { useCurrentUser } from "@/lib/hooks/useCurrentUser";
import { useMemberships } from "@/lib/hooks/useMemberships";
import { subscriptionStatus } from "@/lib/utils/subscriptionStatus";
import type { Membership } from "@/types/membership";

/**
 * The Billing page: a table of the signed-in user's active paid subscriptions —
 * creator, tier, monthly cost and renewal date. Clicking a row opens a modal to
 * upgrade, downgrade, or cancel that subscription. Free memberships aren't
 * billed, so they don't appear.
 */
export default function BillingPage() {
  const { user, loading, error } = useCurrentUser();
  const {
    memberships,
    loading: membershipsLoading,
    refresh,
  } = useMemberships();
  const router = useRouter();
  const [selected, setSelected] = useState<Membership | null>(null);

  // Bounce signed-out visitors (no session / 401) back to login.
  useEffect(() => {
    if (!loading && (error || !user)) router.replace("/login");
  }, [loading, error, user, router]);

  if (loading || !user || membershipsLoading) {
    return <BrandLoader />;
  }

  // Every membership on a priced tier is a subscription — active or ended;
  // free tiers cost nothing, so there's no billing to show for them. Grouped by
  // status (healthy first, ended last), then most recent period end first.
  const subscriptions = memberships
    .filter((m) => m.tier.price_cents > 0)
    .sort((a, b) => {
      const byStatus = subscriptionStatus(a).rank - subscriptionStatus(b).rank;
      if (byStatus !== 0) return byStatus;
      return (
        new Date(b.current_period_end ?? 0).getTime() -
        new Date(a.current_period_end ?? 0).getTime()
      );
    });

  return (
    <HomeShell user={user}>
      <div className="mx-auto max-w-3xl">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Billing</h1>
            <p className="text-muted mt-1 text-sm">
              Your subscriptions — select one to upgrade, downgrade, or cancel.
            </p>
          </div>
          {subscriptions.length > 0 && <ManagePaymentMethodsButton />}
        </header>

        <section className="mt-8">
          <SectionHeading title="Subscriptions" />
          <div className="mt-3">
            {subscriptions.length > 0 ? (
              <>
                {/* Wide table on tablet/desktop; stacked cards on mobile so the
                    list never needs a horizontal scroll. */}
                <div className="hidden md:block">
                  <SubscriptionsTable
                    subscriptions={subscriptions}
                    onSelect={setSelected}
                  />
                </div>
                <div className="space-y-3 md:hidden">
                  {subscriptions.map((membership) => (
                    <SubscriptionCard
                      key={membership.id}
                      membership={membership}
                      onSelect={setSelected}
                    />
                  ))}
                </div>
              </>
            ) : (
              <div className="border-border bg-background rounded-xl border border-dashed p-8 text-center">
                <span className="bg-foreground/5 mx-auto mb-3 inline-flex h-12 w-12 items-center justify-center rounded-full">
                  <CardIcon className="text-muted h-5 w-5" />
                </span>
                <b className="text-foreground block text-sm font-semibold">
                  No subscriptions yet
                </b>
                <p className="text-foreground-soft mx-auto mt-1.5 max-w-sm text-sm">
                  When you subscribe to a creator&apos;s paid tier, it&apos;ll
                  show up here.
                </p>
              </div>
            )}
          </div>
        </section>
      </div>

      <BillingSubscriptionModal
        membership={selected}
        onClose={() => setSelected(null)}
        onChanged={() => {
          setSelected(null);
          refresh();
        }}
      />
    </HomeShell>
  );
}
