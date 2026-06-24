import { NAV_TOP } from "@/components/home/navItems";
import SidebarNavLink from "@/components/home/SidebarNavLink";

/**
 * The navigation list, shared by the desktop sidebar and the mobile drawer.
 * `collapsed` hides labels into an icon rail; `onNavigate` fires on click so
 * the mobile drawer can close itself.
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
          <SidebarNavLink
            key={item.label}
            item={item}
            collapsed={collapsed}
            onNavigate={onNavigate}
          />
        ))}
      </div>
    </nav>
  );
}
