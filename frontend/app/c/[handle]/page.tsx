import { notFound } from "next/navigation";
import CreatorView from "@/components/creator/CreatorView";
import { getTiersByHandle } from "@/lib/api/tiers";
import { getUserByHandle } from "@/lib/api/users";

/**
 * A creator's page at `/c/{handle}`. Resolves the handle and the tier ladder
 * against the backend in parallel (404 if no such user), then hands off to
 * {@link CreatorView}, which loads the current viewer and renders the owner or
 * viewer experience inside the shell.
 */
export default async function CreatorPage({
  params,
}: {
  params: Promise<{ handle: string }>;
}) {
  const { handle } = await params;
  const [creator, tiers] = await Promise.all([
    getUserByHandle(handle),
    getTiersByHandle(handle),
  ]);
  if (!creator) notFound();

  return <CreatorView creator={creator} tiers={tiers ?? []} />;
}
