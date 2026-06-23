import { displayName } from "@/lib/utils/names";
import type { PublicUser } from "@/types/user";
import UserAvatar from "../auth/UserAvatar";

/**
 * The shared creator-page identity block: avatar, name, `@handle`, and bio.
 * Both the owner and viewer headers compose this — the owner adds an actions
 * row via `children`.
 */
export default function CreatorIdentity({
  creator,
  children,
}: {
  creator: PublicUser;
  children?: React.ReactNode;
}) {
  const name = displayName(creator) ?? creator.handle ?? "Untitled creator";

  return (
    <header className="flex items-start gap-4">
      <UserAvatar user={creator} size={64} />
      <div className="min-w-0 flex-1">
        <h1 className="text-foreground text-2xl font-semibold tracking-tight">
          {name}
        </h1>
        <p className="text-muted mt-0.5 text-sm">@{creator.handle}</p>
        {creator.bio && (
          <p className="text-foreground-soft mt-2 text-sm">{creator.bio}</p>
        )}
        {children && (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {children}
          </div>
        )}
      </div>
    </header>
  );
}
