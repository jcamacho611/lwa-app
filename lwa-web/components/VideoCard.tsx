"use client";

import { useRef, useState } from "react";
import { ClipResult } from "../lib/types";

export type VideoCardProps = {
  clip: ClipResult;
  feedbackVote?: "good" | "bad" | null;
  onVote?: (clip: ClipResult, vote: "good" | "bad") => void;
  queued?: boolean;
  onToggleQueue?: (clip: ClipResult) => void;
};

export default function VideoCard({
  clip,
  feedbackVote = null,
  onVote,
  queued = false,
  onToggleQueue,
}: VideoCardProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [isHovering, setIsHovering] = useState(false);

  const previewUrl = clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url || null;
  const thumbnailUrl = clip.thumbnail_url || clip.preview_image_url || null;
  const downloadUrl = clip.download_url || null;
  const scoreLabel = clip.virality_score ?? clip.score;

  async function handleEnter() {
    setIsHovering(true);
    const video = videoRef.current;
    if (!video || !previewUrl) {
      return;
    }

    try {
      video.currentTime = 0;
      await video.play();
    } catch {
      // Ignore autoplay rejections and keep the poster visible.
    }
  }

  function handleLeave() {
    setIsHovering(false);
    const video = videoRef.current;
    if (!video) {
      return;
    }

    video.pause();
    video.currentTime = 0;
  }

  return (
    <article
      className="video-card group rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.015)),linear-gradient(180deg,rgba(16,24,46,0.88),rgba(10,16,35,0.94))] p-4 shadow-card transition duration-300 hover:-translate-y-1 hover:border-white/16"
      onMouseEnter={() => void handleEnter()}
      onMouseLeave={handleLeave}
    >
      <div className="video-shell overflow-hidden rounded-[22px] border border-white/10 bg-black/60">
        {previewUrl ? (
          <video
            ref={videoRef}
            src={previewUrl}
            poster={thumbnailUrl || undefined}
            className="aspect-[9/16] w-full bg-black object-cover transition duration-300 group-hover:scale-[1.01]"
            muted
            loop
            playsInline
            preload="metadata"
          />
        ) : thumbnailUrl ? (
          <img src={thumbnailUrl} alt={clip.hook} className="aspect-[9/16] w-full bg-black object-cover" />
        ) : (
          <div className="flex aspect-[9/16] items-center justify-center bg-[radial-gradient(circle_at_top,rgba(124,58,237,0.24),transparent_44%),linear-gradient(180deg,#030712,#050816)] text-sm text-ink/56">
            Preview unavailable
          </div>
        )}

        <div className="video-overlay pointer-events-none absolute inset-x-0 bottom-0 p-3">
          <div className="flex items-center justify-between gap-3">
            <span className="status-chip status-submitted">Score {scoreLabel}</span>
            <span className="rounded-full border border-white/10 bg-black/35 px-3 py-1.5 text-[11px] font-medium text-white/82 backdrop-blur">
              {isHovering ? "Previewing" : "Hover to play"}
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <div className="space-y-2">
          <h3 className="line-clamp-2 text-lg font-semibold leading-tight text-ink">{clip.hook}</h3>
          <p className="line-clamp-2 text-sm leading-6 text-ink/64">{clip.caption}</p>
        </div>

        <div className="flex flex-wrap gap-2">
          {clip.platform_fit ? (
            <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">
              {clip.platform_fit}
            </span>
          ) : null}
          {clip.best_post_order ? (
            <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">
              Post #{clip.best_post_order}
            </span>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => onToggleQueue?.(clip)}
            className={[
              "secondary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium",
              queued ? "border-neonPurple/30 bg-neonPurple/15 text-white shadow-neon" : "",
            ].join(" ")}
          >
            {queued ? "Queued" : "Mark ready"}
          </button>
          {downloadUrl ? (
            <a
              href={downloadUrl}
              download
              className="primary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-semibold"
            >
              Download
            </a>
          ) : (
            <span className="rounded-full border border-neonPurple/18 bg-neonPurple/10 px-4 py-2 text-sm text-white/78">
              Pro unlocks download
            </span>
          )}
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => onVote?.(clip, "good")}
            className={[
              "rounded-full border px-3 py-1.5 text-xs font-medium transition",
              feedbackVote === "good"
                ? "border-emerald-400/30 bg-emerald-400/12 text-emerald-200"
                : "border-white/12 bg-white/[0.05] text-ink/76 hover:border-emerald-400/30 hover:bg-emerald-400/10 hover:text-emerald-200",
            ].join(" ")}
          >
            Good
          </button>
          <button
            type="button"
            onClick={() => onVote?.(clip, "bad")}
            className={[
              "rounded-full border px-3 py-1.5 text-xs font-medium transition",
              feedbackVote === "bad"
                ? "border-red-400/30 bg-red-400/10 text-red-100"
                : "border-white/12 bg-white/[0.05] text-ink/76 hover:border-red-400/30 hover:bg-red-400/10 hover:text-red-100",
            ].join(" ")}
          >
            Bad
          </button>
        </div>
      </div>
    </article>
  );
}
