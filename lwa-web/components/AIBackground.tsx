"use client";

/**
 * AIBackground — living computational background system.
 *
 * Renders four animated gradient orbs, a breathing grid overlay, and a
 * slow scan-line sweep. All motion is CSS-driven (no canvas, no JS RAF loop)
 * so it stays at 60 fps with zero layout thrash. Respects prefers-reduced-motion
 * via the CSS media query in globals.css.
 */

import React from "react";

type AIBackgroundProps = {
  variant?: "workspace" | "home";
};

export function AIBackground({ variant = "workspace" }: AIBackgroundProps) {
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

      {variant === "home" ? (
        <>
          <div className="ai-stars" aria-hidden="true" />
          <div className="ai-fog ai-fog-a" aria-hidden="true" />
          <div className="ai-fog ai-fog-b" aria-hidden="true" />
          <div className="ai-beam ai-beam-a" aria-hidden="true" />
          <div className="ai-beam ai-beam-b" aria-hidden="true" />
          <div className="ai-shimmer ai-shimmer-a" aria-hidden="true" />
        </>
      ) : null}

      {/* Seedance premium background — non-blocking, falls back silently */}
      {variant === "home" && <SeedancePremiumLayer />}
    </>
  );
}

/**
 * Seedance premium background layer.
 *
 * Attempts to load a Seedance-generated background video asset from the
 * backend. Falls back to nothing (existing AIBackground layers stay
 * visible underneath). Never blocks initial render.
 */
function SeedancePremiumLayer() {
  const [assetUrl, setAssetUrl] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;

    async function checkSeedance() {
      try {
        const apiBase =
          process.env.NEXT_PUBLIC_API_URL ??
          process.env.NEXT_PUBLIC_BACKEND_URL ??
          "";
        if (!apiBase) return;

        const res = await fetch(`${apiBase}/v1/seedance/background`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt:
              "Mythic void with crimson energy veins and slow drifting fog",
            style_preset: "mythic-void",
            duration_seconds: 8,
            aspect_ratio: "16:9",
          }),
        });
        if (!res.ok) return;
        const data = await res.json();
        if (!data.enabled || !data.job?.job_id) return;

        // Poll for completion (max ~2 minutes)
        const jobId = data.job.job_id;
        for (let i = 0; i < 24; i++) {
          await new Promise((r) => setTimeout(r, 5000));
          if (cancelled) return;
          const pollRes = await fetch(
            `${apiBase}/v1/seedance/jobs/${jobId}`,
          );
          if (!pollRes.ok) break;
          const pollData = await pollRes.json();
          if (
            pollData.job?.status === "completed" &&
            pollData.job?.asset_url
          ) {
            if (!cancelled) setAssetUrl(pollData.job.asset_url);
            return;
          }
          if (pollData.job?.status === "failed") return;
        }
      } catch {
        // Seedance unavailable — fall back silently
      }
    }

    checkSeedance();
    return () => {
      cancelled = true;
    };
  }, []);

  if (!assetUrl) return null;

  return (
    <div
      className="pointer-events-none fixed inset-0 z-[1] overflow-hidden"
      aria-hidden="true"
    >
      <video
        autoPlay
        loop
        muted
        playsInline
        className="h-full w-full object-cover opacity-30"
        src={assetUrl}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/40 to-black" />
    </div>
  );
}
