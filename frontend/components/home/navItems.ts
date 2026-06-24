import type { ComponentType } from "react";
import CardIcon from "@/components/svg/CardIcon";
import HomeIcon from "@/components/svg/HomeIcon";
import SettingsIcon from "@/components/svg/SettingsIcon";

export type NavItem = {
  href: string;
  label: string;
  Icon: ComponentType<{ className?: string }>;
  /** Disable the link and show a "coming soon" tooltip — page not built yet. */
  comingSoon?: boolean;
};

/** Top-level links shown in the sidebar (no heading). */
export const NAV_TOP: NavItem[] = [
  { href: "/home", label: "Home", Icon: HomeIcon },
  { href: "#", label: "Billing", Icon: CardIcon },
  { href: "#", label: "Settings", Icon: SettingsIcon },
];
