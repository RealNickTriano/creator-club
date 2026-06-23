import StrokeIcon from "@/components/svg/StrokeIcon";

/** A payment card — billing. */
export default function CardIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <rect x="2" y="5" width="20" height="14" rx="2" />
      <path d="M2 10h20M6 15h4" />
    </StrokeIcon>
  );
}
