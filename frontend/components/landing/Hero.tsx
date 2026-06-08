import JoinButton from "@/components/landing/JoinButton";

/**
 * "Bold" direction (03): oversized headline filling the lower viewport, with
 * the supporting line and CTA sharing a baseline row beneath it.
 */
export default function Hero() {
  return (
    <section className="flex flex-1 items-end px-6 pb-20 sm:px-10 lg:px-16 lg:pb-28">
      <div className="mx-auto w-full max-w-6xl">
        <h1 className="text-[clamp(52px,11vw,168px)] leading-[0.9] font-medium tracking-tighter">
          Make what
          <br />
          you love.
          <br />
          Get paid
          <br />
          for it.
        </h1>
        <div className="mt-10 flex flex-wrap items-end justify-between gap-10">
          <p className="text-foreground-soft max-w-md text-lg leading-relaxed sm:text-xl">
            Creator Club gives independent creators a dependable income from the
            fans who value their work the most.
          </p>
          <JoinButton />
        </div>
      </div>
    </section>
  );
}
