"use client";

import { useState } from "react";
import type { ReadyQueueItem } from "../lib/queue";
import { buildReadyQueueExport } from "../lib/queue";

type ReadyQueuePanelProps = {
  items: ReadyQueueItem[];
  onMove: (clipId: string, direction: -1 | 1) => void;
  onRemove: (clipId: string) => void;
  onClear: () => void;
};

export function ReadyQueuePanel({ items, onMove, onRemove, onClear }: ReadyQueuePanelProps) {
  const [message, setMessage] = useState<string | null>(null);

  async function copyQueue() {
    try {
      await navigator.clipboard.writeText(buildReadyQueueExport(items));
      setMessage("Ready queue copied.");
      window.setTimeout(() => setMessage(null), 1600);
    } catch {
      setMessage("Copy failed.");
      window.setTimeout(() => setMessage(null), 1600);
    }
  }

  function exportQueueJson() {
    const payload = JSON.stringify(items, null, 2);
    const blob = new Blob([payload], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "lwa-ready-queue.json";
    link.click();
    URL.revokeObjectURL(url);
    setMessage("Queue exported.");
    window.setTimeout(() => setMessage(null), 1600);
  }

  return (
    <section className="glass-panel rounded-[28px] p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-muted">Ready Queue</p>
          <h3 className="mt-2 text-xl font-semibold text-ink">Clips lined up to post</h3>
          <p className="mt-2 text-sm leading-7 text-ink/60">
            Reorder the next few assets, remove weak candidates, then export the queue as one clean package.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-ink/72">
            {items.length} ready
          </span>
          {items.length ? (
            <button
              type="button"
              onClick={onClear}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
            >
              Clear
            </button>
          ) : null}
        </div>
      </div>

      {items.length ? (
        <>
          <div className="mt-6 space-y-3">
            {items.map((item, index) => (
              <div key={item.clipId} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full border border-neonPurple/30 bg-neonPurple/12 px-3 py-1 text-xs font-medium text-white">
                        Queue #{index + 1}
                      </span>
                      <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink/72">
                        {item.targetPlatform}
                      </span>
                      {item.packagingAngle ? (
                        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink/72">
                          {item.packagingAngle}
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-3 text-base font-semibold text-ink">{item.hook}</p>
                    <p className="mt-2 text-sm leading-7 text-ink/62">{item.caption}</p>
                    <p className="mt-2 text-xs text-muted">
                      Virality {item.viralityScore ?? "N/A"}
                      {item.bestPostOrder ? ` · Suggested post order ${item.bestPostOrder}` : ""}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2 lg:justify-end">
                    <button
                      type="button"
                      disabled={index === 0}
                      onClick={() => onMove(item.clipId, -1)}
                      className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Move up
                    </button>
                    <button
                      type="button"
                      disabled={index === items.length - 1}
                      onClick={() => onMove(item.clipId, 1)}
                      className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Move down
                    </button>
                    {item.assetUrl ? (
                      <a
                        href={item.assetUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
                      >
                        Open asset
                      </a>
                    ) : null}
                    <button
                      type="button"
                      onClick={() => onRemove(item.clipId)}
                      className="rounded-full border border-red-400/20 bg-red-400/8 px-4 py-2 text-sm font-medium text-red-100 transition hover:bg-red-400/14"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={copyQueue}
              className="rounded-full bg-gradient-to-r from-accent to-accentSoft px-5 py-3 text-sm font-semibold text-white shadow-glow"
            >
              Copy queue brief
            </button>
            <button
              type="button"
              onClick={exportQueueJson}
              className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
            >
              Export queue JSON
            </button>
            {message ? <span className="text-sm text-accent">{message}</span> : null}
          </div>
        </>
      ) : (
        <div className="mt-6 rounded-[24px] border border-white/10 bg-white/[0.03] p-5 text-sm text-ink/62">
          Mark clips ready from Generate to build the queue. The strongest item should sit at the top before you export.
        </div>
      )}
    </section>
  );
}
