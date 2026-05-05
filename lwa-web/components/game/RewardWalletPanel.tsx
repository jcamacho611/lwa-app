"use client";

import type { SignalSprintPlayerProfile } from "../../lib/game/types";

interface RewardWalletPanelProps {
  profile: SignalSprintPlayerProfile;
}

export default function RewardWalletPanel({ profile }: RewardWalletPanelProps) {
  return (
    <div className="bg-[#0a0a0a] border border-[#1a1a1a] rounded-xl p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-white/70">Wallet</h3>
        <span className="px-2 py-1 bg-[#C9A24A]/20 border border-[#C9A24A]/40 rounded text-xs text-[#C9A24A]">
          DEMO MODE
        </span>
      </div>

      {/* Balances */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* Signal Fragments */}
        <div className="bg-[#1a1a1a] rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-6 h-6 rounded-full bg-[#C9A24A] flex items-center justify-center">
              <span className="text-black text-xs font-bold">S</span>
            </div>
            <span className="text-xs text-white/50">Signal Fragments</span>
          </div>
          <p className="text-xl font-bold text-white">{profile.signalFragments.toLocaleString()}</p>
        </div>

        {/* Compressed Signal */}
        <div className="bg-[#1a1a1a] rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center">
              <span className="text-black text-xs font-bold">CS</span>
            </div>
            <span className="text-xs text-white/50">Compressed Signal</span>
          </div>
          <p className="text-xl font-bold text-white">{profile.compressedSignal}</p>
        </div>
      </div>

      {/* Withdrawable Signal (always 0 in demo) */}
      <div className="bg-[#1a1a1a] rounded-lg p-3 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-[#C9A24A] flex items-center justify-center">
              <svg className="w-4 h-4 text-black" fill="currentColor" viewBox="0 0 20 20">
                <path d="M4 4a2 2 0 00-2 2v1h2V6h12v1h2V6a2 2 0 00-2-2H4zm12 6h-2v6h2v-6zm-4 0h-2v6h2v-6zm-4 0H4v6h2v-6zm-4 0v4a2 2 0 002 2h12a2 2 0 002-2v-4H2z" />
              </svg>
            </div>
            <span className="text-xs text-white/50">Withdrawable Signal</span>
          </div>
          <span className="text-lg font-bold text-white/40">{profile.withdrawableSignal}</span>
        </div>
        <p className="text-xs text-white/30 mt-1">
          Real payouts disabled in demo
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="bg-[#1a1a1a] rounded p-2">
          <p className="text-xs text-white/50">Realm</p>
          <p className="text-sm font-bold text-white">{profile.realm}</p>
        </div>
        <div className="bg-[#1a1a1a] rounded p-2">
          <p className="text-xs text-white/50">Ascension</p>
          <p className="text-lg font-bold text-white">{profile.ascension}</p>
        </div>
        <div className="bg-[#1a1a1a] rounded p-2">
          <p className="text-xs text-white/50">Flow</p>
          <p className="text-lg font-bold text-[#C9A24A]">{profile.flowStreak}d</p>
        </div>
      </div>

      {/* Daily Progress */}
      <div className="mt-4 pt-4 border-t border-[#1a1a1a]">
        <div className="flex justify-between text-xs text-white/50 mb-2">
          <span>Daily Progress</span>
          <span>{profile.dailyRuns} runs</span>
        </div>
        <div className="h-1 bg-[#1a1a1a] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#C9A24A]"
            style={{ width: `${Math.min((profile.dailyRuns / 10) * 100, 100)}%` }}
          />
        </div>
        <p className="text-xs text-white/30 mt-2">
          Max 10 sessions/day for demo rewards
        </p>
      </div>
    </div>
  );
}
