"use client";

import { useEffect, useState } from "react";
import { BatchSourceRef, BatchSummary, PlatformOption, UploadAsset } from "../lib/types";

type BatchPanelProps = {
  batches: BatchSummary[];
  uploads: UploadAsset[];
  currentVideoUrl: string;
  selectedUpload: UploadAsset | null;
  platform: PlatformOption;
  onCreate: (payload: { title: string; target_platform: string; selected_trend?: string; sources: BatchSourceRef[] }) => Promise<void>;
};

export function BatchPanel({ batches, uploads, currentVideoUrl, selectedUpload, platform, onCreate }: BatchPanelProps) {
  const [title, setTitle] = useState("");
  const [selectedTrend, setSelectedTrend] = useState("");
  const [selectedUploadIds, setSelectedUploadIds] = useState<string[]>([]);
  const [includeCurrentUrl, setIncludeCurrentUrl] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const uploadId = selectedUpload?.file_id || selectedUpload?.source_ref?.upload_id || selectedUpload?.id;
    if (uploadId) {
      setSelectedUploadIds((current) => (current.includes(uploadId) ? current : [uploadId, ...current]));
    }
  }, [selectedUpload]);

  function toggleUpload(uploadId: string) {
    setSelectedUploadIds((current) =>
      current.includes(uploadId) ? current.filter((item) => item !== uploadId) : [...current, uploadId],
    );
  }

  async function handleCreate() {
    const sources: BatchSourceRef[] = [];

    if (includeCurrentUrl && currentVideoUrl.trim()) {
      sources.push({ source_kind: "url", video_url: currentVideoUrl.trim() });
    }

    for (const uploadId of selectedUploadIds) {
      sources.push({ source_kind: "upload", upload_id: uploadId });
    }

    if (!sources.length) {
      setMessage("Select at least one upload or include the current pasted URL.");
      return;
    }

    setIsSaving(true);
    setMessage(null);
    try {
      await onCreate({
        title: title.trim() || `Batch ${new Date().toLocaleDateString()}`,
        target_platform: platform,
        selected_trend: selectedTrend.trim() || undefined,
        sources,
      });
      setTitle("");
      setSelectedTrend("");
      setIncludeCurrentUrl(false);
      setSelectedUploadIds([]);
      setMessage("Batch created.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to create batch.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="grid gap-6 xl:grid-cols-[0.96fr,1.04fr]">
      <div className="glass-panel rounded-[32px] p-6 sm:p-8">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Batch Mode</p>
        <h3 className="mt-2 text-3xl font-semibold text-ink">Queue multi-source runs</h3>
        <p className="mt-4 text-sm leading-7 text-ink/64">
          Stack multiple sources into one repeatable workflow when a single run is not enough.
        </p>

        <div className="mt-6 space-y-5">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-ink/80">Batch title</span>
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Weekly Creator Pipeline"
              className="w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition placeholder:text-muted focus:border-accent/40"
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-ink/80">Optional trend tag</span>
            <input
              value={selectedTrend}
              onChange={(event) => setSelectedTrend(event.target.value)}
              placeholder="Founder clips, product launch, educational"
              className="w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition placeholder:text-muted focus:border-accent/40"
            />
          </label>

          <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
            <div className="flex items-start gap-3">
              <input
                id="batch-current-url"
                type="checkbox"
                checked={includeCurrentUrl}
                disabled={!currentVideoUrl.trim()}
                onChange={(event) => setIncludeCurrentUrl(event.target.checked)}
                className="mt-1 h-4 w-4 accent-cyan-400"
              />
              <label htmlFor="batch-current-url" className="text-sm leading-7 text-ink/72">
                Include current pasted URL
                <span className="block text-xs text-muted">{currentVideoUrl.trim() || "Paste a URL on Generate to use this source."}</span>
              </label>
            </div>
          </div>

          <div>
            <p className="mb-3 text-sm font-medium text-ink/80">Choose uploads</p>
            <div className="space-y-3">
              {uploads.length ? (
                uploads.map((upload) => {
                  const uploadId = upload.file_id || upload.source_ref?.upload_id || upload.id;
                  if (!uploadId) {
                    return null;
                  }
                  const checked = selectedUploadIds.includes(uploadId);
                  return (
                    <label
                      key={uploadId}
                      className={[
                        "flex cursor-pointer items-start gap-3 rounded-[24px] border p-4 transition",
                        checked ? "border-accent/30 bg-accent/10" : "border-white/10 bg-white/[0.03]",
                      ].join(" ")}
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleUpload(uploadId)}
                        className="mt-1 h-4 w-4 accent-cyan-400"
                      />
                      <span className="text-sm leading-7 text-ink/72">
                        <span className="block font-medium text-ink">{upload.file_name || upload.filename || uploadId}</span>
                        <span className="block text-xs text-muted">{upload.content_type || "video"} · {upload.created_at || "recent"}</span>
                      </span>
                    </label>
                  );
                })
              ) : (
              <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4 text-sm text-ink/62">
                  Upload a file from Generate or Upload to start building a batch queue.
              </div>
              )}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              disabled={isSaving}
              onClick={handleCreate}
              className="rounded-full bg-gradient-to-r from-accent to-accentSoft px-5 py-3 text-sm font-semibold text-white shadow-glow disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSaving ? "Creating batch..." : "Create Batch"}
            </button>
            {message ? <span className="text-sm text-accent">{message}</span> : null}
          </div>
        </div>
      </div>

      <div className="glass-panel rounded-[32px] p-6 sm:p-8">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Runs</p>
            <h3 className="mt-2 text-2xl font-semibold text-ink">Recent batches</h3>
          </div>
          <span className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-ink/72">{batches.length} total</span>
        </div>

        <div className="mt-6 space-y-3">
          {batches.length ? (
            batches.map((batch) => (
              <div key={batch.id} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink/72">{batch.status}</span>
                  <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink/72">
                    {batch.target_platform || platform}
                  </span>
                </div>
                <p className="mt-3 text-base font-semibold text-ink">{batch.title}</p>
                <p className="mt-2 text-sm text-ink/62">
                  {batch.completed_sources}/{batch.total_sources} completed · {batch.failed_sources || 0} failed
                </p>
              </div>
            ))
          ) : (
            <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4 text-sm text-ink/62">
              No batches yet. Combine a few links or uploads to create the first one.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
