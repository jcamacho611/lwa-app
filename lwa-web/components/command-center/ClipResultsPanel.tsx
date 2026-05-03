"use client";

import { useState } from "react";
import { LeeWuhCharacter, LeeWuhAvatar, LeeWuhLoading } from "../lee-wuh";

interface ClipResult {
  id: string;
  rank: number;
  hook: string;
  caption: string;
  thumbnailText: string;
  timestamp: string;
  duration: number;
  aiScore: number;
  status: "rendered" | "rendering" | "strategy_only" | "failed";
  previewUrl?: string;
  platform: string;
}

const mockClipResults: ClipResult[] = [
  {
    id: "clip_001",
    rank: 1,
    hook: "You won't believe what happens at 3:42...",
    caption: "The moment that changed everything",
    thumbnailText: "WAIT FOR IT",
    timestamp: "3:42",
    duration: 15,
    aiScore: 0.94,
    status: "rendered",
    previewUrl: "/generated/clip_001.mp4",
    platform: "tiktok",
  },
  {
    id: "clip_002",
    rank: 2,
    hook: "Stop making this mistake...",
    caption: "Common error most people miss",
    thumbnailText: "DON'T DO THIS",
    timestamp: "5:18",
    duration: 22,
    aiScore: 0.88,
    status: "rendered",
    previewUrl: "/generated/clip_002.mp4",
    platform: "youtube_shorts",
  },
  {
    id: "clip_003",
    rank: 3,
    hook: "The truth about productivity...",
    caption: "What experts won't tell you",
    thumbnailText: "EXPOSED",
    timestamp: "8:24",
    duration: 18,
    aiScore: 0.82,
    status: "strategy_only",
    platform: "instagram_reels",
  },
];

