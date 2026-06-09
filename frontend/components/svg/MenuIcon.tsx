import StrokeIcon from "@/components/svg/StrokeIcon";

/** Three stacked lines — the hamburger menu / sidebar toggle. */
export default function MenuIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <path d="M4 6h16M4 12h16M4 18h16" />
    </StrokeIcon>
  );
}
