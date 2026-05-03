"use client";

import Link from "next/link";
import { useState } from "react";
import { LeeWuhCharacter } from "../../components/lee-wuh";

export default function FirstMissionPage() {
  const [selectedMission, setSelectedMission] = useState<"content" | "money" | null>(null);

  return (
    <main className="relative flex min-h-screen items-center justify-center bg-[#0A0A0B] text-[#F5F1E8] overflow-hidden p-6">
      {/* Background aura effect */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background: `
            radial-gradient(circle at 70% 30%, rgba(201,162,74,0.15) 0%, transparent 50%),
            radial-gradient(circle at 30% 70%, rgba(109,59,255,0.1) 0%, transparent 50%)
          `
        }}
      />

      {/* LWA First Mission Entry */}
      <div className="relative z-10 w-full max-w-lg">
        {/* Lee-Wuh Header */}
        <div className="mb-8 text-center">
          <LeeWuhCharacter
            mood={selectedMission ? "victory" : "idle"}
            size="xl"
            showMessage={true}
            customMessage={
              selectedMission
                ? selectedMission === "content"
                  ? "Let's make some clips! Paste your source."
                  : "Let's find you some paid work."
                : "You got content or you tryna make money today?"
            }
          />
        </div>

        {/* Mission Selection */}
        <div className="space-y-4">
          {/* Content Mission */}
          <button
            onClick={() => setSelectedMission("content")}
            className={`group w-full rounded-2xl border p-6 text-left transition ${
              selectedMission === "content"
                ? "border-[#C9A24A] bg-[#C9A24A]/20"
                : "border-white/10 bg-white/[0.04] hover:border-[#C9A24A]/50"
            }`}
          >
            <div className="flex items-center gap-4">
              <span className="text-4xl">🎬</span>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-white">Content Mission</h2>
                <p className="mt-1 text-sm text-white/60">
                  Turn one video into a pack of short-form clips
                </p>
              </div>
              {selectedMission === "content" && (
                <span className="text-2xl text-[#C9A24A]">→</span>
              )}
            </div>
          </button>

          {/* Money Mission */}
          <button
            onClick={() => setSelectedMission("money")}
            className={`group w-full rounded-2xl border p-6 text-left transition ${
              selectedMission === "money"
                ? "border-green-400 bg-green-400/20"
                : "border-white/10 bg-white/[0.04] hover:border-green-400/50"
            }`}
          >
            <div className="flex items-center gap-4">
              <span className="text-4xl">💰</span>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-white">Money Mission</h2>
                <p className="mt-1 text-sm text-white/60">
                  Find paid clip jobs and campaign opportunities
                </p>
              </div>
              {selectedMission === "money" && (
                <span className="text-2xl text-green-400">→</span>
              )}
            </div>
          </button>
        </div>

        {/* Action Button */}
        {selectedMission && (
          <div className="mt-8">
            <Link
              href={selectedMission === "content" ? "/generate" : "/opportunities"}
              className="block w-full rounded-2xl bg-[#C9A24A] py-4 text-center text-lg font-bold text-black transition hover:bg-[#E9C77B]"
            >
              {selectedMission === "content"
                ? "🎬 Start Creating Clips →"
                : "💰 Find Paid Work →"}
            </Link>
          </div>
        )}

        {/* Stats / Trust */}
        <div className="mt-12 grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-[#C9A24A]">50K+</div>
            <div className="text-xs text-white/40">Clips Created</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-[#C9A24A]">$2M+</div>
            <div className="text-xs text-white/40">Creator Earnings</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-[#C9A24A]">4.9★</div>
            <div className="text-xs text-white/40">User Rating</div>
          </div>
        </div>

        {/* Footer nav */}
        <div className="mt-8 flex justify-center gap-6 text-sm text-white/40">
          <Link href="/command-center" className="hover:text-white">
            Command Center
          </Link>
          <Link href="/" className="hover:text-white">
            Home
          </Link>
        </div>
      </div>
    </main>
  );
}
