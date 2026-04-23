"use client";

import { useEffect, useRef, useState } from "react";
import { resolveCharacterState, type WorldMode, type WorldPhase, type WorldSignal, type WorldState } from "../lib/world-state";
import { WorldCharacter } from "./WorldCharacter";
import { WorldEffects } from "./WorldEffects";

type WorldEngineProps = {
  variant?: "workspace" | "home";
  worldState?: WorldState;
  worldPhase?: WorldPhase;
  generationMode?: WorldMode;
  signal?: WorldSignal;
};

const EVENT_SEQUENCE: Record<WorldSignal, Array<"scan" | "flare" | "surge">> = {
  idle: ["scan", "flare"],
  hover: ["scan", "flare", "surge"],
  focus: ["flare", "scan", "surge"],
  generating: ["surge", "flare", "scan"],
  complete: ["flare", "surge", "scan"],
};

export function WorldEngine({
  variant = "workspace",
  worldState = "idle",
  worldPhase = "idle",
  generationMode = "quick",
  signal = "idle",
}: WorldEngineProps) {
  const backgroundRef = useRef<HTMLDivElement | null>(null);
  const pointerResetRef = useRef<number | null>(null);
  const [pointerActive, setPointerActive] = useState(false);
  const [eventKind, setEventKind] = useState<"scan" | "flare" | "surge">("scan");
  const [eventEpoch, setEventEpoch] = useState(0);

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
      node.style.setProperty("--world-pointer-strength", "0");
      return;
    }

    let frame = 0;

    const resetPointer = () => {
      setPointerActive(false);
      node.style.setProperty("--ai-depth-x", "0px");
      node.style.setProperty("--ai-depth-y", "0px");
      node.style.setProperty("--ai-glow-x", "50%");
      node.style.setProperty("--ai-glow-y", "26%");
      node.style.setProperty("--world-pointer-strength", "0");
    };

    const handlePointerMove = (event: PointerEvent) => {
      const width = window.innerWidth || 1;
      const height = window.innerHeight || 1;
      const normalizedX = event.clientX / width - 0.5;
      const normalizedY = event.clientY / height - 0.5;
      const strength = Math.min(1, Math.abs(normalizedX) + Math.abs(normalizedY));

      if (pointerResetRef.current) {
        window.clearTimeout(pointerResetRef.current);
      }
      setPointerActive(true);

      cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(() => {
        node.style.setProperty("--ai-depth-x", `${normalizedX * 30}px`);
        node.style.setProperty("--ai-depth-y", `${normalizedY * 24}px`);
        node.style.setProperty("--ai-glow-x", `${event.clientX}px`);
        node.style.setProperty("--ai-glow-y", `${event.clientY}px`);
        node.style.setProperty("--world-pointer-strength", `${strength.toFixed(2)}`);
      });

      pointerResetRef.current = window.setTimeout(resetPointer, 1800);
    };

    const handlePointerReset = () => {
      if (pointerResetRef.current) {
        window.clearTimeout(pointerResetRef.current);
      }
      cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(resetPointer);
    };

    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    window.addEventListener("pointerleave", handlePointerReset);

    return () => {
      if (pointerResetRef.current) {
        window.clearTimeout(pointerResetRef.current);
      }
      cancelAnimationFrame(frame);
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerleave", handlePointerReset);
    };
  }, [variant]);

  useEffect(() => {
    const node = backgroundRef.current;
    if (!node || variant !== "home") {
      return;
    }

    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (media.matches) {
      return;
    }

    let cancelled = false;
    let timeout = 0;

    const schedule = () => {
      const choices = EVENT_SEQUENCE[signal];
      const nextEvent = choices[Math.floor(Math.random() * choices.length)];
      const delayBase = worldState === "surge" ? 2400 : generationMode === "pro" ? 4200 : 5600;
      timeout = window.setTimeout(() => {
        if (cancelled) {
          return;
        }
        setEventKind(nextEvent);
        setEventEpoch((current) => current + 1);
        schedule();
      }, delayBase + Math.round(Math.random() * 1600));
    };

    schedule();

    return () => {
      cancelled = true;
      window.clearTimeout(timeout);
    };
  }, [generationMode, signal, variant, worldState]);

  return (
    <div
      ref={backgroundRef}
      className={[
        "ai-background",
        variant === "home" ? "ai-background-home world-engine world-engine-home" : "ai-background-workspace world-engine world-engine-workspace",
      ].join(" ")}
      data-world-state={worldState}
      data-world-phase={worldPhase}
      data-world-mode={generationMode}
      data-world-signal={signal}
      data-pointer-active={pointerActive ? "true" : "false"}
      aria-hidden="true"
    >
      <div className="world-source-art world-source-art-main">
        <img src="/brand-source/world/Celestial gods and chatbot interface.png" alt="" />
      </div>
      <div className="world-source-art world-source-art-council">
        <img src="/brand-source/characters/d394931b-1f61-48fb-984c-1258d72e5ab4.png" alt="" />
      </div>
      <div className="world-source-art world-source-art-command">
        <img src="/brand-source/world/24083f08-e428-4b99-ac75-3a10d43579dd.png" alt="" />
      </div>
      <div className="world-source-art world-source-art-mask">
        <img src="/brand-source/world/FullSizeRender.jpg" alt="" />
      </div>
      <WorldEffects variant={variant} phase={worldPhase} eventKind={eventKind} eventEpoch={eventEpoch} />

      {variant === "home" ? (
        <>
          <WorldCharacter position="left" tone="magenta" state={resolveCharacterState(0, worldState)} phase={worldPhase} />
          <WorldCharacter position="right" tone="cyan" state={resolveCharacterState(1, worldState)} phase={worldPhase} />
        </>
      ) : (
        <>
          <WorldCharacter position="left" tone="magenta" state={resolveCharacterState(0, worldState)} phase={worldPhase} />
          <WorldCharacter position="right" tone="cyan" state={resolveCharacterState(1, worldState)} phase={worldPhase} />
        </>
      )}
    </div>
  );
}
