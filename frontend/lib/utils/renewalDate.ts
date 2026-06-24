/**
 * An absolute date label for a subscription's period end, e.g. "Jul 8, 2026";
 * an em dash when the membership is open-ended (no period end, e.g. free tiers).
 */
export function renewalDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
