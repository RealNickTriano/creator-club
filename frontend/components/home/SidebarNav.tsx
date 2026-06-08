import Link from "next/link";
import { NAV_ITEMS } from "@/components/home/navItems";

/**
 * The navigation link list, shared by the desktop sidebar and the mobile
 * drawer. `collapsed` hides labels into an icon rail; `onNavigate` fires on
 * click so the mobile drawer can close itself.
 */
export default function SidebarNav({
  collapsed = false,
  onNavigate,
}: {
  collapsed?: boolean;
  onNavigate?: () => void;
}) {
  return (
    <nav className="flex flex-1 flex-col gap-1 overflow-x-hidden overflow-y-auto p-3">
      {NAV_ITEMS.map(({ href, label, Icon }) => (
        <Link
          key={label}
          href={href}
          onClick={onNavigate}
          title={collapsed ? label : undefined}
          className={`text-foreground-soft hover:bg-foreground/5 hover:text-foreground flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${collapsed ? "justify-center" : ""}`}
        >
          <Icon className="h-5 w-5 shrink-0" />
          {!collapsed && <span className="truncate">{label}</span>}
        </Link>
      ))}
    </nav>
  );
}
