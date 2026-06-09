import StrokeIcon from "@/components/svg/StrokeIcon";

/** Two people — members / community. */
export default function UsersIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <path d="M16 19v-1a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v1M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM22 19v-1a4 4 0 0 0-3-3.87M16 5.13A4 4 0 0 1 16 13" />
    </StrokeIcon>
  );
}
