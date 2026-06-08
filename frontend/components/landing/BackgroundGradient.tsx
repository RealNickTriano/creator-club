"use client";

import { useEffect, useRef } from "react";
import { useTheme } from "@/lib/hooks/useTheme";

/**
 * Decorative, cursor-reactive background for the "Bold" direction. A canvas
 * renders soft pastel blobs that drift gently, parallax with the pointer, and
 * are pulled toward it, plus a colored spotlight that follows the cursor. The
 * engine is theme-aware: pastels tint a near-white base (multiply) in light
 * mode and glow against a deep base (screen) in dark mode.
 *
 * Parent should be `relative isolate overflow-hidden`; the canvas sits behind
 * all other content.
 */

// Pastel palette — pink, periwinkle, mint, lavender, peach.
const COLORS = ["#f7b5c4", "#c2cffa", "#bfe3d6", "#ddc8f2", "#ffd6c2"];

type ThemeConfig = {
  base: string;
  comp: GlobalCompositeOperation;
  blobA: number;
  cursor: string;
  cursorA: number;
};

const THEMES: Record<"light" | "dark", ThemeConfig> = {
  light: {
    base: "#fbfbfd",
    comp: "multiply",
    blobA: 0.5,
    cursor: "#c2cffa",
    cursorA: 0.22,
  },
  dark: {
    base: "#0c0c10",
    comp: "screen",
    blobA: 0.34,
    cursor: "#8ea2ff",
    cursorA: 0.3,
  },
};

// "Bold" direction (03): large, saturated blobs that strongly chase the cursor.
const BOLD = {
  pull: 0.075,
  parallax: 2.0,
  intensity: 1.18,
  layout: [
    { x: 0.32, y: 0.3, c: 0, r: 0.58, depth: 1.1 },
    { x: 0.74, y: 0.34, c: 1, r: 0.56, depth: 1.3 },
    { x: 0.6, y: 0.78, c: 3, r: 0.5, depth: 0.9 },
    { x: 0.22, y: 0.74, c: 2, r: 0.46, depth: 1.0 },
    { x: 0.5, y: 0.46, c: 4, r: 0.4, depth: 0.7 },
  ],
};

function hexA(hex: string, a: number) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}

export default function BackgroundGradient() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { theme } = useTheme();
  // Read by the animation loop each frame so theme changes apply live.
  const themeRef = useRef<ThemeConfig>(THEMES.light);

  useEffect(() => {
    themeRef.current = theme === "dark" ? THEMES.dark : THEMES.light;
  }, [theme]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reduce = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;

    let W = 0;
    let H = 0;
    const resize = () => {
      const DPR = Math.min(window.devicePixelRatio || 1, 2);
      W = window.innerWidth;
      H = window.innerHeight;
      canvas.width = Math.floor(W * DPR);
      canvas.height = Math.floor(H * DPR);
      canvas.style.width = `${W}px`;
      canvas.style.height = `${H}px`;
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    };
    resize();
    window.addEventListener("resize", resize);

    const blobs = BOLD.layout.map((b) => ({
      bx: b.x,
      by: b.y,
      color: COLORS[b.c % COLORS.length],
      rad: b.r,
      depth: b.depth,
      ph: Math.random() * Math.PI * 2,
      sp: 0.12 + Math.random() * 0.18,
      amp: 0.025 + Math.random() * 0.03,
    }));

    // Pointer: target (raw) vs eased, normalized to 0..1.
    let tmx = 0.5;
    let tmy = 0.5;
    let mx = 0.5;
    let my = 0.5;
    const onMove = (e: PointerEvent) => {
      tmx = e.clientX / W;
      tmy = e.clientY / H;
    };
    const onLeave = () => {
      tmx = 0.5;
      tmy = 0.5;
    };
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerleave", onLeave);

    const drawBlob = (
      cx: number,
      cy: number,
      r: number,
      color: string,
      alpha: number,
    ) => {
      const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
      g.addColorStop(0, hexA(color, alpha));
      g.addColorStop(0.55, hexA(color, alpha * 0.5));
      g.addColorStop(1, hexA(color, 0));
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();
    };

    let t = 0;
    let raf = 0;
    const frame = () => {
      const cfg = themeRef.current;
      t += reduce ? 0 : 0.006;
      mx += (tmx - mx) * 0.06;
      my += (tmy - my) * 0.06;

      ctx.globalCompositeOperation = "source-over";
      ctx.fillStyle = cfg.base;
      ctx.fillRect(0, 0, W, H);

      ctx.globalCompositeOperation = cfg.comp;
      const diag = Math.hypot(W, H);
      const ox = mx - 0.5;
      const oy = my - 0.5;

      for (const b of blobs) {
        const drift = reduce ? 0 : 1;
        const dx = Math.cos(t * b.sp + b.ph) * b.amp * drift;
        const dy = Math.sin(t * b.sp * 1.3 + b.ph) * b.amp * drift;
        // parallax with the pointer …
        const px = b.bx + dx + ox * b.depth * BOLD.parallax * 0.12;
        const py = b.by + dy + oy * b.depth * BOLD.parallax * 0.12;
        // … then a gentle pull toward it, scaled by depth.
        const gx = px + (mx - px) * BOLD.pull * b.depth * 3;
        const gy = py + (my - py) * BOLD.pull * b.depth * 3;
        drawBlob(
          gx * W,
          gy * H,
          b.rad * diag * 0.7,
          b.color,
          cfg.blobA * BOLD.intensity,
        );
      }

      // Cursor spotlight — the clearest interaction cue.
      drawBlob(
        mx * W,
        my * H,
        diag * 0.16,
        cfg.cursor,
        cfg.cursorA * BOLD.intensity,
      );

      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerleave", onLeave);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 -z-20 h-full w-full"
    />
  );
}
