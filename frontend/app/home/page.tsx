"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import BrandLoader from "@/components/brand/BrandLoader";
import CreatorPageSection from "@/components/home/CreatorPageSection";
import HomeGreeting from "@/components/home/HomeGreeting";
import HomeShell from "@/components/home/HomeShell";
import MembershipsSection from "@/components/home/MembershipsSection";
import { useCurrentUser } from "@/lib/hooks/useCurrentUser";
import { useMemberships } from "@/lib/hooks/useMemberships";
import { displayName } from "@/lib/utils/names";

export default function HomePage() {
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

  // The home grid shows the creators they currently support; canceled and
  // expired memberships stay out of it (they resurface as a resume path on
  // the creator's own page).
  const activeMemberships = memberships.filter((m) => m.active);

  // The greeting addresses the user personally (personal_name), not by the
  // public display name others see.
  const greetingName = user.personal_name ?? displayName(user) ?? "there";
  const firstName = greetingName.split(" ")[0];

  return (
    <HomeShell user={user}>
      <div className="mx-auto max-w-3xl">
        <HomeGreeting name={firstName} />

        <CreatorPageSection user={user} />

        <MembershipsSection memberships={activeMemberships} />
      </div>
    </HomeShell>
  );
}
