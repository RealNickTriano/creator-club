import CreatorPageLiveCard from "@/components/home/CreatorPageLiveCard";
import CreatorPageSetupCard from "@/components/home/CreatorPageSetupCard";
import SectionHeading from "@/components/home/SectionHeading";
import type { User } from "@/types/user";

/** The signed-in user's own creator page, once it exists. */
export type CreatorPage = {
  handle: string;
  tierCount: number;
  postCount: number;
};

/**
 * The "Your creator page" block: a section heading plus the owner card. Shows
 * the live card when the user has a page, or the setup CTA when they don't.
 * `user` is the signed-in user; the setup CTA shows their avatar and either
 * links to their page or prompts them to pick a handle first.
 */
export default function CreatorPageSection({
  page,
  user,
}: {
  page?: CreatorPage;
  user: User;
}) {
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
          <CreatorPageSetupCard user={user} />
        )}
      </div>
    </section>
  );
}
