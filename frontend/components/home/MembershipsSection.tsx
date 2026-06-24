import MembershipCard from "@/components/home/MembershipCard";
import MembershipsEmpty from "@/components/home/MembershipsEmpty";
import SectionHeading from "@/components/home/SectionHeading";
import type { Membership } from "@/types/membership";

/**
 * The "Your memberships" block: the creators the signed-in user supports, laid
 * out in a responsive grid (mockup A). Falls back to {@link MembershipsEmpty}
 * when they don't support anyone yet (mockup B).
 */
export default function MembershipsSection({
  memberships,
}: {
  memberships: Membership[];
}) {
  const hasMemberships = memberships.length > 0;

  return (
    <section className="mt-8">
      <SectionHeading title="Your memberships" />
      <div className="mt-3">
        {hasMemberships ? (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {memberships.map((membership) => (
              <MembershipCard key={membership.id} membership={membership} />
            ))}
          </div>
        ) : (
          <MembershipsEmpty />
        )}
      </div>
    </section>
  );
}
