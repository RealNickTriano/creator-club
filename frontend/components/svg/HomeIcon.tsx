import StrokeIcon from "@/components/svg/StrokeIcon";

/** A house — the home destination. */
export default function HomeIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <path d="M3 10.5 12 3l9 7.5M5 9.5V21h14V9.5" />
    </StrokeIcon>
  );
}
