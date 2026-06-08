import AuthNav from "@/components/landing/AuthNav";
import Wordmark from "@/components/brand/Wordmark";
import ThemeToggle from "@/components/ui/ThemeToggle";

export default function Header() {
  return (
    <header className="flex items-center justify-between px-6 py-7 sm:px-10 lg:px-16">
      <Wordmark />
      <div className="flex items-center gap-6">
        <AuthNav />
        <ThemeToggle />
      </div>
    </header>
  );
}
