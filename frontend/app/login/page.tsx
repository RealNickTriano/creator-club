import GoogleSignInButton from "@/components/auth/GoogleSignInButton";
import Wordmark from "@/components/brand/Wordmark";

/**
 * The sign-in page. `?next=/some/path` carries where to land after the OAuth
 * round trip (e.g. back to the creator page whose locked post prompted the
 * login); without it the backend defaults to /home.
 */
export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string | string[] }>;
}) {
  const { next } = await searchParams;
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-10 px-6">
      <Wordmark />
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Welcome</h1>
        <p className="text-muted text-sm">
          Sign in to continue to Creator Club.
        </p>
      </div>
      <GoogleSignInButton next={typeof next === "string" ? next : undefined} />
    </main>
  );
}
