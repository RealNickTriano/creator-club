"use client";

import { BRAND_GRADIENT } from "@/lib/brand";
import { useTheme } from "@/lib/hooks/useTheme";

/**
 * Brand-gradient pill switch: a track with a gradient knob that slides right in
 * dark mode. Flips light ⇄ dark and persists the choice via the theme hook.
 */
export default function ThemeToggle() {
  const { theme, toggle } = useTheme();
  const dark = theme === "dark";

  return (
    <button
      type="button"
      onClick={toggle}
      role="switch"
      aria-checked={dark}
      aria-label="Toggle dark theme"
      className="border-border bg-foreground/10 focus-visible:ring-foreground focus-visible:ring-offset-background relative h-7 w-12 cursor-pointer rounded-full border p-0 transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none dark:bg-white/10"
    >
      <span
        className="absolute top-1 left-1 h-5 w-5 rounded-full shadow-sm transition-transform duration-300 ease-out dark:translate-x-5"
        style={{ backgroundImage: BRAND_GRADIENT }}
      />
    </button>
  );
}
