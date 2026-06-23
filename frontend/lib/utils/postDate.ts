/**
 * A short, human label for when a post was published — relative for recent
 * posts, an absolute date beyond a week:
 *   Today · Yesterday · "2d ago" … "6d ago" · "Jun 12" · "Mar 3, 2024".
 * A draft (no `published_at`) reads "Not published". Pure so it stays testable;
 * pass a fixed `now` in tests.
 */
export function postDateLabel(
  publishedAt: string | null,
  now: Date = new Date(),
): string {
  if (publishedAt === null) return "Not published";

  const published = new Date(publishedAt);
  // Compare by calendar day (not 24h windows), so "Today" means the same date.
  const startOfDay = (d: Date) =>
    new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
  const days = Math.round(
    (startOfDay(now) - startOfDay(published)) / 86_400_000,
  );

  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days >= 2 && days <= 6) return `${days}d ago`;

  // Older (or any future date) falls back to an absolute date, with the year
  // only when it differs from now.
  return published.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: published.getFullYear() === now.getFullYear() ? undefined : "numeric",
  });
}
