"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import SignalSprintGame from "../../components/game/SignalSprintGame";
import RewardWalletPanel from "../../components/game/RewardWalletPanel";
import { getSignalSprintProfile, resetMockProfile } from "../../lib/game/mockGameApi";
import type { SignalSprintPlayerProfile } from "../../lib/game/types";

export default function GamePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<SignalSprintPlayerProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const profileData = await getSignalSprintProfile();
      setProfile(profileData);
    } catch (error) {
      console.error("Failed to load profile:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    if (confirm("Reset your demo progress? This cannot be undone.")) {
      resetMockProfile();
      loadProfile();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-2 border-[#C9A24A] border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] py-8 px-4">
      {/* Header */}
      <div className="max-w-4xl mx-auto mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-white">Signal Sprint</h1>
            <p className="text-white/60 text-sm">LWA Bitcoin Reward Game • Demo Mode</p>
          </div>
          <button
            onClick={() => router.push("/")}
            className="px-4 py-2 bg-[#1a1a1a] hover:bg-[#2a2a2a] text-white rounded-lg text-sm transition-colors"
          >
            ← Back to Home
          </button>
        </div>

        {/* Demo Banner */}
        <div className="bg-[#C9A24A]/10 border border-[#C9A24A]/30 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-[#C9A24A]/20 flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-[#C9A24A]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-sm font-medium text-[#C9A24A] mb-1">Demo Mode Only</h3>
              <p className="text-xs text-white/60">
                This is a playable demo of Signal Sprint. Rewards shown are simulated and not withdrawable. 
                Real Bitcoin payouts will be enabled after compliance review and fraud controls are in place.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-6">
        {/* Game Area */}
        <div>
          <SignalSprintGame onComplete={loadProfile} />
        </div>

        {/* Wallet & Stats */}
        <div className="space-y-4">
          {profile && <RewardWalletPanel profile={profile} />}

          {/* Quick Actions */}
          <div className="bg-[#0a0a0a] border border-[#1a1a1a] rounded-xl p-4">
            <h3 className="text-sm font-medium text-white/70 mb-3">Actions</h3>
            <div className="space-y-2">
              <button
                onClick={loadProfile}
                className="w-full py-2 px-3 bg-[#1a1a1a] hover:bg-[#2a2a2a] text-white text-sm rounded-lg transition-colors"
              >
                Refresh Profile
              </button>
              <button
                onClick={handleReset}
                className="w-full py-2 px-3 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-sm rounded-lg transition-colors"
              >
                Reset Demo Progress
              </button>
            </div>
          </div>

          {/* Instructions */}
          <div className="bg-[#0a0a0a] border border-[#1a1a1a] rounded-xl p-4">
            <h3 className="text-sm font-medium text-white/70 mb-3">How to Play</h3>
            <ul className="space-y-2 text-sm text-white/60">
              <li className="flex items-start gap-2">
                <span className="text-[#C9A24A]">1.</span>
                <span>Use ← → arrow keys or tap buttons to move</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#C9A24A]">2.</span>
                <span>Collect gold Signal orbs (+100 pts, +streak)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#C9A24A]">3.</span>
                <span>Avoid red Noise blocks (-50 pts, breaks streak)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#C9A24A]">4.</span>
                <span>Build streaks for bonus multipliers</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#C9A24A]">5.</span>
                <span>Earn XP, coins, and demo sats!</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-4xl mx-auto mt-8 text-center">
        <p className="text-xs text-white/30">
          Signal Sprint is part of the LWA ecosystem • All rewards are currently simulated
        </p>
      </div>
    </div>
  );
}
