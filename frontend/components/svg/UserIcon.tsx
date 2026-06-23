import StrokeIcon from "@/components/svg/StrokeIcon";

/** A single person — your own profile / page. */
export default function UserIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1" />
    </StrokeIcon>
  );
}
