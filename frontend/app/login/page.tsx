import GoogleSignInButton from "@/components/auth/GoogleSignInButton";
import Wordmark from "@/components/brand/Wordmark";

export default function LoginPage() {
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-10 px-6">
      <Wordmark />
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Welcome</h1>
        <p className="text-muted text-sm">
          Sign in to continue to Creator Club.
        </p>
      </div>
      <GoogleSignInButton />
    </main>
  );
}
