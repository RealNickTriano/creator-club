import ThemeToggle from "@/components/ui/ThemeToggle";
import { BRAND_GRADIENT } from "@/lib/brand";

export default function Header() {
  return (
    <header className="flex items-center justify-between px-6 py-7 sm:px-10 lg:px-16">
      <div className="flex items-center gap-3 text-lg font-semibold tracking-tight">
        <span
          aria-hidden="true"
          className="h-4 w-4 rounded-full shadow-sm"
          style={{ backgroundImage: BRAND_GRADIENT }}
        />
        Creator Club
      </div>
      <div className="flex items-center gap-6">
        {/* Placeholder: wire up auth later */}
        <a
          href="#"
          className="text-foreground-soft hover:text-foreground text-sm font-medium transition-colors"
        >
          Sign in
        </a>
        <ThemeToggle />
      </div>
    </header>
  );
}
