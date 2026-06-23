import StrokeIcon from "@/components/svg/StrokeIcon";

/** An outlined heart — memberships (creators you support). */
export default function HeartIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <path d="M20.8 5.6a5 5 0 0 0-7.1 0L12 7.3l-1.7-1.7a5 5 0 1 0-7.1 7.1L12 21l8.8-8.3a5 5 0 0 0 0-7.1Z" />
    </StrokeIcon>
  );
}
