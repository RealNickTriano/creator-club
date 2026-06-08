/**
 * Primary CTA: the "Join now" pill. On hover the pill eases wider and an arrow
 * slides in from the label. The outer anchor stays put so :hover can't
 * oscillate; the inner span does the animating.
 */
export default function JoinButton() {
  return (
    <a href="#" className="group inline-block">
      <span className="bg-foreground text-background flex transform-gpu items-center rounded-full px-6 py-3.5 text-base font-medium shadow-lg transition-[padding] duration-300 ease-out group-hover:pr-8 group-hover:pl-7">
        Join now
        {/* Collapsed to zero width until hover, then expands + slides in. */}
        <span className="ml-0 flex w-0 -translate-x-1 items-center overflow-hidden opacity-0 transition-all duration-300 ease-out group-hover:ml-2 group-hover:w-5 group-hover:translate-x-0 group-hover:opacity-100">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
            className="h-5 w-5 shrink-0"
          >
            <path d="M2 12h17M13 6l6 6-6 6" />
          </svg>
        </span>
      </span>
    </a>
  );
}
