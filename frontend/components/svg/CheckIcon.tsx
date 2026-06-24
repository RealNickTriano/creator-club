import StrokeIcon from "@/components/svg/StrokeIcon";

/** A checkmark — success / confirmation. */
export default function CheckIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <path d="M5 13l4 4L19 7" />
    </StrokeIcon>
  );
}
