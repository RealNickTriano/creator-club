import Link from "next/link";
import UserAvatar from "@/components/auth/UserAvatar";
import TierPill from "@/components/home/TierPill";
import { displayName } from "@/lib/utils/names";
import type { Membership } from "@/types/membership";

/**
 * One creator the signed-in user supports, in the memberships grid (mockup A):
 * avatar, display name, `@handle` and current tier. The whole card links
 * through to the creator's page at `/c/{handle}`.
 * {@link MembershipsSection} lays these out in a responsive grid.
 */
export default function MembershipCard({
  membership,
}: {
  membership: Membership;
}) {
  const { creator, tier } = membership;
  const handle = creator.handle;
  const creatorName =
    displayName(creator) ?? (handle ? `@${handle}` : "Creator");

  return (
    <Link
      href={handle ? `/c/${handle}` : "#"}
      className="border-border bg-background hover:bg-foreground/5 flex items-center gap-3 rounded-xl border p-3.5 transition-colors"
    >
      <span className="shrink-0">
        <UserAvatar user={creator} size={40} />
      </span>
      <div className="min-w-0 flex-1">
        <b className="text-foreground block truncate text-sm font-semibold">
          {creatorName}
        </b>
        {handle && (
          <span className="text-muted block truncate text-xs">@{handle}</span>
        )}
        <div className="mt-1.5">
          <TierPill name={tier.name} rank={tier.rank} />
        </div>
      </div>
      <span aria-hidden="true" className="text-muted shrink-0 text-lg">
        ›
      </span>
    </Link>
  );
}
