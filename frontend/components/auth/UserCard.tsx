import type { User } from "@/types/user";

/** Presentational summary of the signed-in user. */
export default function UserCard({ user }: { user: User }) {
  return (
    <div className="border-border flex flex-col items-center gap-4 rounded-2xl border p-8 text-center">
      {user.google_avatar_url ? (
        // eslint-disable-next-line @next/next/no-img-element -- remote avatar, no next/image domain config
        <img
          src={user.google_avatar_url}
          alt=""
          className="h-16 w-16 rounded-full object-cover"
        />
      ) : (
        <div className="bg-foreground/10 h-16 w-16 rounded-full" />
      )}

      <div className="space-y-0.5">
        <p className="text-lg font-semibold tracking-tight">
          {user.google_name}
        </p>
        {user.handle && <p className="text-muted text-sm">@{user.handle}</p>}
        <p className="text-muted text-sm">{user.google_email}</p>
      </div>
    </div>
  );
}
