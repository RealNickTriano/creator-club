"use client";

import { useSyncExternalStore } from "react";

const subscribe = () => () => {};

/**
 * Returns `false` during SSR and the initial hydration render, then `true` once
 * mounted on the client. Use it to gate client-only values (e.g. resolved
 * theme) so the first render matches the server and avoids hydration mismatches.
 */
export function useMounted(): boolean {
  return useSyncExternalStore(
    subscribe,
    () => true,
    () => false,
  );
}
