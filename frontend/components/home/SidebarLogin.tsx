"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import LogInIcon from "@/components/svg/LogInIcon";

/**
 * The sidebar footer for signed-out visitors — takes the spot {@link UserMenu}
 * holds when someone is signed in. A primary "Log in" pill, shrinking to an
 * icon button when the sidebar is collapsed to its rail. Carries the current
 * path as the post-login destination, so signing in returns you here.
 */
export default function SidebarLogin({
  collapsed = false,
}: {
  collapsed?: boolean;
}) {
  const pathname = usePathname();
  const loginUrl = `/login?next=${encodeURIComponent(pathname)}`;

  if (collapsed) {
    return (
      <Link
        href={loginUrl}
        title="Log in"
        className="text-foreground-soft hover:bg-foreground/5 hover:text-foreground flex items-center justify-center rounded-lg p-2 transition-colors"
      >
        <LogInIcon className="h-5 w-5 shrink-0" />
      </Link>
    );
  }

  return (
    <Link
      href={loginUrl}
      className="bg-foreground text-background flex h-9 w-full items-center justify-center gap-2 rounded-full text-sm font-medium transition-opacity hover:opacity-90"
    >
      <LogInIcon className="h-4 w-4 shrink-0" />
      Log in
    </Link>
  );
}
