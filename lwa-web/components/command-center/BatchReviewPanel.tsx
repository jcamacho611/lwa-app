"use client";

import { useState } from "react";

interface BatchItem {
  id: string;
  thumbnail: string;
  hook: string;
  caption: string;
  duration: number;
  ai_score: number;
  status: "pending" | "approved" | "rejected" | "edited";
  platform: string;
}

const mockBatch: BatchItem[] = [
  { id: "clip_001", thumbnail: "🎬", hook: "You won't believe what happens...", caption: "The moment that changed everything", duration: 15, ai_score: 0.94, status: "pending", platform: "tiktok" },
  { id: "clip_002", thumbnail: "✨", hook: "This trick saves hours...", caption: "Time-saving hack revealed", duration: 22, ai_score: 0.88, status: "approved", platform: "instagram" },
  { id: "clip_003", thumbnail: "🔥", hook: "The truth about...", caption: "Exposing the real story", duration: 18, ai_score: 0.91, status: "pending", platform: "youtube" },
  { id: "clip_004", thumbnail: "💡", hook: "Stop doing this wrong...", caption: "Common mistake fixed", duration: 25, ai_score: 0.85, status: "rejected", platform: "tiktok" },
  { id: "clip_005", thumbnail: "🎯", hook: "3 steps to...", caption: "Simple process breakdown", duration: 20, ai_score: 0.92, status: "pending", platform: "instagram" },
];

export function BatchReviewPanel() {
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [filter, setFilter] = useState<string>("all");

  const toggleSelection = (id: string) => {
    setSelectedItems((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const filteredBatch = filter === "all" ? mockBatch : mockBatch.filter((b) => b.status === filter);

  const stats = {
    pending: mockBatch.filter((b) => b.status === "pending").length,
    approved: mockBatch.filter((b) => b.status === "approved").length,
    rejected: mockBatch.filter((b) => b.status === "rejected").length,
    edited: mockBatch.filter((b) => b.status === "edited").length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#00D9FF]/20 text-3xl">
            📋
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white">Batch Review</h3>
            <p className="text-sm text-white/50">Review and approve generated clips in bulk</p>
          </div>
          <div className="flex gap-3 text-right">
            <div className="rounded-lg bg-yellow-400/20 px-3 py-2">
              <div className="text-lg font-bold text-yellow-400">{stats.pending}</div>
              <div className="text-xs text-white/50">Pending</div>
            </div>
            <div className="rounded-lg bg-green-400/20 px-3 py-2">
              <div className="text-lg font-bold text-green-400">{stats.approved}</div>
              <div className="text-xs text-white/50">Approved</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters & Actions */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex gap-2">
          {["all", "pending", "approved", "rejected"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-full px-3 py-1 text-sm capitalize transition ${
                filter === f
                  ? "bg-[#C9A24A] text-black"
                  : "border border-white/10 bg-white/[0.04] text-white/50 hover:bg-white/[0.08]"
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        {selectedItems.length > 0 && (
          <div className="flex gap-2">
            <button className="rounded-lg bg-green-400/20 px-3 py-2 text-sm text-green-400 transition hover:bg-green-400/30">
              Approve ({selectedItems.length})
            </button>
            <button className="rounded-lg bg-red-400/20 px-3 py-2 text-sm text-red-400 transition hover:bg-red-400/30">
              Reject ({selectedItems.length})
            </button>
            <button
              onClick={() => setSelectedItems([])}
              className="rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-white/50 transition hover:bg-white/[0.08]"
            >
              Clear
            </button>
          </div>
        )}
      </div>

      {/* Batch Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredBatch.map((item) => (
          <div
            key={item.id}
            onClick={() => toggleSelection(item.id)}
            className={`relative cursor-pointer rounded-2xl border p-4 transition ${
              selectedItems.includes(item.id)
                ? "border-[#C9A24A] bg-[#C9A24A]/10"
                : "border-white/10 bg-white/[0.04] hover:border-white/20"
            }`}
          >
            {/* Checkbox */}
            <div className="absolute left-4 top-4">
              <div
                className={`flex h-5 w-5 items-center justify-center rounded border transition ${
                  selectedItems.includes(item.id)
                    ? "border-[#C9A24A] bg-[#C9A24A]"
                    : "border-white/30 bg-transparent"
                }`}
              >
                {selectedItems.includes(item.id) && <span className="text-xs text-black">✓</span>}
              </div>
            </div>

            {/* Thumbnail */}
            <div className="mb-3 flex aspect-video items-center justify-center rounded-xl bg-black/40 text-4xl">
              {item.thumbnail}
            </div>

            {/* Status Badge */}
            <div className="mb-2">
              <span
                className={`rounded-full px-2 py-0.5 text-xs ${
                  item.status === "approved"
                    ? "bg-green-400/20 text-green-400"
                    : item.status === "rejected"
                    ? "bg-red-400/20 text-red-400"
                    : item.status === "edited"
                    ? "bg-blue-400/20 text-blue-400"
                    : "bg-yellow-400/20 text-yellow-400"
                }`}
              >
                {item.status}
              </span>
            </div>

            {/* Hook */}
            <h4 className="mb-1 text-sm font-medium text-white line-clamp-2">{item.hook}</h4>

            {/* Caption */}
            <p className="mb-3 text-xs text-white/50 line-clamp-1">{item.caption}</p>

            {/* Meta */}
            <div className="flex items-center justify-between text-xs text-white/30">
              <span>{item.duration}s</span>
              <span className="capitalize">{item.platform}</span>
              <span className="text-[#E9C77B]">{(item.ai_score * 100).toFixed(0)}%</span>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredBatch.length === 0 && (
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-12 text-center">
          <div className="mb-2 text-4xl">📭</div>
          <p className="text-white/50">No clips found with this filter</p>
          <button
            onClick={() => setFilter("all")}
            className="mt-4 rounded-lg bg-[#C9A24A] px-4 py-2 text-sm font-medium text-black transition hover:bg-[#E9C77B]"
          >
            Show All
          </button>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        <button className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
          Approve All Pending
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Export Approved
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Regenerate Rejected
        </button>
      </div>
    </div>
  );
}
