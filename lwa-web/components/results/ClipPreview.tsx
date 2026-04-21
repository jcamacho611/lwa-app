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
        <div className="absolute inset-0 bg-black/35" />
        <div className="absolute bottom-4 left-4 right-4 rounded-2xl border border-white/10 bg-black/35 px-4 py-3 backdrop-blur-md">
          <p className="text-xs uppercase tracking-[0.24em] text-cyan-300/70">{RESULT_COPY.previewProcessing}</p>
          <p className="mt-2 text-sm text-white/80">
            {formatTime(liveClip.start_time)} - {formatTime(liveClip.end_time)}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${shellClassName} flex min-h-[280px] items-center justify-center border border-white/10 bg-[radial-gradient(circle_at_top,_rgba(90,40,180,0.28),_rgba(3,8,28,0.94)_58%)]`}>
      <div className="absolute inset-0 opacity-60">
        <div className="absolute left-[12%] top-[14%] h-20 w-20 rounded-full bg-fuchsia-500/18 blur-2xl" />
        <div className="absolute bottom-[10%] right-[12%] h-24 w-24 rounded-full bg-cyan-400/18 blur-2xl" />
      </div>

      <div className="relative z-10 rounded-[24px] border border-white/12 bg-black/25 px-6 py-5 text-center backdrop-blur-xl">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-300/70">{RESULT_COPY.previewProcessing}</p>
        <p className="mt-3 text-sm text-white/80">
          {formatTime(liveClip.start_time)} - {formatTime(liveClip.end_time)}
        </p>
      </div>
    </div>
  );
}
