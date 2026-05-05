"use client";

import type { GameState } from "../../lib/game/types";

interface SignalSprintHudProps {
  score: number;
  streak: number;
  timeLeft: number;
  maxTime: number;
  gameState: GameState;
  onStart: () => void;
}

export default function SignalSprintHud({
  score,
  streak,
  timeLeft,
  maxTime,
  gameState,
  onStart,
}: SignalSprintHudProps) {
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (gameState === "idle") {
    return (
      <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#0a0a0a]">
        {/* Lee-Wuh Realm Aura */}
        <div className="absolute inset-0 bg-gradient-to-b from-purple-900/10 via-transparent to-[#0a0a0a] pointer-events-none" />

        <div className="text-center mb-8 relative z-10">
          <h2 className="text-3xl font-bold text-white mb-2">Signal Sprint</h2>
          <p className="text-white/60 text-sm max-w-xs">
            A ritual of proving you can control chaos.
          </p>
        </div>

        {/* Lee-Wuh Presents */}
        <div className="mb-6 px-4 py-2 bg-purple-500/10 border border-purple-500/30 rounded-lg">
          <p className="text-xs text-purple-400 text-center italic">
            Prove your signal.
          </p>
        </div>

        {/* Tutorial — Lee-Wuh System */}
        <div className="mb-8 space-y-2 text-sm relative z-10">
          <div className="flex items-center gap-2 text-white/70">
            <span className="w-6 h-6 rounded bg-[#C9A24A] flex items-center justify-center text-black text-xs">↑</span>
            <span>Collect Signal (gold)</span>
          </div>
          <div className="flex items-center gap-2 text-white/70">
            <span className="w-6 h-6 rounded bg-red-500 flex items-center justify-center text-white text-xs">×</span>
            <span>Avoid Noise (red)</span>
          </div>
          <div className="flex items-center gap-2 text-white/70">
            <span className="text-purple-400">⌨️ ← →</span>
            <span>or tap arrows to move</span>
          </div>
        </div>

        <button
          onClick={onStart}
          className="px-8 py-3 bg-[#C9A24A] hover:bg-[#D4AF37] text-black font-semibold rounded-lg transition-colors relative z-10"
        >
          Enter the Realm
        </button>

        <p className="mt-4 text-xs text-white/40">
          60-second runs • Demo mode
        </p>
      </div>
    );
  }

  const progressPercent = (timeLeft / maxTime) * 100;

  return (
    <div className="absolute top-0 left-0 right-0 p-4">
      {/* Top Bar */}
      <div className="flex justify-between items-start mb-2">
        {/* Score */}
        <div className="bg-[#1a1a1a] rounded-lg px-3 py-2">
          <p className="text-xs text-white/50">SCORE</p>
          <p className="text-xl font-bold text-white">{score.toLocaleString()}</p>
        </div>

        {/* Flow State (reframed from Streak) */}
        <div className="bg-[#1a1a1a] rounded-lg px-3 py-2">
          <p className="text-xs text-white/50">FLOW</p>
          <p className={`text-xl font-bold ${streak > 0 ? "text-purple-400" : "text-white/40"}`}>
            {streak}x
          </p>
        </div>

        {/* Time */}
        <div className="bg-[#1a1a1a] rounded-lg px-3 py-2">
          <p className="text-xs text-white/50">TIME</p>
          <p className={`text-xl font-bold ${timeLeft <= 10 ? "text-red-400" : "text-white"}`}>
            {formatTime(timeLeft)}
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-1 bg-[#1a1a1a] rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-1000 ${
            progressPercent < 20 ? "bg-red-500" : "bg-[#C9A24A]"
          }`}
          style={{ width: `${progressPercent}%` }}
        />
      </div>
    </div>
  );
}
