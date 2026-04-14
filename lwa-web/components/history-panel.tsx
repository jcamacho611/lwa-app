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
          <p className="text-xs uppercase tracking-[0.24em] text-muted">History</p>
          <h3 className="mt-2 text-3xl font-semibold text-ink">Saved clip packs</h3>
        </div>
        <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-ink/72">
          {clipPacks.length} stored runs
        </div>
      </div>

      <p className="mt-4 max-w-3xl text-sm leading-7 text-ink/64">
        Reopen past runs, inspect what won, and jump straight back into editing without regenerating from scratch.
      </p>

      {isLoading ? (
        <div className="mt-6 rounded-[24px] border border-white/10 bg-white/[0.03] px-5 py-6 text-sm text-ink/70">
          Loading clip pack detail...
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
                  "rounded-[24px] border p-5 transition",
                  selected ? "border-accent/30 bg-accent/10 shadow-glow" : "border-white/10 bg-white/[0.03]",
                ].join(" ")}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink/70">
                    {pack.target_platform || "Clip pack"}
                  </span>
                  {pack.top_score ? (
                    <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink/70">
                      Top score {pack.top_score}
                    </span>
                  ) : null}
                </div>
                <p className="mt-4 text-lg font-semibold text-ink">{pack.source_title || pack.video_url || pack.request_id}</p>
                <p className="mt-2 text-sm leading-7 text-ink/62">
                  {pack.clip_count || 0} clips · {pack.created_at || "recent"}
                </p>
                <button
                  type="button"
                  onClick={() => onOpenClipPack(pack.request_id)}
                  className="mt-4 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
                >
                  {selected ? "Open in editor" : "Review clip pack"}
                </button>
              </div>
            );
          })
        ) : (
          <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-5 text-sm text-ink/62">
            Sign in and generate a clip pack to start building your library.
          </div>
        )}
      </div>
    </section>
  );
}
