"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

type LeeWuhMood = "idle" | "thinking" | "excited" | "marketplace" | "realm";

type LeeWuhAction = {
  label: string;
  href: string;
  detail: string;
  mood: LeeWuhMood;
};

const actions: LeeWuhAction[] = [
  {
    label: "Generate clips",
    href: "/generate",
    detail: "Drop one source and let LWA find the best moments.",
    mood: "excited",
  },
  {
    label: "Explore marketplace",
    href: "/marketplace",
    detail: "Find paid creative work, campaigns, and clipping tasks.",
    mood: "marketplace",
  },
  {
    label: "Post a job",
    href: "/marketplace/post-job",
    detail: "Create a prepaid or partially paid creator task.",
    mood: "marketplace",
  },
  {
    label: "Start campaign",
    href: "/campaigns",
    detail: "Package requirements, assets, submissions, and review.",
    mood: "thinking",
  },
  {
    label: "Enter realm",
    href: "/realm",
    detail: "Step into the Lee-Wuh world and game layer.",
    mood: "realm",
  },
  {
    label: "Open Company OS",
    href: "/company-os",
    detail: "See the full LWA operating system.",
    mood: "thinking",
  },
];

function moodLine(mood: LeeWuhMood) {
  switch (mood) {
    case "excited":
      return "Wussup. Feed me one source and I’ll find what deserves to move.";
    case "marketplace":
      return "Money flows when the work has a place to land. Pick the market path.";
    case "realm":
      return "You want the world? Step through the gate.";
    case "thinking":
      return "I can guide the next move. Choose the lane.";
    default:
      return "Wussup. I’m Lee-Wuh. Where we starting?";
  }
}

export default function LivingLeeWuhAgent({ compact = false }: { compact?: boolean }) {
  const [open, setOpen] = useState(false);
  const [mood, setMood] = useState<LeeWuhMood>("idle");
  const visibleActions = useMemo(() => actions, []);

  return (
    <div className={compact ? "fixed bottom-4 right-4 z-50" : "fixed bottom-6 right-6 z-50"}>
      {open ? (
        <div className="mb-4 w-[min(92vw,420px)] rounded-[28px] border border-[#C9A24A]/30 bg-[#08080A]/95 p-5 text-[#F5F1E8] shadow-[0_24px_90px_rgba(0,0,0,0.55)] backdrop-blur">
          <div className="flex items-start gap-4">
            <div className="relative h-16 w-16 shrink-0 overflow-hidden rounded-2xl border border-[#C9A24A]/30 bg-black">
              <img src="/brand/lee-wuh-hero-16x9.svg" alt="Lee-Wuh" className="h-full w-full object-cover" />
              <span className="absolute inset-0 animate-pulse bg-purple-500/10" />
            </div>
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#E9C77B]">Lee-Wuh // Living Agent</p>
              <p className="mt-2 text-sm leading-6 text-white/80">{moodLine(mood)}</p>
            </div>
          </div>

          <div className="mt-5 grid gap-2">
            {visibleActions.map((action) => (
              <Link
                key={action.href}
                href={action.href}
                onMouseEnter={() => setMood(action.mood)}
                className="group rounded-2xl border border-white/10 bg-white/[0.04] p-3 transition hover:border-[#C9A24A]/40 hover:bg-[#C9A24A]/10"
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm font-semibold text-white">{action.label}</span>
                  <span className="text-[#E9C77B] transition group-hover:translate-x-1">→</span>
                </div>
                <p className="mt-1 text-xs leading-5 text-white/50">{action.detail}</p>
              </Link>
            ))}
          </div>
        </div>
      ) : null}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        onMouseEnter={() => setMood("excited")}
        onMouseLeave={() => setMood("idle")}
        className="group relative flex h-24 w-24 items-center justify-center rounded-full border border-[#C9A24A]/40 bg-black shadow-[0_0_42px_rgba(126,58,242,0.5)] transition hover:scale-105"
        aria-label="Open Lee-Wuh living agent"
      >
        <span className="absolute inset-[-10px] animate-pulse rounded-full border border-purple-500/35" />
        <span className="absolute inset-[-22px] rounded-full bg-purple-600/20 blur-2xl" />
        <img src="/brand/lee-wuh-hero-16x9.svg" alt="" className="relative h-20 w-20 rounded-full object-cover" />
        <span className="absolute -top-2 right-0 rounded-full bg-[#C9A24A] px-2 py-1 text-[10px] font-black uppercase text-black">Ask</span>
      </button>
    </div>
  );
}
