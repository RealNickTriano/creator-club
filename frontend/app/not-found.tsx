import Link from "next/link";
import Wordmark from "@/components/brand/Wordmark";

export default function NotFound() {
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-4 px-6">
      <Wordmark />
      <div className="space-y-2 text-center">
        <p className="text-muted text-7xl font-bold tracking-tight">404</p>
        <h1 className="text-2xl font-semibold tracking-tight">
          This page doesn&apos;t exist
        </h1>
        <p className="text-muted text-sm">
          The page you&apos;re looking for may have moved or never existed.
        </p>
      </div>
      <Link
        href="/home"
        className="bg-foreground text-background focus-visible:ring-foreground focus-visible:ring-offset-background inline-flex items-center rounded-full px-6 py-3 text-sm font-medium shadow-sm transition-opacity hover:opacity-90 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none"
      >
        Back to home
      </Link>
    </main>
  );
}
