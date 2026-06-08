"use client";

import { useMemo } from "react";
import { useMounted } from "@/lib/hooks/useMounted";
import { pickGreeting } from "@/lib/utils/greeting";

/**
 * The home page's opening line: a personalized greeting + one-line subtext.
 * Returning members get a randomly chosen greeting — the time-of-day line
 * ("Good morning, Nick") or one of a handful of playful ones; new users (no
 * memberships / no page) get the onboarding welcome from mockup B.
 *
 * Both the random pick and the time-of-day depend on client-only state (RNG and
 * the visitor's local clock), so they're gated behind {@link useMounted}: the
 * server and first client render show a stable "Welcome back" fallback, then it
 * resolves to the chosen greeting on mount to avoid a hydration mismatch.
 */
export default function HomeGreeting({
  name,
  isNewUser = false,
}: {
  name: string;
  isNewUser?: boolean;
}) {
  const mounted = useMounted();
  // Pick once per mount (not on every re-render) so the greeting stays stable.
  const randomGreeting = useMemo(
    () => pickGreeting(name),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [name, mounted],
  );

  let heading: string;
  let subtext: string;
  if (isNewUser) {
    heading = `Welcome to Creator Club, ${name}`;
    subtext = "Support the creators you love — or start your own page.";
  } else {
    heading = mounted ? randomGreeting : `Welcome back, ${name}`;
    subtext = "Jump back into the creators you support.";
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">{heading}</h1>
      <p className="text-muted mt-1 text-sm">{subtext}</p>
    </div>
  );
}
