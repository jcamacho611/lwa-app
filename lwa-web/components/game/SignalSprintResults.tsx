"use client";

import type { SignalSprintReward, SignalSprintPlayerProfile, GameStats } from "../../lib/game/types";
import RewardWalletPanel from "./RewardWalletPanel";

interface SignalSprintResultsProps {
  result: {
    reward: SignalSprintReward;
    profile: SignalSprintPlayerProfile;
  };
  stats: GameStats;
  onPlayAgain: () => void;
  onBack?: () => void;
}

export default function SignalSprintResults({
  result,
  stats,
  onPlayAgain,
  onBack,
}: SignalSprintResultsProps) {
  const { reward, profile } = result;

  return (
    <div className="w-full max-w-md mx-auto p-4">
      {/* Header */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-white mb-1">Run Complete!</h2>
        <p className="text-white/60 text-sm">
          {reward.rewardEligible
            ? "Great run! Rewards added to your wallet."
            : reward.reason || "Session not eligible for rewards."}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-[#1a1a1a] rounded-lg p-3 text-center">
          <p className="text-xs text-white/50 mb-1">SCORE</p>
          <p className="text-xl font-bold text-white">{stats.score.toLocaleString()}</p>
        </div>
        <div className="bg-[#1a1a1a] rounded-lg p-3 text-center">
          <p className="text-xs text-white/50 mb-1">MAX STREAK</p>
          <p className="text-xl font-bold text-[#C9A24A]">{stats.maxStreak}x</p>
        </div>
        <div className="bg-[#1a1a1a] rounded-lg p-3 text-center">
          <p className="text-xs text-white/50 mb-1">TIME</p>
          <p className="text-xl font-bold text-white">
            {Math.floor(stats.durationMs / 1000)}s
          </p>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="bg-[#1a1a1a] rounded-lg p-4 mb-6">
        <h3 className="text-sm font-medium text-white/70 mb-3">Performance</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-white/60">Signal Collected</span>
            <span className="text-[#C9A24A]">{stats.signalCollected}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-white/60">Noise Hits</span>
            <span className="text-red-400">{stats.noiseHits}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-white/60">Ascension</span>
            <span className="text-white">{profile.ascension}</span>
          </div>
        </div>
      </div>

      {/* Rewards */}
      {reward.rewardEligible && (
        <div className="bg-[#C9A24A]/10 border border-[#C9A24A]/30 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-medium text-[#C9A24A] mb-3">Rewards Earned</h3>
          <div className="grid grid-cols-3 gap-3">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">+{reward.ascensionEarned}</p>
              <p className="text-xs text-white/50">Ascension</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-[#C9A24A]">+{reward.fragmentsEarned}</p>
              <p className="text-xs text-white/50">Fragments</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">+{reward.compressedEarned}</p>
              <p className="text-xs text-white/50">Compressed</p>
            </div>
          </div>
          <p className="text-xs text-center text-white/40 mt-3">
            Demo rewards are not withdrawable
          </p>
        </div>
      )}

      {/* Wallet Panel */}
      <div className="mb-6">
        <RewardWalletPanel profile={profile} />
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={onPlayAgain}
          className="flex-1 py-3 bg-[#C9A24A] hover:bg-[#D4AF37] text-black font-semibold rounded-lg transition-colors"
        >
          Play Again
        </button>
        {onBack && (
          <button
            onClick={onBack}
            className="flex-1 py-3 bg-[#1a1a1a] hover:bg-[#2a2a2a] text-white font-semibold rounded-lg transition-colors"
          >
            Back
          </button>
        )}
      </div>
    </div>
  );
}
