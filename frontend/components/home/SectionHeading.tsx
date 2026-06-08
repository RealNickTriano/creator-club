import Link from "next/link";

/**
 * A section label row: an uppercase heading on the left with an optional action
 * link on the right (e.g. "Your memberships" + "Explore →"). Used to introduce
 * each block of the home page.
 */
export default function SectionHeading({
  title,
  action,
}: {
  title: string;
  action?: { label: string; href: string };
}) {
  return (
    <div className="flex items-baseline justify-between">
      <h2 className="text-muted text-xs font-semibold tracking-wider uppercase">
        {title}
      </h2>
      {action && (
        <Link
          href={action.href}
          className="text-foreground-soft hover:text-foreground text-sm font-medium transition-colors"
        >
          {action.label}
        </Link>
      )}
    </div>
  );
}
