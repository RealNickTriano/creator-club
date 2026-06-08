import { BRAND_GRADIENT } from "@/lib/brand";

/**
 * Full-screen branded loading state: the gradient brand mark gently breathing,
 * with a soft blurred halo behind it. Used while we resolve the session.
 */
export default function BrandLoader() {
  return (
    <div
      role="status"
      aria-label="Loading"
      className="flex min-h-dvh items-center justify-center"
    >
      <div className="relative h-12 w-12">
        <span
          aria-hidden="true"
          className="animate-brand-breathe absolute inset-0 rounded-full opacity-60 blur-md"
          style={{ backgroundImage: BRAND_GRADIENT }}
        />
        <span
          aria-hidden="true"
          className="animate-brand-breathe absolute inset-0 rounded-full shadow-sm"
          style={{ backgroundImage: BRAND_GRADIENT }}
        />
      </div>
    </div>
  );
}
