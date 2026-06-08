import Image from "next/image";
import type { User } from "@/types/user";

/**
 * The user's Google avatar, falling back to their initial in a circle. Rendered
 * via next/image so the avatar is optimized + cached server-side rather than
 * hotlinked from Google (which rate-limits direct requests with 429s).
 */
export default function UserAvatar({
  user,
  size = 32,
}: {
  user: User;
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
      style={{ width: size, height: size }}
      className="bg-foreground/10 flex items-center justify-center rounded-full text-xs"
    >
      {user.google_name.charAt(0).toUpperCase()}
    </span>
  );
}
