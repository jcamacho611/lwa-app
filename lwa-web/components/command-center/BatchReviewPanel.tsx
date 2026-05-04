"use client";

import { useEffect, useState } from "react";
import { bulkApproveClips, bulkRejectClips, bulkExportClips, listClips, ClipItem } from "../../lib/api";

interface DisplayBatchItem {
  id: string;
  thumbnail: string;
  hook: string;
  caption: string;
  duration: number;
  ai_score: number;
  status: "pending" | "approved" | "rejected" | "edited";
  platform: string;
}

function mapClipToDisplay(clip: ClipItem): DisplayBatchItem {
  return {
    id: clip.clip_id,
    thumbnail: clip.thumbnail_url ? "🎬" : "📄",
    hook: clip.hook,
    caption: clip.caption,
    duration: clip.duration,
    ai_score: clip.ai_score,
    status: clip.status,
    platform: clip.platform,
  };
}

export function BatchReviewPanel() {
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [batch, setBatch] = useState<DisplayBatchItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadClips() {
      try {
        const response = await listClips(filter !== "all" ? filter : null);
        if (response.success) {
          setBatch(response.clips.map(mapClipToDisplay));
        } else {
          setError("Failed to load clips");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load clips");
      } finally {
        setLoading(false);
      }
    }
    loadClips();
  }, [filter]);

  const toggleSelection = (id: string) => {
    setSelectedItems((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const filteredBatch = filter === "all" ? batch : batch.filter((b) => b.status === filter);

  const stats = {
    pending: batch.filter((b) => b.status === "pending").length,
    approved: batch.filter((b) => b.status === "approved").length,
    rejected: batch.filter((b) => b.status === "rejected").length,
    edited: batch.filter((b) => b.status === "edited").length,
  };

  const handleBulkApprove = async () => {
    if (selectedItems.length === 0) return;
    setLoading(true);
    setMessage(null);
    try {
      const response = await bulkApproveClips({ clip_ids: selectedItems });
      if (response.success) {
        setBatch((prev) =>
          prev.map((item) =>
            selectedItems.includes(item.id) ? { ...item, status: "approved" as const } : item
          )
        );
        setMessage(`Approved ${response.approved_count} clips`);
        setSelectedItems([]);
      } else {
        setMessage("Failed to approve clips");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to approve clips");
    } finally {
      setLoading(false);
    }
  };

  const handleBulkReject = async () => {
    if (selectedItems.length === 0) return;
    setLoading(true);
    setMessage(null);
    try {
      const response = await bulkRejectClips({ clip_ids: selectedItems });
      if (response.success) {
        setBatch((prev) =>
          prev.map((item) =>
            selectedItems.includes(item.id) ? { ...item, status: "rejected" as const } : item
          )
        );
        setMessage(`Rejected ${response.rejected_count} clips`);
        setSelectedItems([]);
      } else {
        setMessage("Failed to reject clips");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to reject clips");
    } finally {
      setLoading(false);
    }
  };

  const handleExportApproved = async () => {
    const approvedIds = batch.filter((b) => b.status === "approved").map((b) => b.id);
    if (approvedIds.length === 0) {
      setMessage("No approved clips to export");
      return;
    }
    setLoading(true);
    setMessage(null);
    try {
      const response = await bulkExportClips({ clip_ids: approvedIds, format: "json" });
      if (response.success) {
        setMessage(`Exported ${response.bundle?.clips?.length || 0} clips`);
      } else {
        setMessage("Failed to export clips");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to export clips");
    } finally {
      setLoading(false);
    }
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
            {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
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
            <button
              onClick={handleBulkApprove}
              disabled={loading}
              className="rounded-lg bg-green-400/20 px-3 py-2 text-sm text-green-400 transition hover:bg-green-400/30 disabled:opacity-50"
            >
              {loading ? "Working..." : `Approve (${selectedItems.length})`}
            </button>
            <button
              onClick={handleBulkReject}
              disabled={loading}
              className="rounded-lg bg-red-400/20 px-3 py-2 text-sm text-red-400 transition hover:bg-red-400/30 disabled:opacity-50"
            >
              {loading ? "Working..." : `Reject (${selectedItems.length})`}
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
      {loading ? (
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-12 text-center">
          <div className="mb-2 text-4xl">⏳</div>
          <p className="text-white/50">Loading clips...</p>
        </div>
      ) : filteredBatch.length === 0 ? (
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-12 text-center">
          <div className="mb-2 text-4xl">📭</div>
          <p className="text-white/50">No clips found</p>
          <button
            onClick={() => setFilter("all")}
            className="mt-4 rounded-lg bg-[#C9A24A] px-4 py-2 text-sm font-medium text-black transition hover:bg-[#E9C77B]"
          >
            Show All
          </button>
        </div>
      ) : (
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
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={handleBulkApprove}
          disabled={loading || stats.pending === 0}
          className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B] disabled:opacity-50"
        >
          {loading ? "Working..." : `Approve All Pending (${stats.pending})`}
        </button>
        <button
          onClick={handleExportApproved}
          disabled={loading || stats.approved === 0}
          className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08] disabled:opacity-50"
        >
          {loading ? "Working..." : `Export Approved (${stats.approved})`}
        </button>
        <button
          disabled={loading || stats.rejected === 0}
          className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08] disabled:opacity-50"
        >
          Regenerate Rejected ({stats.rejected})
        </button>
      </div>
    </div>
  );
}
