"use client";

import type { LwaExperienceReward } from "../../lib/lwa-experience-state";

type LeeWuhRewardToastProps = {
  reward: LwaExperienceReward;
  onDismiss: () => void;
};

export default function LeeWuhRewardToast({
  reward,
  onDismiss,
}: LeeWuhRewardToastProps) {
  return (
    <div
      aria-live="polite"
      className="rounded-[24px] border border-[#C9A24A]/35 bg-[#120f08]/95 p-5 shadow-[0_24px_80px_-48px_rgba(201,162,74,0.9)]"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#E9C77B]">
            Reward unlocked
          </p>
          <h3 className="mt-2 text-2xl font-black text-white">
            {reward.xp} XP
          </h3>
          <p className="mt-2 text-sm leading-6 text-white/65">
            {reward.label}
          </p>
        </div>
        <button
          type="button"
          onClick={onDismiss}
          className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-semibold text-white/60 transition hover:border-[#C9A24A]/40 hover:text-white"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}

