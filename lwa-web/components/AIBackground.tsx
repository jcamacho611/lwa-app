"use client";

import type { WorldMode, WorldSignal, WorldState } from "../lib/world-state";
import { WorldEngine } from "./WorldEngine";

type AIBackgroundProps = {
  variant?: "workspace" | "home";
  worldState?: WorldState;
  generationMode?: WorldMode;
  signal?: WorldSignal;
};

export function AIBackground({
  variant = "workspace",
  worldState = "idle",
  generationMode = "quick",
  signal = "idle",
}: AIBackgroundProps) {
  return <WorldEngine variant={variant} worldState={worldState} generationMode={generationMode} signal={signal} />;
}
