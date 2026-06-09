import Link from "next/link";
import UsersIcon from "@/components/svg/UsersIcon";

/**
 * The memberships empty state (mockup B): shown when the signed-in user
 * doesn't support any creators yet, nudging them to find some.
 * {@link MembershipsSection} renders this in place of the grid.
 */
export default function MembershipsEmpty({
  findHref = "#",
}: {
  findHref?: string;
}) {
  return (
    <div className="border-border bg-background rounded-xl border border-dashed p-8 text-center">
      <span className="bg-foreground/5 mx-auto mb-3 inline-flex h-12 w-12 items-center justify-center rounded-full">
        <UsersIcon className="text-muted h-5 w-5" />
      </span>
      <b className="text-foreground block text-sm font-semibold">
        You haven&apos;t joined any creators yet
      </b>
      <p className="text-foreground-soft mx-auto mt-1.5 max-w-sm text-sm">
        When you join a creator, they&apos;ll show up here for quick access.
      </p>
      <Link
        href={findHref}
        className="bg-foreground text-background mt-4 inline-flex h-9 items-center rounded-full px-4 text-sm font-medium transition-opacity hover:opacity-90"
      >
        Find creators
      </Link>
    </div>
  );
}
