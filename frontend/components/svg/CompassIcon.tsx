import StrokeIcon from "@/components/svg/StrokeIcon";

/** A compass with a needle — explore. */
export default function CompassIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <circle cx="12" cy="12" r="9" />
      <path d="m15.5 8.5-2 5-5 2 2-5 5-2Z" />
    </StrokeIcon>
  );
}
