"use client";

import { useEffect, useRef, useState } from "react";
import type { ClipResult } from "../lib/types";
import { editClip } from "../lib/api";

type Props = {
  clip: ClipResult;
  token: string;
  onSaved: (updated: ClipResult) => void;
  onClose: () => void;
};

function formatTime(sec: number): string {
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = Math.floor(sec % 60);
  const ms = Math.round((sec % 1) * 10);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}.${ms}`;
}

function toTimecode(sec: number): string {
  // Work in integer milliseconds to prevent Math.round producing ms=1000
  const totalMs = Math.round(sec * 1000);
  const ms = totalMs % 1000;
  const totalSec = Math.floor(totalMs / 1000);
  const h = Math.floor(totalSec / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const s = totalSec % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
}

// The backend applies -ss/-to against the rendered clip asset, not the original
// source, so trim bounds must be clip-relative (0 … clip.duration).
function clipDuration(clip: ClipResult): number {
  if (clip.duration && clip.duration > 0) return clip.duration;
  return 60; // conservative fallback when duration is unknown
}

export function TimelineEditorPanel({ clip, token, onSaved, onClose }: Props) {
  const clipId = clip.record_id || clip.clip_id || clip.id;
  const duration = clipDuration(clip);

  const [trimStart, setTrimStart] = useState(0);
  const [trimEnd, setTrimEnd] = useState(duration);
  const [captionText, setCaptionText] = useState(clip.caption || "");
  const [burnCaptions, setBurnCaptions] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  // Reset all state when the selected clip changes (P2 fix)
  useEffect(() => {
    const d = clipDuration(clip);
    setTrimStart(0);
    setTrimEnd(d);
    setCaptionText(clip.caption || "");
    setBurnCaptions(false);
    setSaving(false);
    setError(null);
    setSaved(false);
  }, [clip.id]);

  const trackRef = useRef<HTMLDivElement>(null);
  const dragging = useRef<"start" | "end" | null>(null);

  const startPct = duration > 0 ? (trimStart / duration) * 100 : 0;
  const endPct = duration > 0 ? (trimEnd / duration) * 100 : 100;

  function clampedInput(val: string, min: number, max: number): number {
    const n = parseFloat(val);
    if (isNaN(n)) return min;
    return Math.max(min, Math.min(max, n));
  }

  async function handleSave() {
    if (trimStart >= trimEnd) {
      setError("Start must be before end.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const updated = await editClip(
        clipId,
        {
          start_time: toTimecode(trimStart),
          end_time: toTimecode(trimEnd),
          caption_text: burnCaptions ? captionText : undefined,
        },
        token,
      );
      setSaved(true);
      onSaved(updated);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Edit failed. Try again.");
    } finally {
      setSaving(false);
    }
  }

  function onTrackMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    if (!dragging.current || !trackRef.current) return;
    const rect = trackRef.current.getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const t = pct * duration;
    if (dragging.current === "start") {
      setTrimStart(Math.min(t, trimEnd - 0.5));
    } else {
      setTrimEnd(Math.max(t, trimStart + 0.5));
    }
  }

  return (
    <div className="glass-panel rounded-[24px] p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.15em] text-ink/46">Timeline editor</p>
          <p className="mt-0.5 text-sm font-medium text-ink truncate max-w-xs">{clip.title}</p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-full px-3 py-1 text-xs text-ink/50 hover:text-ink border border-white/10 hover:border-white/20 transition"
        >
          Close
        </button>
      </div>

      {/* Scrub bar — positions are clip-relative (0 … duration) */}
      <div className="space-y-2">
        <div className="flex justify-between text-[10px] text-ink/46">
          <span>0:00</span>
          <span>{formatTime(duration)}</span>
        </div>
        <div
          ref={trackRef}
          className="relative h-10 rounded-full bg-white/[0.06] border border-white/10 cursor-pointer select-none overflow-hidden"
          onMouseMove={onTrackMouseMove}
          onMouseUp={() => { dragging.current = null; }}
          onMouseLeave={() => { dragging.current = null; }}
        >
          <div
            className="absolute top-0 h-full bg-[var(--gold-dim)] border-x border-[var(--gold-border)]"
            style={{ left: `${startPct}%`, width: `${endPct - startPct}%` }}
          />
          <div
            className="absolute top-0 h-full w-3 cursor-ew-resize flex items-center justify-center group"
            style={{ left: `calc(${startPct}% - 6px)` }}
            onMouseDown={(e) => { e.preventDefault(); dragging.current = "start"; }}
          >
            <div className="w-1 h-5 rounded-full bg-[var(--gold)] opacity-80 group-hover:opacity-100" />
          </div>
          <div
            className="absolute top-0 h-full w-3 cursor-ew-resize flex items-center justify-center group"
            style={{ left: `calc(${endPct}% - 6px)` }}
            onMouseDown={(e) => { e.preventDefault(); dragging.current = "end"; }}
          >
            <div className="w-1 h-5 rounded-full bg-[var(--gold)] opacity-80 group-hover:opacity-100" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <label className="space-y-1">
            <span className="text-[10px] font-semibold uppercase tracking-[0.15em] text-ink/46">Start (s)</span>
            <input
              type="number"
              step="0.1"
              min={0}
              max={trimEnd - 0.5}
              value={trimStart.toFixed(1)}
              onChange={(e) => setTrimStart(clampedInput(e.target.value, 0, trimEnd - 0.5))}
              className="w-full rounded-xl border border-white/10 bg-white/[0.05] px-3 py-2 text-sm text-ink outline-none focus:border-[var(--gold-border)]"
            />
          </label>
          <label className="space-y-1">
            <span className="text-[10px] font-semibold uppercase tracking-[0.15em] text-ink/46">End (s)</span>
            <input
              type="number"
              step="0.1"
              min={trimStart + 0.5}
              max={duration}
              value={trimEnd.toFixed(1)}
              onChange={(e) => setTrimEnd(clampedInput(e.target.value, trimStart + 0.5, duration))}
              className="w-full rounded-xl border border-white/10 bg-white/[0.05] px-3 py-2 text-sm text-ink outline-none focus:border-[var(--gold-border)]"
            />
          </label>
        </div>
        <p className="text-[10px] text-ink/40">
          Duration: {formatTime(trimEnd - trimStart)} &nbsp;·&nbsp; Clip length: {formatTime(duration)}
        </p>
      </div>

      {/* Caption burn */}
      <div className="space-y-3">
        <label className="flex items-center gap-3 cursor-pointer">
          <div
            className={[
              "relative h-5 w-9 rounded-full transition",
              burnCaptions ? "bg-[var(--gold)]" : "bg-white/10",
            ].join(" ")}
            onClick={() => setBurnCaptions((v) => !v)}
          >
            <div
              className={[
                "absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform",
                burnCaptions ? "translate-x-4" : "translate-x-0.5",
              ].join(" ")}
            />
          </div>
          <span className="text-sm text-ink">Burn captions into clip</span>
        </label>
        {burnCaptions && (
          <textarea
            rows={3}
            value={captionText}
            onChange={(e) => setCaptionText(e.target.value)}
            placeholder="Caption text to burn in..."
            className="w-full rounded-xl border border-white/10 bg-white/[0.05] px-3 py-2 text-sm text-ink outline-none focus:border-[var(--gold-border)] resize-none"
          />
        )}
      </div>

      {error && <p className="text-xs text-red-400">{error}</p>}
      {saved && <p className="text-xs text-[var(--gold)]">Saved — processed clip available in history.</p>}

      <button
        type="button"
        onClick={handleSave}
        disabled={saving || saved}
        className="w-full rounded-full bg-[var(--gold)] py-2.5 text-sm font-semibold text-black transition hover:opacity-90 disabled:opacity-50"
      >
        {saving ? "Processing…" : saved ? "Saved" : "Apply trim & save"}
      </button>
    </div>
  );
}
