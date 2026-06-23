import Link from "next/link";
import {
  type NavItem,
  NAV_SECTIONS,
  NAV_TOP,
} from "@/components/home/navItems";

/** One nav link; `collapsed` hides its label into the icon rail. */
function NavLink({
  item: { href, label, Icon },
  collapsed,
  onNavigate,
}: {
  item: NavItem;
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onNavigate}
      title={collapsed ? label : undefined}
      className={`text-foreground-soft hover:bg-foreground/5 hover:text-foreground flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${collapsed ? "justify-center" : ""}`}
    >
      <Icon className="h-5 w-5 shrink-0" />
      {!collapsed && <span className="truncate">{label}</span>}
    </Link>
  );
}

/**
 * The navigation list, shared by the desktop sidebar and the mobile drawer.
 * Top-level links ({@link NAV_TOP}, e.g. Home) sit above the role sections
 * (Member, Creator), each section under a heading. `collapsed` hides labels and
 * headings into an icon rail (groups separated by dividers instead);
 * `onNavigate` fires on click so the mobile drawer can close itself.
 */
export default function SidebarNav({
  collapsed = false,
  onNavigate,
}: {
  collapsed?: boolean;
  onNavigate?: () => void;
}) {
  return (
    <nav className="flex flex-1 flex-col gap-4 overflow-x-hidden overflow-y-auto p-3">
      <div className="flex flex-col gap-1">
        {NAV_TOP.map((item) => (
          <NavLink
            key={item.label}
            item={item}
            collapsed={collapsed}
            onNavigate={onNavigate}
          />
        ))}
      </div>
      {NAV_SECTIONS.map((section) => (
        <div key={section.title} className="flex flex-col gap-1">
          {collapsed ? (
            <div className="border-border mx-2 mb-1 border-t" />
          ) : (
            <p className="text-muted px-3 pt-1 pb-1 text-xs font-semibold tracking-wide uppercase">
              {section.title}
            </p>
          )}
          {section.items.map((item) => (
            <NavLink
              key={item.label}
              item={item}
              collapsed={collapsed}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      ))}
    </nav>
  );
}
