"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import BrandLoader from "@/components/brand/BrandLoader";
import CreatorPageSection from "@/components/home/CreatorPageSection";
import CreatorSearch from "@/components/home/CreatorSearch";
import HomeGreeting from "@/components/home/HomeGreeting";
import HomeShell from "@/components/home/HomeShell";
import MembershipsSection from "@/components/home/MembershipsSection";
import { useCurrentUser } from "@/lib/hooks/useCurrentUser";
import { PLACEHOLDER_MEMBERSHIPS } from "@/lib/placeholders/memberships";

export default function HomePage() {
  const { user, loading, error } = useCurrentUser();
  const router = useRouter();

  // Bounce signed-out visitors (no session / 401) back to login.
  useEffect(() => {
    if (!loading && (error || !user)) router.replace("/login");
  }, [loading, error, user, router]);

  if (loading || !user) {
    return <BrandLoader />;
  }

  const firstName = user.google_name.split(" ")[0];

  return (
    <HomeShell user={user}>
      <div className="mx-auto max-w-3xl">
        <HomeGreeting name={firstName} />
        <div className="mt-6">
          <CreatorSearch />
        </div>

        <CreatorPageSection handle={user.handle} />

        <MembershipsSection memberships={PLACEHOLDER_MEMBERSHIPS} />
      </div>
    </HomeShell>
  );
}
