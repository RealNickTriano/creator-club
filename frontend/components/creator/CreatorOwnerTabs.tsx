"use client";

import { useState } from "react";
import CreatorMembershipsList from "@/components/creator/CreatorMembershipsList";
import CreatorPostList from "@/components/creator/CreatorPostList";
import type { CreatorPost } from "@/types/creator";
import type { Tier } from "@/types/tier";

const TABS = ["Posts", "Memberships"] as const;
type Tab = (typeof TABS)[number];

/**
 * The owner view's tab switcher: "Posts" shows the manageable feed,
 * "Memberships" shows the tier list. Owner-only, so it holds its own active-tab
 * state client-side.
 */
export default function CreatorOwnerTabs({
  posts,
  tiers,
}: {
  posts: CreatorPost[];
  tiers: Tier[];
}) {
  const [active, setActive] = useState<Tab>("Posts");

  return (
    <div>
      <div
        role="tablist"
        aria-label="Creator sections"
        className="border-border flex gap-6 border-b"
      >
        {TABS.map((tab) => {
          const selected = tab === active;
          return (
            <button
              key={tab}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => setActive(tab)}
              className={`-mb-px cursor-pointer border-b-2 px-1 pb-3 text-sm font-medium transition-colors ${
                selected
                  ? "border-foreground text-foreground"
                  : "text-muted hover:text-foreground border-transparent"
              }`}
            >
              {tab}
            </button>
          );
        })}
      </div>

      <div role="tabpanel" className="mt-5">
        {active === "Posts" ? (
          <CreatorPostList posts={posts} />
        ) : (
          <CreatorMembershipsList tiers={tiers} />
        )}
      </div>
    </div>
  );
}
