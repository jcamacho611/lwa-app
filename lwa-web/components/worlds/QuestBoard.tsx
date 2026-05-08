"use client";

import { useState } from "react";
import type { Quest } from "../../lib/worlds/types";
import { claimQuest } from "../../lib/worlds/api";
import { readStoredToken } from "../../lib/auth";
import { StatPill } from "./StatPill";
import { StatusBadge } from "./StatusBadge";

function ClaimButton({ quest, onClaimed }: { quest: Quest; onClaimed: (id: string) => void }) {
  const [claiming, setClaiming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [xpAwarded, setXpAwarded] = useState<number | null>(null);

  if (quest.status === "claimed" || xpAwarded !== null) {
    return (
      <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-400">
        {xpAwarded !== null ? `+${xpAwarded} XP claimed` : "Claimed"}
      </span>
    );
  }

  if (quest.status !== "completed") return null;

  async function handleClaim() {
    const token = readStoredToken();
    if (!token) {
      setError("Sign in to claim rewards.");
      return;
    }
    setClaiming(true);
    setError(null);
    try {
      const result = await claimQuest(quest.id, token);
      setXpAwarded(result.xp_awarded ?? quest.rewardXp);
      onClaimed(quest.id);
    } catch {
      setError("Claim failed. Try again.");
    } finally {
      setClaiming(false);
    }
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <button
        type="button"
        onClick={handleClaim}
        disabled={claiming}
        className="rounded-full bg-[var(--gold)] px-4 py-1.5 text-xs font-semibold text-black transition hover:opacity-90 disabled:opacity-50"
      >
        {claiming ? "Claiming…" : "Claim reward"}
      </button>
      {error ? <p className="text-[10px] text-red-400">{error}</p> : null}
    </div>
  );
}

export function QuestBoard({ quests: initial }: { quests: Quest[] }) {
  const [quests, setQuests] = useState(initial);

  function handleClaimed(id: string) {
    setQuests((prev) => prev.map((q) => (q.id === id ? { ...q, status: "claimed" as const } : q)));
  }

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      {quests.map((quest) => {
        const progress = Math.min(Math.round((quest.progress / quest.goal) * 100), 100);
        return (
          <article key={quest.id} className="glass-panel rounded-[24px] p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <StatusBadge status={quest.status} />
              <StatPill label="Reward" value={`+${quest.rewardXp} XP`} accent />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-ink">{quest.title}</h3>
            <p className="mt-2 text-sm leading-7 text-ink/62">{quest.description}</p>
            <div className="mt-5">
              <div className="mb-2 flex justify-between text-xs text-ink/46">
                <span>Progress</span>
                <span>
                  {quest.progress}/{quest.goal}
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-[var(--surface-inset-strong)]">
                <div className="h-full rounded-full bg-[var(--gold)]" style={{ width: `${progress}%` }} />
              </div>
            </div>
            {quest.status === "completed" || quest.status === "claimed" ? (
              <div className="mt-4 flex justify-end">
                <ClaimButton quest={quest} onClaimed={handleClaimed} />
              </div>
            ) : null}
          </article>
        );
      })}
    </div>
  );
}
