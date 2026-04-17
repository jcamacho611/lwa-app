"use client";

import { useMemo, useRef } from "react";
import { usePointerParallax } from "../../hooks/usePointerParallax";

export default function InteractiveMythicScene() {
  const ref = useRef<HTMLDivElement>(null);
  usePointerParallax(ref, {
    rotate: 0,
    shiftSmall: 6,
    shiftMedium: 16,
    shiftLarge: 24,
  });

  const particles = useMemo(
    () =>
      Array.from({ length: 20 }).map((_, index) => ({
        id: index,
        left: `${(index * 13.7) % 100}%`,
        top: `${(index * 17.3) % 100}%`,
        duration: `${5 + (index % 5)}s`,
        delay: `${index * 0.18}s`,
      })),
    [],
  );

  return (
    <div ref={ref} className="mythic-scene pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden>
      <div className="mythic-scene-base absolute inset-0" />

      <div
        className="mythic-scene-layer mythic-scene-layer-back absolute inset-0"
        style={{
          transform: "translate3d(var(--px-sm, 0px), var(--py-sm, 0px), 0)",
        }}
      />

      <div
        className="mythic-figure mythic-figure-left absolute left-0 top-0 h-full w-[34%]"
        style={{
          transform: "translate3d(var(--px-lg, 0px), var(--py-md, 0px), 0)",
        }}
      >
        <span className="mythic-eye mythic-eye-left-a" />
        <span className="mythic-eye mythic-eye-left-b" />
      </div>

      <div
        className="mythic-figure mythic-figure-right absolute right-0 top-0 h-full w-[34%]"
        style={{
          transform: "translate3d(calc(var(--px-lg, 0px) * -1), var(--py-md, 0px), 0)",
        }}
      >
        <span className="mythic-eye mythic-eye-right-a" />
        <span className="mythic-eye mythic-eye-right-b" />
      </div>

      <div
        className="mythic-fog mythic-fog-a absolute inset-x-[-10%] bottom-[-10%] h-[42%]"
        style={{
          transform: "translate3d(var(--px-sm, 0px), var(--py-sm, 0px), 0)",
        }}
      />
      <div
        className="mythic-fog mythic-fog-b absolute inset-x-[-12%] top-[10%] h-[28%]"
        style={{
          transform: "translate3d(calc(var(--px-sm, 0px) * -1), calc(var(--py-sm, 0px) * -1), 0)",
        }}
      />

      <div className="absolute inset-0">
        {particles.map((particle) => (
          <span
            key={particle.id}
            className="mythic-particle absolute h-[2px] w-[2px] rounded-full"
            style={{
              left: particle.left,
              top: particle.top,
              animationDuration: particle.duration,
              animationDelay: particle.delay,
            }}
          />
        ))}
      </div>

      <div className="mythic-lightning absolute inset-0" />
      <div className="mythic-vignette absolute inset-0" />
    </div>
  );
}
