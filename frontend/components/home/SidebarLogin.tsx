import Link from "next/link";
import LogInIcon from "@/components/svg/LogInIcon";

/**
 * The sidebar footer for signed-out visitors — takes the spot {@link UserMenu}
 * holds when someone is signed in. A primary "Log in" pill, shrinking to an
 * icon button when the sidebar is collapsed to its rail.
 */
export default function SidebarLogin({
  collapsed = false,
}: {
  collapsed?: boolean;
}) {
  if (collapsed) {
    return (
      <Link
        href="/login"
        title="Log in"
        className="text-foreground-soft hover:bg-foreground/5 hover:text-foreground flex items-center justify-center rounded-lg p-2 transition-colors"
      >
        <LogInIcon className="h-5 w-5 shrink-0" />
      </Link>
    );
  }

  return (
    <Link
      href="/login"
      className="bg-foreground text-background flex h-9 w-full items-center justify-center gap-2 rounded-full text-sm font-medium transition-opacity hover:opacity-90"
    >
      <LogInIcon className="h-4 w-4 shrink-0" />
      Log in
    </Link>
  );
}
