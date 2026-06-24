"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import UserAvatar from "@/components/auth/UserAvatar";
import BrandLoader from "@/components/brand/BrandLoader";
import HomeShell from "@/components/home/HomeShell";
import SectionHeading from "@/components/home/SectionHeading";
import TierPill from "@/components/home/TierPill";
import CardIcon from "@/components/svg/CardIcon";
import { useCurrentUser } from "@/lib/hooks/useCurrentUser";
import { useMemberships } from "@/lib/hooks/useMemberships";
import { displayName } from "@/lib/utils/names";
import { formatPrice } from "@/lib/utils/price";

/** An absolute renewal date, e.g. "Jul 8, 2026"; em dash when open-ended. */
function renewalDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/**
 * The Billing page: a table of the signed-in user's active paid subscriptions —
 * creator, tier, monthly cost and renewal date. Free memberships aren't billed,
 * so they don't appear.
 */
export default function BillingPage() {
  const { user, loading, error } = useCurrentUser();
  const { memberships, loading: membershipsLoading } = useMemberships();
  const router = useRouter();

  // Bounce signed-out visitors (no session / 401) back to login.
  useEffect(() => {
    if (!loading && (error || !user)) router.replace("/login");
  }, [loading, error, user, router]);

  if (loading || !user || membershipsLoading) {
    return <BrandLoader />;
  }

  // Subscriptions are active memberships on a priced tier; free tiers cost
  // nothing, so there's no billing to show for them.
  const subscriptions = memberships.filter(
    (m) => m.active && m.tier.price_cents > 0,
  );

  return (
    <HomeShell user={user}>
      <div className="mx-auto max-w-3xl">
        <header>
          <h1 className="text-2xl font-semibold tracking-tight">Billing</h1>
          <p className="text-muted mt-1 text-sm">
            Your active subscriptions and what they renew at.
          </p>
        </header>

        <section className="mt-8">
          <SectionHeading title="Subscriptions" />
          <div className="mt-3">
            {subscriptions.length > 0 ? (
              <div className="border-border overflow-x-auto rounded-xl border">
                <table className="w-full min-w-[34rem] text-left text-sm">
                  <thead>
                    <tr className="border-border text-muted border-b text-xs font-semibold tracking-wider uppercase">
                      <th className="px-4 py-3">Creator</th>
                      <th className="px-4 py-3">Tier</th>
                      <th className="px-4 py-3">Cost / month</th>
                      <th className="px-4 py-3">Renews</th>
                    </tr>
                  </thead>
                  <tbody className="divide-border divide-y">
                    {subscriptions.map((membership) => {
                      const { creator, tier } = membership;
                      const name =
                        displayName(creator) ??
                        (creator.handle ? `@${creator.handle}` : "Creator");
                      return (
                        <tr key={membership.id}>
                          <td className="px-4 py-3">
                            <Link
                              href={
                                creator.handle ? `/c/${creator.handle}` : "#"
                              }
                              className="group flex items-center gap-3"
                            >
                              <UserAvatar user={creator} size={32} />
                              <span className="min-w-0">
                                <b className="text-foreground group-hover:text-foreground block truncate font-semibold">
                                  {name}
                                </b>
                                {creator.handle && (
                                  <span className="text-muted block truncate text-xs">
                                    @{creator.handle}
                                  </span>
                                )}
                              </span>
                            </Link>
                          </td>
                          <td className="px-4 py-3">
                            <TierPill name={tier.name} rank={tier.rank} />
                          </td>
                          <td className="text-foreground px-4 py-3 whitespace-nowrap">
                            {formatPrice(tier.price_cents)}
                          </td>
                          <td className="text-foreground-soft px-4 py-3 whitespace-nowrap">
                            {renewalDate(membership.current_period_end)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="border-border bg-background rounded-xl border border-dashed p-8 text-center">
                <span className="bg-foreground/5 mx-auto mb-3 inline-flex h-12 w-12 items-center justify-center rounded-full">
                  <CardIcon className="text-muted h-5 w-5" />
                </span>
                <b className="text-foreground block text-sm font-semibold">
                  No active subscriptions
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
    </HomeShell>
  );
}
