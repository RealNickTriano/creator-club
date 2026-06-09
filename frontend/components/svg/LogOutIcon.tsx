import StrokeIcon from "@/components/svg/StrokeIcon";

/** A door with an out-arrow — sign out. */
export default function LogOutIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" />
    </StrokeIcon>
  );
}
