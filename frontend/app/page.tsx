import BackgroundGradient from "@/components/landing/BackgroundGradient";
import GrainOverlay from "@/components/landing/GrainOverlay";
import Header from "@/components/landing/Header";
import Hero from "@/components/landing/Hero";

export default function Home() {
  return (
    <main className="relative isolate flex h-dvh flex-col overflow-hidden">
      <BackgroundGradient />
      <GrainOverlay />
      <Header />
      <Hero />
    </main>
  );
}
