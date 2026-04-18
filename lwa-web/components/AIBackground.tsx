"use client";

import { useEffect, useRef } from "react";

type AIBackgroundProps = {
  variant?: "workspace" | "home";
};

export function AIBackground({ variant = "workspace" }: AIBackgroundProps) {
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) {
      return;
    }

    const media = window.matchMedia("(prefers-reduced-motion: reduce)");

    const resetDepth = () => {
      root.style.setProperty("--lwa-ai-depth-x", "0px");
      root.style.setProperty("--lwa-ai-depth-y", "0px");
      root.style.setProperty("--lwa-ai-glow-x", "50%");
      root.style.setProperty("--lwa-ai-glow-y", variant === "home" ? "24%" : "20%");
    };

    resetDepth();

    if (media.matches) {
      return;
    }

    const handlePointerMove = (event: PointerEvent) => {
      const normalizedX = event.clientX / window.innerWidth - 0.5;
      const normalizedY = event.clientY / window.innerHeight - 0.5;

      root.style.setProperty("--lwa-ai-depth-x", `${normalizedX * 28}px`);
      root.style.setProperty("--lwa-ai-depth-y", `${normalizedY * 22}px`);
      root.style.setProperty("--lwa-ai-glow-x", `${event.clientX}px`);
      root.style.setProperty("--lwa-ai-glow-y", `${event.clientY}px`);
    };

    const handleLeave = () => resetDepth();

    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    window.addEventListener("blur", handleLeave);

    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("blur", handleLeave);
    };
  }, [variant]);

  return (
    <>
      <div
        ref={rootRef}
        className={`lwa-ai-bg ${variant === "home" ? "lwa-ai-bg-home" : "lwa-ai-bg-workspace"}`}
        aria-hidden="true"
      >
        <div className="lwa-ai-depth-field" />
        <div className="lwa-ai-orb lwa-ai-orb-a" />
        <div className="lwa-ai-orb lwa-ai-orb-b" />
        <div className="lwa-ai-orb lwa-ai-orb-c" />
        <div className="lwa-ai-orb lwa-ai-orb-d" />
        <div className="lwa-ai-grid" />
        <div className="lwa-ai-particle-field" />
        <div className="lwa-ai-stars" />
        <div className="lwa-ai-fog lwa-ai-fog-a" />
        <div className="lwa-ai-fog lwa-ai-fog-b" />
        <div className="lwa-ai-beam lwa-ai-beam-a" />
        <div className="lwa-ai-beam lwa-ai-beam-b" />
        <div className="lwa-ai-shimmer lwa-ai-shimmer-a" />
        <div className="lwa-ai-scan-line" />
        <div className="lwa-ai-silhouette lwa-ai-silhouette-a">
          <div className="lwa-ai-aura-halo" />
          <div className="lwa-ai-figure-core" />
          <div className="lwa-ai-eye-glow lwa-ai-eye-glow-a" />
        </div>
        <div className="lwa-ai-silhouette lwa-ai-silhouette-b">
          <div className="lwa-ai-aura-halo" />
          <div className="lwa-ai-figure-core" />
          <div className="lwa-ai-eye-glow lwa-ai-eye-glow-b" />
        </div>
      </div>

      <style jsx global>{`
        @keyframes lwa-ai-orb-drift-a {
          0% { transform: translate3d(0, 0, 0) scale(1); }
          50% { transform: translate3d(32px, -24px, 0) scale(1.06); }
          100% { transform: translate3d(0, 0, 0) scale(1); }
        }

        @keyframes lwa-ai-orb-drift-b {
          0% { transform: translate3d(0, 0, 0) scale(1); }
          50% { transform: translate3d(-28px, 20px, 0) scale(1.05); }
          100% { transform: translate3d(0, 0, 0) scale(1); }
        }

        @keyframes lwa-ai-orb-drift-c {
          0% { transform: translate3d(0, 0, 0) scale(1); }
          50% { transform: translate3d(24px, 18px, 0) scale(1.04); }
          100% { transform: translate3d(0, 0, 0) scale(1); }
        }

        @keyframes lwa-ai-pulse {
          0%, 100% { opacity: 0.42; }
          50% { opacity: 0.74; }
        }

        @keyframes lwa-ai-grid-breathe {
          0%, 100% { opacity: 0.18; }
          50% { opacity: 0.3; }
        }

        @keyframes lwa-ai-scan-line {
          0% { transform: translateY(-120%); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: translateY(100vh); opacity: 0; }
        }

        @keyframes lwa-ai-particle-drift {
          0% { transform: translate3d(0, 0, 0) scale(1); }
          50% { transform: translate3d(-2%, -3%, 0) scale(1.03); }
          100% { transform: translate3d(2%, 2%, 0) scale(0.98); }
        }

        @keyframes lwa-ai-fog-drift {
          0% { transform: translate3d(-3%, 0, 0) scale(1); opacity: 0.14; }
          50% { transform: translate3d(2%, -2%, 0) scale(1.04); opacity: 0.24; }
          100% { transform: translate3d(4%, 2%, 0) scale(1.08); opacity: 0.16; }
        }

        @keyframes lwa-ai-depth-drift {
          0%, 100% { opacity: 0.22; transform: translate3d(0, 0, 0) scale(1); }
          50% { opacity: 0.34; transform: translate3d(2%, -3%, 0) scale(1.06); }
        }

        @keyframes lwa-ai-silhouette-float {
          0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
          50% { transform: translate3d(0, -12px, 0) scale(1.02); }
        }

        @keyframes lwa-ai-aura-flicker {
          0%, 100% { opacity: 0.16; }
          40% { opacity: 0.3; }
          54% { opacity: 0.36; }
          72% { opacity: 0.2; }
        }

        @keyframes lwa-ai-eye-flicker {
          0%, 86%, 100% { opacity: 0.18; filter: blur(6px); }
          88% { opacity: 0.62; filter: blur(2px); }
          92% { opacity: 0.72; filter: blur(1px); }
          94% { opacity: 0.24; }
        }

        @keyframes lwa-ai-lightning {
          0%, 89%, 100% { opacity: 0; }
          90% { opacity: 0.06; }
          92% { opacity: 0.14; }
          96% { opacity: 0.08; }
        }

        .lwa-ai-bg {
          --lwa-ai-depth-x: 0px;
          --lwa-ai-depth-y: 0px;
          --lwa-ai-glow-x: 50%;
          --lwa-ai-glow-y: 24%;
          position: fixed;
          inset: 0;
          overflow: hidden;
          pointer-events: none;
          z-index: 0;
        }

        .lwa-ai-bg-workspace {
          opacity: 0.82;
        }

        .lwa-ai-bg-home {
          opacity: 1;
        }

        .lwa-ai-depth-field,
        .lwa-ai-orb,
        .lwa-ai-grid,
        .lwa-ai-particle-field,
        .lwa-ai-stars,
        .lwa-ai-fog,
        .lwa-ai-beam,
        .lwa-ai-shimmer,
        .lwa-ai-scan-line,
        .lwa-ai-silhouette {
          position: absolute;
          inset: 0;
          pointer-events: none;
        }

        .lwa-ai-depth-field {
          inset: -8%;
          background:
            radial-gradient(circle at var(--lwa-ai-glow-x) var(--lwa-ai-glow-y), rgba(255, 45, 166, 0.16), transparent 18%),
            radial-gradient(circle at 14% 18%, rgba(255, 0, 60, 0.18), transparent 28%),
            radial-gradient(circle at 74% 20%, rgba(0, 231, 255, 0.12), transparent 22%),
            radial-gradient(circle at 52% 74%, rgba(161, 0, 47, 0.12), transparent 24%);
          transform: translate3d(calc(var(--lwa-ai-depth-x) * 0.28), calc(var(--lwa-ai-depth-y) * 0.28), 0);
          filter: blur(20px);
          animation: lwa-ai-depth-drift 18s ease-in-out infinite;
        }

        .lwa-ai-orb {
          border-radius: 9999px;
          filter: blur(90px);
          will-change: transform, opacity;
        }

        .lwa-ai-orb-a {
          top: -140px;
          left: -90px;
          width: 520px;
          height: 520px;
          background: radial-gradient(circle, rgba(255, 0, 60, 0.2) 0%, transparent 70%);
          animation: lwa-ai-orb-drift-a 18s ease-in-out infinite, lwa-ai-pulse 8s ease-in-out infinite;
        }

        .lwa-ai-orb-b {
          top: 48px;
          right: -60px;
          width: 440px;
          height: 440px;
          background: radial-gradient(circle, rgba(255, 45, 166, 0.18) 0%, transparent 70%);
          animation: lwa-ai-orb-drift-b 22s ease-in-out infinite, lwa-ai-pulse 10s ease-in-out infinite 1.4s;
        }

        .lwa-ai-orb-c {
          right: 12%;
          bottom: 14%;
          width: 360px;
          height: 360px;
          background: radial-gradient(circle, rgba(0, 231, 255, 0.14) 0%, transparent 70%);
          animation: lwa-ai-orb-drift-c 16s ease-in-out infinite, lwa-ai-pulse 7s ease-in-out infinite 0.8s;
        }

        .lwa-ai-orb-d {
          left: 8%;
          bottom: 28%;
          width: 280px;
          height: 280px;
          background: radial-gradient(circle, rgba(122, 22, 44, 0.14) 0%, transparent 70%);
          animation: lwa-ai-orb-drift-b 26s ease-in-out infinite reverse, lwa-ai-pulse 9s ease-in-out infinite 2.2s;
        }

        .lwa-ai-grid {
          background-image:
            linear-gradient(rgba(255, 255, 255, 0.028) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.028) 1px, transparent 1px);
          background-size: 120px 120px;
          mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.46), transparent 90%);
          animation: lwa-ai-grid-breathe 12s ease-in-out infinite;
        }

        .lwa-ai-particle-field {
          background-image:
            radial-gradient(circle at 18% 22%, rgba(255, 255, 255, 0.16) 0 1px, transparent 2px),
            radial-gradient(circle at 36% 48%, rgba(255, 107, 139, 0.18) 0 1px, transparent 2px),
            radial-gradient(circle at 62% 26%, rgba(0, 231, 255, 0.18) 0 1px, transparent 2px),
            radial-gradient(circle at 74% 58%, rgba(255, 45, 166, 0.14) 0 1px, transparent 2px),
            radial-gradient(circle at 88% 18%, rgba(255, 255, 255, 0.14) 0 1px, transparent 2px);
          opacity: 0.24;
          transform: translate3d(calc(var(--lwa-ai-depth-x) * -0.2), calc(var(--lwa-ai-depth-y) * -0.16), 0);
          animation: lwa-ai-particle-drift 24s linear infinite alternate;
        }

        .lwa-ai-stars {
          background-image:
            radial-gradient(circle at 12% 16%, rgba(255, 107, 139, 0.66) 0 1px, transparent 2px),
            radial-gradient(circle at 32% 28%, rgba(255, 107, 139, 0.28) 0 1px, transparent 2px),
            radial-gradient(circle at 66% 22%, rgba(0, 231, 255, 0.42) 0 1px, transparent 2px),
            radial-gradient(circle at 78% 34%, rgba(255, 107, 139, 0.24) 0 1px, transparent 2px),
            radial-gradient(circle at 58% 12%, rgba(0, 231, 255, 0.32) 0 1px, transparent 2px);
          opacity: 0.24;
          animation: lwa-ai-particle-drift 20s linear infinite alternate;
        }

        .lwa-ai-fog {
          filter: blur(56px);
          opacity: 0.2;
        }

        .lwa-ai-fog-a {
          background: radial-gradient(circle at 18% 24%, rgba(122, 22, 44, 0.18), transparent 28%);
          animation: lwa-ai-fog-drift 16s ease-in-out infinite alternate;
        }

        .lwa-ai-fog-b {
          background: radial-gradient(circle at 84% 18%, rgba(255, 45, 166, 0.12), transparent 26%);
          animation: lwa-ai-fog-drift 20s ease-in-out infinite alternate-reverse;
        }

        .lwa-ai-beam {
          opacity: 0.14;
          mix-blend-mode: screen;
        }

        .lwa-ai-beam-a {
          background: linear-gradient(120deg, transparent 0%, rgba(255, 0, 60, 0.1) 46%, transparent 72%);
          transform: translateY(-6%);
        }

        .lwa-ai-beam-b {
          background: linear-gradient(92deg, transparent 0%, rgba(0, 231, 255, 0.06) 42%, transparent 78%);
          animation: lwa-ai-lightning 12s ease-in-out infinite;
        }

        .lwa-ai-shimmer-a {
          background: radial-gradient(circle at 72% 16%, rgba(255, 45, 166, 0.08), transparent 18%);
          animation: lwa-ai-lightning 18s ease-in-out infinite;
        }

        .lwa-ai-scan-line {
          inset: 0 auto auto 0;
          right: 0;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(255, 0, 60, 0.14), rgba(0, 231, 255, 0.12), transparent);
          animation: lwa-ai-scan-line 14s linear infinite;
          animation-delay: 4s;
        }

        .lwa-ai-silhouette {
          bottom: -2%;
          inset: auto auto -2% auto;
          width: min(34vw, 420px);
          aspect-ratio: 0.68;
          opacity: 0.72;
          filter: saturate(1.06);
          transform: translate3d(calc(var(--lwa-ai-depth-x) * -0.28), calc(var(--lwa-ai-depth-y) * -0.22), 0);
          animation: lwa-ai-silhouette-float 14s ease-in-out infinite;
        }

        .lwa-ai-silhouette-a {
          right: 4%;
          opacity: 0.78;
        }

        .lwa-ai-silhouette-b {
          left: -2%;
          bottom: 4%;
          width: min(24vw, 280px);
          opacity: 0.4;
          animation-duration: 18s;
          transform: translate3d(calc(var(--lwa-ai-depth-x) * 0.18), calc(var(--lwa-ai-depth-y) * -0.16), 0);
        }

        .lwa-ai-aura-halo,
        .lwa-ai-figure-core,
        .lwa-ai-eye-glow {
          position: absolute;
          inset: 0;
        }

        .lwa-ai-aura-halo {
          border-radius: 50% 50% 40% 40%;
          background:
            radial-gradient(circle at 50% 28%, rgba(255, 45, 166, 0.18), transparent 28%),
            radial-gradient(circle at 54% 52%, rgba(255, 0, 60, 0.16), transparent 34%),
            radial-gradient(circle at 50% 70%, rgba(0, 231, 255, 0.08), transparent 44%);
          filter: blur(24px);
          animation: lwa-ai-aura-flicker 7.8s ease-in-out infinite;
        }

        .lwa-ai-figure-core {
          background:
            radial-gradient(circle at 50% 18%, rgba(255, 255, 255, 0.06), transparent 12%),
            radial-gradient(circle at 50% 24%, rgba(18, 7, 10, 0.88) 0 10%, transparent 11%),
            radial-gradient(circle at 50% 38%, rgba(14, 6, 9, 0.9) 0 16%, transparent 17%),
            radial-gradient(circle at 50% 62%, rgba(10, 4, 7, 0.88) 0 24%, transparent 25%),
            linear-gradient(180deg, rgba(8, 4, 6, 0) 0%, rgba(8, 4, 6, 0.92) 26%, rgba(5, 4, 5, 0.98) 100%);
          clip-path: polygon(50% 4%, 58% 10%, 64% 20%, 68% 31%, 72% 46%, 78% 64%, 74% 100%, 26% 100%, 22% 64%, 28% 46%, 32% 31%, 36% 20%, 42% 10%);
          box-shadow:
            0 0 60px rgba(255, 0, 60, 0.08),
            0 0 100px rgba(0, 231, 255, 0.04);
        }

        .lwa-ai-eye-glow {
          inset: 18% 34% auto 34%;
          height: 18%;
          background:
            radial-gradient(circle at 30% 52%, rgba(255, 45, 166, 0.7) 0 12%, transparent 24%),
            radial-gradient(circle at 70% 52%, rgba(0, 231, 255, 0.66) 0 12%, transparent 24%);
          filter: blur(6px);
          opacity: 0.24;
        }

        .lwa-ai-eye-glow-a {
          animation: lwa-ai-eye-flicker 8.8s ease-in-out infinite;
        }

        .lwa-ai-eye-glow-b {
          animation: lwa-ai-eye-flicker 10.4s ease-in-out infinite 1.2s;
        }

        @media (prefers-reduced-motion: reduce) {
          .lwa-ai-depth-field,
          .lwa-ai-orb,
          .lwa-ai-grid,
          .lwa-ai-particle-field,
          .lwa-ai-stars,
          .lwa-ai-fog,
          .lwa-ai-beam,
          .lwa-ai-shimmer,
          .lwa-ai-scan-line,
          .lwa-ai-silhouette,
          .lwa-ai-aura-halo,
          .lwa-ai-eye-glow {
            animation: none !important;
            transform: none !important;
          }
        }

        @media (max-width: 1024px) {
          .lwa-ai-silhouette-b {
            display: none;
          }

          .lwa-ai-depth-field {
            opacity: 0.82;
          }
        }

        @media (max-width: 768px) {
          .lwa-ai-silhouette-a {
            width: min(56vw, 260px);
            right: -8%;
            opacity: 0.42;
          }

          .lwa-ai-orb-a,
          .lwa-ai-orb-b {
            width: 320px;
            height: 320px;
            filter: blur(72px);
          }

          .lwa-ai-particle-field,
          .lwa-ai-beam-b,
          .lwa-ai-shimmer-a {
            opacity: 0.5;
          }
        }
      `}</style>
    </>
  );
}
