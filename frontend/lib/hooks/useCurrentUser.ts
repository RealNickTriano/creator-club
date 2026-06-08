"use client";

import { useEffect, useState } from "react";
import { getCurrentUser } from "@/lib/api/auth";
import type { User } from "@/types/user";

type CurrentUser = {
  user: User | null;
  loading: boolean;
  /** Set when `/me` fails — most commonly a 401 (not signed in). */
  error: boolean;
};

/**
 * Loads the current user from `/me` on mount. Components use this to gate
 * authenticated views and redirect signed-out visitors to /login.
 */
export function useCurrentUser(): CurrentUser {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    getCurrentUser()
      .then((u) => {
        if (active) setUser(u);
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

  return { user, loading, error };
}
