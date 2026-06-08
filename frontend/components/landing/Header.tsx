import Button from "@/components/ui/Button";
import ThemeToggle from "@/components/ui/ThemeToggle";

export default function Header() {
  return (
    <header className="flex items-center justify-between px-6 py-5 sm:px-10">
      <span className="text-lg font-semibold tracking-tight">Creator Club</span>
      <div className="flex items-center gap-3">
        <ThemeToggle />
        {/* Placeholder: wire up auth later */}
        <Button variant="outline">Log in</Button>
      </div>
    </header>
  );
}
