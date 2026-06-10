"use client";

import { useCallback, useEffect, useState } from "react";
import { listMyMemberships } from "@/lib/api/memberships";
import type { Membership } from "@/types/membership";

type Memberships = {
  memberships: Membership[];
  /** True during the initial load only — `refresh` updates in place. */
  loading: boolean;
  /** Set when `/memberships` fails — most commonly a 401 (not signed in). */
  error: boolean;
  /** Refetch the list, e.g. after joining or changing a tier. */
  refresh: () => void;
};

/**
 * Loads the signed-in user's memberships from `/memberships` on mount.
 * `memberships` stays `[]` until loaded (and on error).
 */
export function useMemberships(): Memberships {
  const [memberships, setMemberships] = useState<Membership[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [generation, setGeneration] = useState(0);

  useEffect(() => {
    let active = true;
    listMyMemberships()
      .then((m) => {
        if (active) {
          setMemberships(m);
          setError(false);
        }
      })
      .catch(() => {
        if (active) setError(true);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [generation]);

  const refresh = useCallback(() => setGeneration((g) => g + 1), []);

  return { memberships, loading, error, refresh };
}
