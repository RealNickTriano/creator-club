import StrokeIcon from "@/components/svg/StrokeIcon";

/** A magnifying glass — search / find. */
export default function SearchIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </StrokeIcon>
  );
}
