import CreatorPageLiveCard from "@/components/home/CreatorPageLiveCard";
import CreatorPageSetupCard from "@/components/home/CreatorPageSetupCard";
import SectionHeading from "@/components/home/SectionHeading";

/** The signed-in user's own creator page, once it exists. */
export type CreatorPage = {
  handle: string;
  tierCount: number;
  postCount: number;
};

/**
 * The "Your creator page" block: a section heading plus the owner card. Shows
 * the live card when the user has a page, or the setup CTA when they don't.
 */
export default function CreatorPageSection({ page }: { page?: CreatorPage }) {
  return (
    <section className="mt-8">
      <SectionHeading title="Your creator page" />
      <div className="mt-3">
        {page ? (
          <CreatorPageLiveCard
            handle={page.handle}
            tierCount={page.tierCount}
            postCount={page.postCount}
          />
        ) : (
          <CreatorPageSetupCard />
        )}
      </div>
    </section>
  );
}
