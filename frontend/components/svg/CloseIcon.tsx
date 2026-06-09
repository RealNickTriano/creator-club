import StrokeIcon from "@/components/svg/StrokeIcon";

/** An X — closes menus and dialogs. */
export default function CloseIcon({ className }: { className?: string }) {
  return (
    <StrokeIcon className={className}>
      <path d="M18 6 6 18M6 6l12 12" />
    </StrokeIcon>
  );
}
