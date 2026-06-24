/**
 * A bare price label, e.g. "$0" or "$5" (cents shown only when not a whole
 * dollar amount).
 */
export function formatPrice(priceCents: number): string {
  const dollars =
    priceCents % 100 === 0
      ? (priceCents / 100).toString()
      : (priceCents / 100).toFixed(2);
  return `$${dollars}`;
}

/** Display label for a tier's monthly price, e.g. "$0 / mo" or "$5 / mo". */
export function formatTierPrice(priceCents: number): string {
  return `${formatPrice(priceCents)} / mo`;
}
