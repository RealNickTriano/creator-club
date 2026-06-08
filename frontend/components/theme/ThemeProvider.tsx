"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";

/**
 * Wraps next-themes with our defaults: theme is reflected as a class on <html>
 * (matching the `.dark` styles in globals.css), starts from the OS preference,
 * and is overridable + persisted by the user. Transitions are left enabled so
 * the surface eases smoothly between themes (see `body` in globals.css).
 */
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </NextThemesProvider>
  );
}
