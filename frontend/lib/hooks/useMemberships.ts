"use client";

import { useEffect, useState } from "react";
import { listMyMemberships } from "@/lib/api/memberships";
import type { Membership } from "@/types/membership";

type Memberships = {
  memberships: Membership[];
  loading: boolean;
  /** Set when `/memberships` fails — most commonly a 401 (not signed in). */
  error: boolean;
};

/**
 * Loads the signed-in user's memberships from `/memberships` on mount.
 * `memberships` stays `[]` until loaded (and on error).
 */
export function useMemberships(): Memberships {
  const [memberships, setMemberships] = useState<Membership[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    listMyMemberships()
      .then((m) => {
        if (active) setMemberships(m);
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
  }, []);

  return { memberships, loading, error };
}
