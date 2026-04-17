"use client";

import { useEffect, useRef } from "react";

type AIBackgroundProps = {
  variant?: "workspace" | "home";
};

export function AIBackground({ variant = "workspace" }: AIBackgroundProps) {
  const backgroundRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const node = backgroundRef.current;
    if (!node || variant !== "home") {
      return;
    }

    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (media.matches) {
      node.style.setProperty("--ai-depth-x", "0px");
      node.style.setProperty("--ai-depth-y", "0px");
      node.style.setProperty("--ai-glow-x", "50%");
      node.style.setProperty("--ai-glow-y", "26%");
      return;
    }

    let frame = 0;

    const handlePointerMove = (event: PointerEvent) => {
      const width = window.innerWidth || 1;
      const height = window.innerHeight || 1;
      const normalizedX = event.clientX / width - 0.5;
      const normalizedY = event.clientY / height - 0.5;

      cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(() => {
        node.style.setProperty("--ai-depth-x", `${normalizedX * 28}px`);
        node.style.setProperty("--ai-depth-y", `${normalizedY * 22}px`);
        node.style.setProperty("--ai-glow-x", `${event.clientX}px`);
        node.style.setProperty("--ai-glow-y", `${event.clientY}px`);
      });
    };

    const handlePointerReset = () => {
      cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(() => {
        node.style.setProperty("--ai-depth-x", "0px");
        node.style.setProperty("--ai-depth-y", "0px");
        node.style.setProperty("--ai-glow-x", "50%");
        node.style.setProperty("--ai-glow-y", "26%");
      });
    };

    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    window.addEventListener("pointerleave", handlePointerReset);

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerleave", handlePointerReset);
    };
  }, [variant]);

  return (
    <div
      ref={backgroundRef}
      className={["ai-background", variant === "home" ? "ai-background-home" : "ai-background-workspace"].join(" ")}
      aria-hidden="true"
    >
      <div className="ai-depth-field" />

      <div className="ai-orb ai-orb-a" />
      <div className="ai-orb ai-orb-b" />
      <div className="ai-orb ai-orb-c" />
      <div className="ai-orb ai-orb-d" />

      <div className="ai-grid" />
      <div className="ai-scan-line" />

      {variant === "home" ? (
        <>
          <div className="ai-particle-field" />
          <div className="ai-stars" />
          <div className="ai-fog ai-fog-a" />
          <div className="ai-fog ai-fog-b" />
          <div className="ai-beam ai-beam-a" />
          <div className="ai-beam ai-beam-b" />
          <div className="ai-shimmer ai-shimmer-a" />

          <div className="ai-silhouette ai-silhouette-a">
            <div className="ai-aura-halo" />
            <div className="ai-figure-core" />
            <div className="ai-eye-glow ai-eye-glow-a" />
          </div>

          <div className="ai-silhouette ai-silhouette-b">
            <div className="ai-aura-halo" />
            <div className="ai-figure-core" />
            <div className="ai-eye-glow ai-eye-glow-b" />
          </div>
        </>
      ) : null}
    </div>
  );
}
