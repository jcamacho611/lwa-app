"use client";

/**
 * AIBackground — living computational background system.
 *
 * Renders four animated gradient orbs, a breathing grid overlay, and a
 * slow scan-line sweep. All motion is CSS-driven (no canvas, no JS RAF loop)
 * so it stays at 60 fps with zero layout thrash. Respects prefers-reduced-motion
 * via the CSS media query in globals.css.
 */
export function AIBackground() {
  return (
    <>
      {/* Animated gradient orbs */}
      <div className="ai-orb ai-orb-a" aria-hidden="true" />
      <div className="ai-orb ai-orb-b" aria-hidden="true" />
      <div className="ai-orb ai-orb-c" aria-hidden="true" />
      <div className="ai-orb ai-orb-d" aria-hidden="true" />

      {/* Breathing grid */}
      <div className="ai-grid" aria-hidden="true" />

      {/* Scan line sweep */}
      <div className="ai-scan-line" aria-hidden="true" />
    </>
  );
}
