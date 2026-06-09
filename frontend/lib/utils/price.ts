/**
 * Display label for a tier's monthly price, e.g. "$0 / mo" or "$5 / mo"
 * (cents shown only when not a whole dollar amount).
 */
export function formatTierPrice(priceCents: number): string {
  const dollars =
    priceCents % 100 === 0
      ? (priceCents / 100).toString()
      : (priceCents / 100).toFixed(2);
  return `$${dollars} / mo`;
}
