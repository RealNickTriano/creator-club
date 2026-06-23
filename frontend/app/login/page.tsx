import DemoSignInButton from "@/components/auth/DemoSignInButton";
import GoogleSignInButton from "@/components/auth/GoogleSignInButton";
import BrandMark from "@/components/brand/BrandMark";
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
  const nextPath = typeof next === "string" ? next : undefined;
  return (
    <main className="relative flex min-h-dvh flex-col items-center justify-center gap-10 px-6">
      <div className="absolute top-6 left-6">
        <Wordmark />
      </div>
      <BrandMark className="h-20 w-20" />
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Welcome</h1>
        <p className="text-muted text-sm">
          Sign in to continue to Creator Club.
        </p>
      </div>
      <div className="flex w-full max-w-xs flex-col items-center gap-4">
        <GoogleSignInButton next={nextPath} />
        <div className="flex w-full items-center gap-3">
          <span className="border-border h-px flex-1 border-t" />
          <span className="text-muted text-xs">or</span>
          <span className="border-border h-px flex-1 border-t" />
        </div>
        <DemoSignInButton next={nextPath} />
        <p className="text-muted text-center text-xs text-balance">
          Just exploring? The demo is your own sandbox to play in.
        </p>
      </div>
    </main>
  );
}
