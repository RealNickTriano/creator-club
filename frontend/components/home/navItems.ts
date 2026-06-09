import type { ComponentType } from "react";
import HomeIcon from "@/components/svg/HomeIcon";
import PostsIcon from "@/components/svg/PostsIcon";
import SettingsIcon from "@/components/svg/SettingsIcon";
import UsersIcon from "@/components/svg/UsersIcon";

export type NavItem = {
  href: string;
  label: string;
  Icon: ComponentType<{ className?: string }>;
};

export const NAV_ITEMS: NavItem[] = [
  { href: "/home", label: "Home", Icon: HomeIcon },
  { href: "#", label: "Posts", Icon: PostsIcon },
  { href: "#", label: "Members", Icon: UsersIcon },
  { href: "#", label: "Settings", Icon: SettingsIcon },
];
