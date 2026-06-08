"use client";

import { useTheme as useNextTheme } from "next-themes";

/**
 * Thin wrapper over next-themes that exposes the resolved theme and a simple
 * light/dark toggle, so components don't depend on the library directly.
 */
export function useTheme() {
  const { resolvedTheme, setTheme } = useNextTheme();

  const toggle = () => setTheme(resolvedTheme === "dark" ? "light" : "dark");

  return { theme: resolvedTheme, toggle };
}
