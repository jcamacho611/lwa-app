import { useEffect, useRef } from "react";
import type { WorldPhase, WorldState } from "../lib/world-state";
import { WorldLayer } from "./WorldLayer";

type WorldCharacterProps = {
  position: "left" | "right" | "center";
  tone: "crimson" | "magenta" | "cyan";
  state: WorldState;
  phase: WorldPhase;
};

const PHASE_ACTIVITY: Record<WorldPhase, number> = {
  idle: 0.4,
  analyzing: 0.65,
  generating: 0.9,
  rendering: 1,
  ready: 0.45,
};

export function WorldCharacter({ position, tone, state, phase }: WorldCharacterProps) {
  const characterRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const node = characterRef.current;
    if (!node) {
      return;
    }

    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (media.matches) {
      node.style.setProperty("--character-drift-x", "0px");
      node.style.setProperty("--character-drift-y", "0px");
      node.style.setProperty("--character-breath", "1");
      node.style.setProperty("--character-tilt", "0deg");
      node.style.setProperty("--character-glow", phase === "ready" ? "0.52" : "0.28");
      node.style.setProperty("--character-eye-alpha", phase === "rendering" ? "0.9" : "0.44");
      return;
    }

    const activity = PHASE_ACTIVITY[phase];
    const seed = position === "left" ? 0.2 : position === "right" ? 0.8 : 1.4;
    let frame = 0;

    const tick = (time: number) => {
      const t = time * 0.001 + seed;
      const driftX = Math.sin(t * (0.38 + activity * 0.18)) * (6 + activity * 8);
      const driftY = Math.cos(t * (0.52 + activity * 0.22)) * (10 + activity * 12);
      const tilt = Math.sin(t * (0.28 + activity * 0.15)) * (1.4 + activity * 1.8);
      const breath = 1 + Math.sin(t * (0.58 + activity * 0.25)) * (0.014 + activity * 0.02);
      const glow = 0.24 + activity * 0.26 + (phase === "ready" ? 0.1 : 0) + Math.sin(t * 1.2) * 0.06;
      const eye = 0.18 + activity * 0.52 + Math.cos(t * 1.6) * 0.08;

      node.style.setProperty("--character-drift-x", `${driftX.toFixed(2)}px`);
      node.style.setProperty("--character-drift-y", `${driftY.toFixed(2)}px`);
      node.style.setProperty("--character-breath", `${breath.toFixed(4)}`);
      node.style.setProperty("--character-tilt", `${tilt.toFixed(2)}deg`);
      node.style.setProperty("--character-glow", `${Math.max(0.18, glow).toFixed(3)}`);
      node.style.setProperty("--character-eye-alpha", `${Math.max(0.12, eye).toFixed(3)}`);

      frame = window.requestAnimationFrame(tick);
    };

    frame = window.requestAnimationFrame(tick);
    return () => window.cancelAnimationFrame(frame);
  }, [phase, position]);

  return (
    <WorldLayer className="world-character-layer">
      <div
        ref={characterRef}
        className={`world-character world-character-${position} world-character-${tone}`}
        data-character-state={state}
        data-character-phase={phase}
        data-character-tone={tone}
      >
        <div className="world-character-shell">
          <div className="world-character-body" />
          <div className="world-character-aura" />
          <div className="world-character-glow" />
          <div className="world-character-sigil" />
          <div className="world-character-crown" />
          <div className="world-character-core" />
          <div className="world-character-veil" />
          <div className="world-character-eyes" />
        </div>
      </div>
    </WorldLayer>
  );
}
