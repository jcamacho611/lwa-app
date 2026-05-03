"use client";

import { getLeeWuhMessage, type LeeWuhState } from "../../lib/brand/lee-wuh";
import { LeeWuhMascot } from "./LeeWuhMascot";

type LeeWuhPresenceProps = {
  screen?: "home" | "generate" | "video_os" | "loading" | "results" | "empty" | "error";
  state?: LeeWuhState;
  message?: string;
  compact?: boolean;
  className?: string;
};

function cn(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(" ");
}

export function LeeWuhPresence({
  screen = "home",
  state = "idle",
  message,
  compact = false,
  className,
}: LeeWuhPresenceProps) {
  return (
    <aside
      className={cn(
        "rounded-3xl border border-yellow-300/15 bg-black/45 p-4 shadow-2xl shadow-black/30 backdrop-blur",
        "bg-[radial-gradient(circle_at_top_right,rgba(139,61,255,0.18),transparent_45%)]",
        compact ? "flex items-center gap-3" : "space-y-3",
        className,
      )}
      data-screen={screen}
    >
      <LeeWuhMascot size={compact ? "sm" : "md"} state={state} showAura={!compact} />

      <div>
        <p className="text-[10px] uppercase tracking-[0.28em] text-yellow-200/70">
          Lee-Wuh says
        </p>
        <p className="mt-1 text-sm leading-6 text-white/75">
          {message || getLeeWuhMessage(state)}
        </p>
      </div>
    </aside>
  );
}
