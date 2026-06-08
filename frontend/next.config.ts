import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Serve Google profile avatars through Next's image optimizer so they're
    // fetched + cached server-side instead of hotlinked (which Google
    // rate-limits with 429s).
    remotePatterns: [
      {
        protocol: "https",
        hostname: "lh3.googleusercontent.com",
        pathname: "/**",
      },
    ],
  },
};

export default nextConfig;
