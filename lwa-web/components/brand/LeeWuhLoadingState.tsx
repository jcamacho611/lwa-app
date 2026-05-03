"use client";

import { LeeWuhMascot } from "./LeeWuhMascot";
import { type LeeWuhState } from "../../lib/brand/lee-wuh";

type LeeWuhLoadingStateProps = {
  phase?: "ingesting" | "analyzing" | "composing" | "rendering" | "packaging" | "complete";
  title?: string;
  body?: string;
};

const phaseToState: Record<NonNullable<LeeWuhLoadingStateProps["phase"]>, LeeWuhState> = {
  ingesting: "ingesting",
  analyzing: "thinking",
  composing: "composing",
  rendering: "rendering",
  packaging: "watching",
  complete: "success",
};

export function LeeWuhLoadingState({
  phase = "analyzing",
  title = "Lee-Wuh is working",
  body = "Finding the strongest move and preparing the output.",
}: LeeWuhLoadingStateProps) {
  return (
    <div className="rounded-[28px] border border-purple-300/20 bg-black/50 p-6 text-center">
      <LeeWuhMascot state={phaseToState[phase]} size="lg" showAura showLabel />

      <div className="mx-auto mt-5 max-w-md">
        <p className="text-xs uppercase tracking-[0.28em] text-purple-200/70">{phase}</p>
        <h3 className="mt-2 text-2xl font-semibold text-white">{title}</h3>
        <p className="mt-2 text-sm leading-6 text-white/60">{body}</p>
      </div>

      <div className="mx-auto mt-5 h-2 max-w-sm overflow-hidden rounded-full bg-white/10">
        <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-yellow-300 to-purple-500 motion-safe:animate-pulse" />
      </div>
    </div>
  );
}
