"use client";

import Link from "next/link";
import { useState } from "react";
import { LeeWuhCharacterStage } from "../components/lee-wuh";

export default function HomePage() {
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

      {/* LWA Core Loop Entry */}
      <div className="relative z-10 w-full max-w-lg">
        {/* Lee-Wuh Header */}
        <div className="mb-8">
          <LeeWuhCharacterStage
            mood={selectedMission ? "confident" : "idle"}
            variant="card"
            title="Lee-Wuh"
            message={
              selectedMission === "content"
                ? "I'm ready to turn your source into clips, hooks, captions, and a ranked posting package."
                : selectedMission === "money"
                  ? "I'm ready to route you into marketplace tasks, campaign briefs, and payout-readiness placeholders."
                  : "I'm your real-time character guide for clipping, campaigns, proof, style memory, and the money loop."
            }
            posterPath="/brand/lee-wuh/lee-wuh-hero-16x9.png"
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
              <span className="text-4xl">01</span>
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
              <span className="text-4xl">02</span>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-white">Marketplace Mission</h2>
                <p className="mt-1 text-sm text-white/60">
                  Review task lanes, campaign shells, and manual payout-readiness paths
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
          <div className="mt-8 animate-pulse">
            <Link
              href={selectedMission === "content" ? "/generate" : "/marketplace"}
              className="block w-full rounded-2xl bg-[#C9A24A] py-4 text-center text-lg font-bold text-black transition hover:bg-[#E9C77B]"
            >
              {selectedMission === "content"
                ? "Start Creating Clips"
                : "Open Marketplace"}
            </Link>
          </div>
        )}

        {/* Claim-safe product proof */}
        <div className="mt-12 grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-sm font-bold uppercase tracking-[0.18em] text-[#C9A24A]">Upload</div>
            <div className="mt-1 text-xs text-white/40">Public URL or source file path</div>
          </div>
          <div>
            <div className="text-sm font-bold uppercase tracking-[0.18em] text-[#C9A24A]">Rank</div>
            <div className="mt-1 text-xs text-white/40">Retention signals first</div>
          </div>
          <div>
            <div className="text-sm font-bold uppercase tracking-[0.18em] text-[#C9A24A]">Package</div>
            <div className="mt-1 text-xs text-white/40">Hooks, captions, timestamps</div>
          </div>
        </div>

        {/* Footer nav */}
        <div className="mt-8 flex justify-center gap-6 text-sm text-white/40">
          <Link href="/command-center" className="hover:text-white">
            Command Center
          </Link>
          <Link href="/company-os" className="hover:text-white">
            Company OS
          </Link>
          <Link href="/worlds" className="hover:text-white">
            Worlds
          </Link>
        </div>
      </div>
    </main>
  );
}
