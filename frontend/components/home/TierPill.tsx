/**
 * A small badge showing the user's current tier on a creator. The color is
 * chosen by tier `rank`: rank 0 (the free tier) through rank 5 each get their
 * own brand pastel; anything above rank 5 reuses the rank-5 color. In dark
 * mode the pastel becomes the text color so the label stays legible.
 */

/** Tone per rank (index 0 = free), as `bg / light text / dark text` classes. */
const RANK_TONES = [
  "bg-[#bfe3d6]/40 text-[#2f6b54] dark:text-[#bfe3d6]", // 0 · free (mint)
  "bg-[#c2cffa]/30 text-[#3b4a86] dark:text-[#c2cffa]", // 1 · periwinkle
  "bg-[#ddc8f2]/40 text-[#6b3b86] dark:text-[#ddc8f2]", // 2 · lavender
  "bg-[#f7b5c4]/30 text-[#86344b] dark:text-[#f7b5c4]", // 3 · pink
  "bg-[#f5d9a8]/40 text-[#87632a] dark:text-[#f5d9a8]", // 4 · gold
  "bg-[#a8e0f5]/40 text-[#2a6587] dark:text-[#a8e0f5]", // 5+ · sky
];

export default function TierPill({
  name,
  rank,
}: {
  name: string;
  rank: number;
}) {
  const tone = RANK_TONES[Math.min(Math.max(rank, 0), RANK_TONES.length - 1)];

  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold tracking-wide ${tone}`}
    >
      {name}
    </span>
  );
}
