import Header from "@/components/landing/Header";
import Hero from "@/components/landing/Hero";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col">
      <Header />
      <Hero />
    </main>
  );
}
