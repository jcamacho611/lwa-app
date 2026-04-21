"use client";

import type { WorldMode, WorldPhase, WorldSignal, WorldState } from "../lib/world-state";
import { WorldEngine } from "./WorldEngine";

type AIBackgroundProps = {
  variant?: "workspace" | "home";
  worldState?: WorldState;
  worldPhase?: WorldPhase;
  generationMode?: WorldMode;
  signal?: WorldSignal;
};

export function AIBackground({
  variant = "workspace",
  worldState = "idle",
  worldPhase = "idle",
  generationMode = "quick",
  signal = "idle",
}: AIBackgroundProps) {
  return <WorldEngine variant={variant} worldState={worldState} worldPhase={worldPhase} generationMode={generationMode} signal={signal} />;
}
