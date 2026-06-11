import StrokeIcon from "@/components/svg/StrokeIcon";

/** A door with an in-arrow — sign in. */
export default function LogInIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3" />
    </StrokeIcon>
  );
}
