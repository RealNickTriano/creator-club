import type { ComponentType } from "react";
import CardIcon from "@/components/svg/CardIcon";
import CompassIcon from "@/components/svg/CompassIcon";
import HeartIcon from "@/components/svg/HeartIcon";
import HomeIcon from "@/components/svg/HomeIcon";
import PostsIcon from "@/components/svg/PostsIcon";
import UserIcon from "@/components/svg/UserIcon";
import UsersIcon from "@/components/svg/UsersIcon";

export type NavItem = {
  href: string;
  label: string;
  Icon: ComponentType<{ className?: string }>;
};

/** A titled group of nav links — the sidebar renders one per role. */
export type NavSection = {
  title: string;
  items: NavItem[];
};

/** Top-level links shown above the role sections (no heading). */
export const NAV_TOP: NavItem[] = [
  { href: "/home", label: "Home", Icon: HomeIcon },
];

/**
 * The sidebar navigation below {@link NAV_TOP}, split by the role the page
 * serves: acting as a member (the feed of creators you follow, your
 * memberships, discovering more) vs. as a creator (your own page, your members,
 * billing). Hrefs are placeholders (`#`) for pages not built yet; the live
 * /home lives on the top-level "Home" link.
 */
export const NAV_SECTIONS: NavSection[] = [
  {
    title: "Member",
    items: [
      { href: "#", label: "Feed", Icon: PostsIcon },
      { href: "#", label: "My memberships", Icon: HeartIcon },
      { href: "#", label: "Explore", Icon: CompassIcon },
    ],
  },
  {
    title: "Creator",
    items: [
      { href: "#", label: "My page", Icon: UserIcon },
      { href: "#", label: "Members", Icon: UsersIcon },
      { href: "#", label: "Billing", Icon: CardIcon },
    ],
  },
];
