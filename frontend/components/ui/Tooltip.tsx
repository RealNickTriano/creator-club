/**
 * Generic tooltip: wraps its child and shows a small label above it on hover
 * or keyboard focus. Pure CSS (no portal), so the label is clipped by any
 * `overflow-hidden` ancestor — fine for toolbars and buttons inside cards.
 *
 * The label is presentational only; give the wrapped control its own
 * `aria-label` so screen readers aren't relying on the tooltip.
 */
export default function Tooltip({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <span className="group/tooltip relative inline-flex">
      {children}
      <span
        aria-hidden="true"
        className="bg-foreground text-background pointer-events-none absolute bottom-full left-1/2 z-10 mb-1.5 -translate-x-1/2 rounded-md px-2 py-1 text-xs font-medium whitespace-nowrap opacity-0 shadow-sm transition-opacity delay-150 duration-150 group-focus-within/tooltip:opacity-100 group-hover/tooltip:opacity-100"
      >
        {label}
      </span>
    </span>
  );
}
