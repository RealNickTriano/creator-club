import StrokeIcon from "@/components/svg/StrokeIcon";

/** A document with lines — posts. */
export default function PostsIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <path d="M5 3h10l4 4v14H5zM15 3v4h4M8 13h8M8 17h8M8 9h3" />
    </StrokeIcon>
  );
}
