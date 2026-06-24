import Link from "next/link";
import type { NavItem } from "@/components/home/navItems";

const LAYOUT =
  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium";
const ENABLED =
  "text-foreground-soft hover:bg-foreground/5 hover:text-foreground transition-colors";
const DISABLED = "text-muted cursor-not-allowed opacity-70";

/**
 * One sidebar row. A normal item renders a navigating `Link`; a `comingSoon`
 * item renders a disabled, non-navigating row with a "coming soon" tooltip (a
 * native `title` — the CSS `Tooltip` would be clipped by the nav's overflow).
 * `collapsed` hides the label into the icon rail.
 */
export default function SidebarNavLink({
  item: { href, label, Icon, comingSoon },
  collapsed,
  onNavigate,
}: {
  item: NavItem;
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const body = (
    <>
      <Icon className="h-5 w-5 shrink-0" />
      {!collapsed && <span className="truncate">{label}</span>}
    </>
  );
  const layout = `${LAYOUT} ${collapsed ? "justify-center" : ""}`;

  if (comingSoon) {
    return (
      <span
        aria-disabled="true"
        title={collapsed ? `${label} — coming soon` : "Coming soon"}
        className={`${layout} ${DISABLED}`}
      >
        {body}
      </span>
    );
  }

  return (
    <Link
      href={href}
      onClick={onNavigate}
      title={collapsed ? label : undefined}
      className={`${layout} ${ENABLED}`}
    >
      {body}
    </Link>
  );
}
