import Image from "next/image";
import { BRAND_GRADIENT } from "@/lib/brand";
import type { PublicUser, User } from "@/types/user";

/**
 * The user's Google avatar, falling back to their initial in a circle. Rendered
 * via next/image so the avatar is optimized + cached server-side rather than
 * hotlinked from Google (which rate-limits direct requests with 429s).
 */
export default function UserAvatar({
  user,
  size = 32,
}: {
  user: User | PublicUser;
  size?: number;
}) {
  if (user.google_avatar_url) {
    return (
      <Image
        src={user.google_avatar_url}
        alt=""
        width={size}
        height={size}
        className="rounded-full object-cover"
      />
    );
  }

  return (
    <span
      style={{
        width: size,
        height: size,
        fontSize: size * 0.45,
        backgroundImage: BRAND_GRADIENT,
      }}
      // Fixed dark ink: the pastel gradient stays light in both themes.
      className="flex items-center justify-center rounded-full font-medium text-zinc-900"
    >
      {user.google_name?.charAt(0).toUpperCase()}
    </span>
  );
}
