/**
 * Fine fractal-noise grain for a premium, slightly tactile surface. Multiplies
 * onto the gradient in light mode; in dark mode it switches to a faint screen
 * blend so it lifts rather than muddies the deep base. Non-interactive, sits
 * just above the canvas and below page content.
 */
const NOISE =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E";

export default function GrainOverlay() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 -z-10 opacity-45 mix-blend-multiply dark:opacity-5 dark:mix-blend-screen"
      style={{ backgroundImage: `url("${NOISE}")` }}
    />
  );
}
