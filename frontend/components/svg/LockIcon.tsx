import StrokeIcon from "@/components/svg/StrokeIcon";

/** A padlock — locked content. */
export default function LockIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </StrokeIcon>
  );
}
