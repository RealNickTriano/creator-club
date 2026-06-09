import { notFound } from "next/navigation";
import { getUserByHandle } from "@/lib/api/users";

/**
 * A creator's public page at `/c/{handle}`. Resolves the handle against the
 * backend: renders the page when the user exists, or the 404 page when they
 * don't. For now it just shows the handle — a placeholder for the real creator
 * profile (bio, tiers, posts) to come.
 */
export default async function CreatorPage({
  params,
}: {
  params: Promise<{ handle: string }>;
}) {
  const { handle } = await params;
  const user = await getUserByHandle(handle);
  if (!user) notFound();

  return (
    <main className="flex min-h-dvh flex-col items-center justify-center px-6">
      <p className="text-2xl font-semibold tracking-tight">@{user.handle}</p>
    </main>
  );
}
