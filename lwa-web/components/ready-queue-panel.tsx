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
    <section className="glass-panel rounded-[30px] p-5 sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="section-kicker">Ready queue</p>
          <h3 className="mt-3 text-2xl font-semibold text-ink">Next out</h3>
          <p className="mt-2 text-sm leading-7 text-ink/60">
            Reorder the stack, cut what misses, then export the run brief.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className={[
            "rounded-full border px-4 py-2 text-sm font-semibold",
            items.length > 0
              ? "border-accent/22 bg-accent/[0.08] text-accent"
              : "border-white/10 bg-white/[0.05] text-ink/72",
          ].join(" ")}>
            {items.length} {items.length === 1 ? "clip" : "clips"} ready
          </span>
          {items.length ? (
            <button
              type="button"
              onClick={onClear}
              className="secondary-button rounded-full px-4 py-2 text-sm font-medium"
            >
              Clear all
            </button>
          ) : null}
        </div>
      </div>

      {items.length ? (
        <>
          <div className="mt-6 space-y-3">
            {items.map((item, index) => (
              <div key={item.clipId} className="metric-tile rounded-[24px] p-4">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="status-chip status-approved">
                        Queue #{index + 1}
                      </span>
                      <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-ink/72">
                        {item.targetPlatform}
                      </span>
                      {item.packagingAngle ? (
                        <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-ink/72">
                          {item.packagingAngle}
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-3 text-base font-semibold text-ink">{item.hook}</p>
                    <p className="mt-2 text-sm leading-7 text-ink/62">{item.caption}</p>
                    <p className="mt-2 text-xs text-muted">
                      Score {item.viralityScore ?? "N/A"}
                      {item.bestPostOrder ? ` · Post ${item.bestPostOrder}` : ""}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2 lg:justify-end">
                    <button
                      type="button"
                      disabled={index === 0}
                      onClick={() => onMove(item.clipId, -1)}
                      className="secondary-button rounded-full px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Move up
                    </button>
                    <button
                      type="button"
                      disabled={index === items.length - 1}
                      onClick={() => onMove(item.clipId, 1)}
                      className="secondary-button rounded-full px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Move down
                    </button>
                    {item.assetUrl ? (
                      <a
                        href={item.assetUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="secondary-button rounded-full px-4 py-2 text-sm font-medium"
                      >
                        Open preview
                      </a>
                    ) : null}
                    <button
                      type="button"
                      onClick={() => onRemove(item.clipId)}
                      className="rounded-full border border-[var(--danger)] bg-[var(--surface-danger)] px-4 py-2 text-sm font-medium text-[var(--danger)] transition hover:bg-[var(--surface-danger-strong)] active:scale-95"
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
              className="primary-button rounded-full px-5 py-3 text-sm font-semibold"
            >
              Copy brief
            </button>
            <button
              type="button"
              onClick={exportQueueJson}
              className="secondary-button rounded-full px-5 py-3 text-sm font-medium"
            >
              Export queue JSON
            </button>
            {message ? <span className="text-sm text-accent">{message}</span> : null}
          </div>
        </>
      ) : (
        <div className="mt-6 rounded-[24px] border border-[var(--divider)] bg-[var(--surface-soft)] p-6">
          <p className="text-sm font-medium text-ink/72">Queue is empty</p>
          <p className="mt-2 text-sm leading-7 text-ink/46">
            Mark clips ready from Generate to build the next posting stack. The queue persists across sessions.
          </p>
        </div>
      )}
    </section>
  );
}
