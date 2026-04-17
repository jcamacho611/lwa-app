"use client";

import { ClipPackSummary } from "../lib/types";

type HistoryPanelProps = {
  clipPacks: ClipPackSummary[];
  selectedClipPackId?: string | null;
  isLoading?: boolean;
  onOpenClipPack: (requestId: string) => void;
};

export function HistoryPanel({ clipPacks, selectedClipPackId, isLoading, onOpenClipPack }: HistoryPanelProps) {
  return (
    <section className="glass-panel rounded-[32px] p-6 sm:p-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="section-kicker">History</p>
          <h3 className="mt-2 text-3xl font-semibold text-ink">Saved clip packs</h3>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-ink/64">
            Reopen past runs, inspect what won, and jump straight back into editing without regenerating from scratch.
          </p>
        </div>
        <div className={[
          "rounded-full border px-4 py-2 text-sm font-semibold",
          clipPacks.length > 0
            ? "border-accent/22 bg-accent/[0.07] text-accent"
            : "border-white/10 bg-white/[0.05] text-ink/72",
        ].join(" ")}>
          {clipPacks.length} {clipPacks.length === 1 ? "run" : "runs"} stored
        </div>
      </div>

      {isLoading ? (
        <div className="mt-6 rounded-[24px] border border-white/10 bg-white/[0.03] px-5 py-6">
          <div className="flex items-center gap-3">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/10 border-t-accent" />
            <span className="text-sm text-ink/70">Loading clip pack detail...</span>
          </div>
        </div>
      ) : null}

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        {clipPacks.length ? (
          clipPacks.map((pack) => {
            const selected = pack.request_id === selectedClipPackId;
            return (
              <div
                key={pack.request_id}
                className={[
                  "rounded-[26px] border p-5 transition duration-200",
                  selected
                    ? "hero-card shadow-glow"
                    : "glass-panel hover:-translate-y-0.5 hover:border-white/16 hover:shadow-card",
                ].join(" ")}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-ink/70">
                    {pack.target_platform || "Clip pack"}
                  </span>
                  {pack.top_score ? (
                    <span className="status-chip status-approved">
                      🏆 Score {pack.top_score}
                    </span>
                  ) : null}
                  {selected ? (
                    <span className="status-chip status-ready">Open</span>
                  ) : null}
                </div>
                <p className="mt-4 text-lg font-semibold text-ink leading-snug">
                  {pack.source_title || pack.video_url || pack.request_id}
                </p>
                <p className="mt-2 text-sm text-ink/56">
                  {pack.clip_count || 0} clips
                  {pack.created_at ? ` · ${pack.created_at}` : ""}
                </p>
                <button
                  type="button"
                  onClick={() => onOpenClipPack(pack.request_id)}
                  className={[
                    "mt-4 rounded-full px-4 py-2 text-sm font-medium transition",
                    selected
                      ? "primary-button"
                      : "secondary-button",
                  ].join(" ")}
                >
                  {selected ? "Open in editor" : "Review clip pack"}
                </button>
              </div>
            );
          })
        ) : (
          <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-6">
            <p className="text-sm font-medium text-ink/72">No saved runs yet</p>
            <p className="mt-2 text-sm leading-7 text-ink/46">
              Generate while signed in to turn your archive into a reusable library of ranked assets.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
