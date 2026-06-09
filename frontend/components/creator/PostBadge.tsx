/** Visibility / draft badge tones, matching the tier-pill pastels. */
const BADGE_TONES = {
  draft: "bg-foreground/10 text-foreground-soft",
  public: "bg-[#bfe3d6]/40 text-[#2f6b54] dark:text-[#bfe3d6]",
  members: "bg-[#ddc8f2]/40 text-[#6b3b86] dark:text-[#ddc8f2]",
} as const;

/** A small badge marking a post's visibility (Public / a tier) or draft state. */
export default function PostBadge({
  tone,
  children,
}: {
  tone: keyof typeof BADGE_TONES;
  children: React.ReactNode;
}) {
  return (
    <span
      className={`inline-block shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${BADGE_TONES[tone]}`}
    >
      {children}
    </span>
  );
}
