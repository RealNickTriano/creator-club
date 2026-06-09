import StrokeIcon from "@/components/svg/StrokeIcon";

/** A rightward arrow — forward navigation / CTAs. */
export default function ArrowRightIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <path d="M2 12h17M13 6l6 6-6 6" />
    </StrokeIcon>
  );
}
