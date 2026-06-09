import GoogleIcon from "@/components/svg/GoogleIcon";
import { googleLoginUrl } from "@/lib/api/auth";

/**
 * Starts Google sign-in. A plain anchor (full-page navigation) so the backend
 * can run the OAuth redirect dance; on success it sets the session cookie and
 * redirects back into the app.
 */
export default function GoogleSignInButton() {
  return (
    <a
      href={googleLoginUrl()}
      className="border-border bg-background text-foreground hover:bg-foreground/5 focus-visible:ring-foreground focus-visible:ring-offset-background inline-flex items-center gap-3 rounded-full border px-6 py-3 text-sm font-medium shadow-sm transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none"
    >
      <GoogleIcon className="h-5 w-5" />
      Sign in with Google
    </a>
  );
}
