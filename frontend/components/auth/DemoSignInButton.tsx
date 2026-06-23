import LogInIcon from "@/components/svg/LogInIcon";
import { demoLoginUrl } from "@/lib/api/auth";

/**
 * Starts a demo session — a fresh, empty account, no Google needed. A plain
 * anchor (full-page navigation) so the backend can set the session cookie and
 * redirect back into the app, to `next` when given, or /home. Styled as the
 * quieter, secondary option beneath Google sign-in.
 */
export default function DemoSignInButton({ next }: { next?: string }) {
  return (
    <a
      href={demoLoginUrl(next)}
      className="border-border text-muted hover:text-foreground hover:bg-foreground/5 focus-visible:ring-foreground focus-visible:ring-offset-background inline-flex items-center gap-3 rounded-full border px-6 py-3 text-sm font-medium transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none"
    >
      <LogInIcon className="h-5 w-5" />
      Continue as demo
    </a>
  );
}