export function ClipResultsPanel() {
  const [selectedClip, setSelectedClip] = useState<string | null>("clip_001");
  const [generationPhase, setGenerationPhase] = useState<"idle" | "scanning" | "ranking" | "rendering" | "complete">("complete");
  const [savedToVault, setSavedToVault] = useState<string[]>([]);

  const selectedClipData = mockClipResults.find((c) => c.id === selectedClip);

  const getLeeWuhMood = () => {
    switch (generationPhase) {
      case "scanning":
        return "analyzing";
      case "rendering":
        return "rendering";
      case "complete":
        return "victory";
      default:
        return "idle";
    }
  };

  const handleSaveToVault = (clipId: string) => {
    setSavedToVault((prev) => [...prev, clipId]);
  };

  return (
    <div className="space-y-6">
      {/* Lee-Wuh Status Header */}
      <div className="rounded-[28px] border border-[#C9A24A]/30 bg-[#C9A24A]/10 p-6">
        <div className="flex items-center gap-4">
          <LeeWuhCharacter
            mood={getLeeWuhMood()}
            size="lg"
            showMessage={true}
            customMessage={
              generationPhase === "complete"
                ? `Found ${mockClipResults.length} clips. Best one first!`
                : undefined
            }
          />
        </div>
      </div>

      {/* Best Clip First - Hero Section */}
      {selectedClipData && selectedClipData.status === "rendered" && (
        <div className="rounded-[28px] border-2 border-green-400/50 bg-green-400/10 p-6">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-green-400 text-xl font-bold text-black">
                1
              </span>
              <div>
                <h3 className="text-lg font-bold text-white">BEST CLIP — POST THIS FIRST</h3>
                <span className="inline-flex items-center gap-1 rounded-full bg-green-400/20 px-2 py-0.5 text-xs text-green-400">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse" />
                  READY NOW
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-[#E9C77B]">
                {(selectedClipData.aiScore * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-white/50">AI Score</div>
            </div>
          </div>

          {/* Video Preview Placeholder */}
          <div className="relative mb-4 aspect-video rounded-2xl bg-black/60">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="mb-2 text-5xl">▶️</div>
                <p className="text-white/70">Rendered Clip Preview</p>
                <p className="text-sm text-white/50">{selectedClipData.duration}s • {selectedClipData.platform}</p>
              </div>
            </div>
            {/* Playable Badge */}
            <div className="absolute bottom-4 left-4">
              <span className="rounded-full bg-green-400/20 px-3 py-1 text-sm text-green-400">
                ▶ Playable
              </span>
            </div>
            {/* Export Ready Badge */}
            <div className="absolute bottom-4 right-4">
              <span className="rounded-full bg-[#C9A24A]/20 px-3 py-1 text-sm text-[#E9C77B]">
                📤 Export-Ready
              </span>
            </div>
          </div>

          {/* Hook & Caption */}
          <div className="mb-4 space-y-3">
            <div className="rounded-xl bg-black/40 p-4">
              <label className="mb-1 block text-xs text-white/50">HOOK</label>
              <p className="text-lg font-medium text-white">&ldquo;{selectedClipData.hook}&rdquo;</p>
            </div>
            <div className="rounded-xl bg-black/40 p-4">
              <label className="mb-1 block text-xs text-white/50">CAPTION</label>
              <p className="text-white/80">{selectedClipData.caption}</p>
            </div>
            <div className="rounded-xl bg-black/40 p-4">
              <label className="mb-1 block text-xs text-white/50">THUMBNAIL TEXT</label>
              <p className="text-xl font-bold text-[#E9C77B]">{selectedClipData.thumbnailText}</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            <button className="flex-1 rounded-xl bg-green-400 px-4 py-3 text-sm font-bold text-black transition hover:bg-green-500">
              ▶ Play Best Clip
            </button>
            <button className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-bold text-black transition hover:bg-[#E9C77B]">
              📤 Export This
            </button>
            <button
              onClick={() => handleSaveToVault(selectedClipData.id)}
              disabled={savedToVault.includes(selectedClipData.id)}
              className="rounded-xl border border-[#C9A24A]/50 bg-[#C9A24A]/10 px-4 py-3 text-sm font-medium text-[#E9C77B] transition hover:bg-[#C9A24A]/20 disabled:opacity-50"
            >
              {savedToVault.includes(selectedClipData.id) ? "✓ Saved to Vault" : "🏆 Save to Proof Vault"}
            </button>
          </div>
        </div>
      )}

      {/* All Clips - Ranked List */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-white">All Clips (Ranked by AI)</h3>

        {mockClipResults.map((clip) => (
          <div
            key={clip.id}
            onClick={() => setSelectedClip(clip.id)}
            className={`cursor-pointer rounded-2xl border p-4 transition ${
              selectedClip === clip.id
                ? "border-[#C9A24A] bg-[#C9A24A]/10"
                : "border-white/10 bg-white/[0.04] hover:border-white/20"
            }`}
          >
            <div className="flex items-start gap-4">
              {/* Rank */}
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-lg font-bold ${
                  clip.rank === 1
                    ? "bg-green-400 text-black"
                    : clip.rank === 2
                    ? "bg-[#C9A24A] text-black"
                    : "bg-white/10 text-white"
                }`}
              >
                {clip.rank}
              </div>

              {/* Content */}
              <div className="min-w-0 flex-1">
                <div className="mb-2 flex items-center gap-2">
                  {/* Status Badge - CRITICAL DISTINCTION */}
                  {clip.status === "rendered" ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-green-400/20 px-2 py-0.5 text-xs text-green-400">
                      <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                      RENDERED — Ready
                    </span>
                  ) : clip.status === "rendering" ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-yellow-400/20 px-2 py-0.5 text-xs text-yellow-400">
                      <span className="h-1.5 w-1.5 rounded-full bg-yellow-400 animate-pulse" />
                      RENDERING...
                    </span>
                  ) : clip.status === "strategy_only" ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-blue-400/20 px-2 py-0.5 text-xs text-blue-400">
                      <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
                      STRATEGY ONLY — Not Rendered
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 rounded-full bg-red-400/20 px-2 py-0.5 text-xs text-red-400">
                      <span className="h-1.5 w-1.5 rounded-full bg-red-400" />
                      FAILED — Recovery Available
                    </span>
                  )}

                  <span className="text-xs text-white/30">{clip.platform}</span>
                </div>

                <p className="truncate text-sm font-medium text-white">{clip.hook}</p>
                <p className="truncate text-xs text-white/50">{clip.caption}</p>

                <div className="mt-2 flex items-center gap-4 text-xs text-white/30">
                  <span>{clip.duration}s</span>
                  <span>@ {clip.timestamp}</span>
                  <span className="text-[#E9C77B]">{(clip.aiScore * 100).toFixed(0)}% AI</span>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex shrink-0 flex-col gap-2">
                {clip.status === "rendered" && (
                  <button className="rounded-lg bg-green-400/20 p-2 text-green-400 transition hover:bg-green-400/30">
                    ▶
                  </button>
                )}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSaveToVault(clip.id);
                  }}
                  disabled={savedToVault.includes(clip.id)}
                  className="rounded-lg border border-white/10 p-2 text-white/50 transition hover:bg-white/[0.08] disabled:text-green-400"
                >
                  {savedToVault.includes(clip.id) ? "✓" : "🏆"}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Batch Actions */}
      <div className="flex flex-wrap gap-3">
        <button className="flex-1 rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-bold text-black transition hover:bg-[#E9C77B]">
          📦 Package All Rendered ({mockClipResults.filter(c => c.status === "rendered").length})
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          🔁 Re-Render Strategy Clips
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          📤 Export Hooks & Captions Only
        </button>
      </div>

      {/* Saved to Vault Feedback */}
      {savedToVault.length > 0 && (
        <div className="flex items-center gap-3 rounded-2xl border border-[#C9A24A]/30 bg-[#C9A24A]/10 p-4">
          <LeeWuhAvatar mood="victory" size="md" />
          <div>
            <p className="text-sm font-medium text-white">
              {savedToVault.length} clip{savedToVault.length > 1 ? "s" : ""} saved to Proof Vault!
            </p>
            <p className="text-xs text-white/50">
              Lee-Wuh will use this to improve future recommendations. Style Memory updated.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
