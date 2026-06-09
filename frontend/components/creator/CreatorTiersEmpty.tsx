/**
 * The owner's tiers empty state: shown in the Memberships tab when the creator
 * hasn't made any tiers yet, nudging them to add the first one.
 */
export default function CreatorTiersEmpty({
  onAddTier,
}: {
  onAddTier: () => void;
}) {
  return (
    <div className="border-border bg-background rounded-xl border border-dashed p-8 text-center">
      <b className="text-foreground block text-sm font-semibold">
        No tiers yet
      </b>
      <p className="text-foreground-soft mx-auto mt-1.5 max-w-sm text-sm">
        Tiers are what people join — add your first one to start taking members.
        Make it free, or set a monthly price.
      </p>
      <button
        type="button"
        onClick={onAddTier}
        className="bg-foreground text-background mt-4 inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-sm font-medium transition-opacity hover:opacity-90"
      >
        Add tier
      </button>
    </div>
  );
}
