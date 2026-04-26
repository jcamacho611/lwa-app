"use client";

import type { ClipResult } from "../../lib/types";
import { RESULT_COPY } from "../../lib/result-copy";
import { useClipPreviewPolling } from "../../hooks/useClipPreviewPolling";

type ClipPreviewProps = {
  clip: Pick<
    ClipResult,
    | "id"
    | "request_id"
    | "preview_url"
    | "edited_clip_url"
    | "clip_url"
    | "raw_clip_url"
    | "thumbnail_url"
    | "preview_image_url"
    | "title"
    | "hook"
    | "caption"
    | "score"
    | "virality_score"
    | "platform_fit"
    | "start_time"
    | "end_time"
    | "render_status"
  >;
  className?: string;
  autoPlay?: boolean;
};

function formatTime(value?: string | number | null) {
  if (value == null) return "--:--";
  if (typeof value === "string") return value || "--:--";
  if (Number.isNaN(value)) return "--:--";
  const mins = Math.floor(value / 60);
  const secs = Math.floor(value % 60).toString().padStart(2, "0");
  return `${mins}:${secs}`;
}

export default function ClipPreview({ clip, className = "aspect-[9/16]", autoPlay = false }: ClipPreviewProps) {
  const liveClip = useClipPreviewPolling(clip);
  const playable = liveClip.preview_url || liveClip.edited_clip_url || liveClip.clip_url || liveClip.raw_clip_url;
  const thumbnail = liveClip.thumbnail_url || liveClip.preview_image_url;
  const shellClassName = `relative h-full w-full overflow-hidden rounded-[inherit] ${className}`;
  const scoreValue = Math.round(liveClip.virality_score ?? liveClip.score ?? 0);
  const showScore = scoreValue >= 70;
  const platformTag = liveClip.platform_fit || "Short-form";
  const captionPreview = liveClip.caption || liveClip.hook || RESULT_COPY.previewProcessing;

  if (playable) {
    return (
      <video
        src={playable}
        poster={thumbnail || undefined}
        controls={!autoPlay}
        autoPlay={autoPlay}
        muted={autoPlay}
        loop={autoPlay}
        playsInline
        preload="metadata"
        className={`${shellClassName} bg-black object-cover`}
      />
    );
  }

  if (thumbnail) {
    return (
      <div className={shellClassName}>
        <img src={thumbnail} alt={liveClip.title || liveClip.hook || "Clip preview"} className="h-full w-full object-cover" />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,var(--surface-veil)_0%,var(--surface-veil-heavy)_100%)]" />
        <div className="absolute inset-x-4 bottom-4 rounded-[24px] border border-[var(--gold-border)] bg-[var(--surface-veil-strong)] px-4 py-4 backdrop-blur-md">
          <div className="flex flex-wrap gap-2">
            {showScore ? <span className="score-badge">{scoreValue}/10</span> : null}
            <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1 text-[11px] font-semibold text-[var(--gold)]">
              {platformTag}
            </span>
          </div>
          <p className="mt-3 text-lg font-semibold leading-7 text-[var(--gold)]">{liveClip.hook || liveClip.title}</p>
          <p className="mt-2 line-clamp-2 text-sm leading-6 text-[var(--ink-mid)]">{captionPreview}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${shellClassName} flex min-h-[280px] items-end border border-[var(--gold-border)] bg-[radial-gradient(circle_at_top,var(--surface-gold-glow),transparent_26%),linear-gradient(180deg,var(--bg-card)_0%,var(--bg)_100%)] p-5`}>
      <div className="w-full rounded-[24px] border border-[var(--gold-border)] bg-[var(--surface-veil)] px-5 py-5 backdrop-blur-md">
        <div className="flex flex-wrap gap-2">
          {showScore ? <span className="score-badge">{scoreValue}/10</span> : null}
          <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1 text-[11px] font-semibold text-[var(--gold)]">
            {platformTag}
          </span>
        </div>
        <p className="mt-4 text-xl font-semibold leading-7 text-[var(--gold)]">{liveClip.hook || liveClip.title}</p>
        <p className="mt-3 line-clamp-2 text-sm leading-6 text-[var(--ink-mid)]">{captionPreview}</p>
        <p className="mt-3 text-xs text-[var(--ink-faint)]">
          {formatTime(liveClip.start_time)} - {formatTime(liveClip.end_time)}
        </p>
      </div>
    </div>
  );
}
