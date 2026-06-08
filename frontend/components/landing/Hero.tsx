import Button from "@/components/ui/Button";

export default function Hero() {
  return (
    <section className="mx-auto flex max-w-2xl flex-1 flex-col items-center justify-center px-6 py-24 text-center">
      <h1 className="text-4xl font-semibold tracking-tight text-balance sm:text-6xl">
        The home for creators.
      </h1>
      <p className="text-muted mt-6 max-w-md text-base text-pretty sm:text-lg">
        Build your audience, share your work, and grow your community — all in
        one place.
      </p>
      <div className="mt-10">
        <Button>Get started</Button>
      </div>
    </section>
  );
}
