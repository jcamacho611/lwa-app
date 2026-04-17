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
  const [copiedHook, setCopiedHook] = useState(false);

  const previewUrl = clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url || null;
  const thumbnailUrl = clip.thumbnail_url || clip.preview_image_url || null;
  const downloadUrl = clip.download_url || null;
  const scoreLabel = clip.virality_score ?? clip.score;
  const confidenceScore = clip.confidence_score ?? (typeof clip.confidence === "number" ? Math.round(clip.confidence * 100) : null);
  const whyThisHits = clip.why_this_matters || clip.reason || null;
  const captionStyle = clip.caption_style || null;
  const postRank = clip.post_rank || clip.best_post_order || clip.rank || null;

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

  async function handleCopyHook() {
    try {
      await navigator.clipboard.writeText(clip.hook);
      setCopiedHook(true);
      window.setTimeout(() => setCopiedHook(false), 1600);
    } catch {
      setCopiedHook(false);
    }
  }

  return (
    <article
      className="video-card group rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.015)),linear-gradient(180deg,rgba(18,7,10,0.9),rgba(8,4,6,0.98))] p-4 shadow-card transition duration-300 hover:-translate-y-1 hover:border-white/16"
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
          <div className="flex aspect-[9/16] items-center justify-center bg-[radial-gradient(circle_at_top,rgba(255,30,86,0.24),transparent_44%),radial-gradient(circle_at_80%_20%,rgba(0,231,255,0.14),transparent_38%),linear-gradient(180deg,#040405,#0d080b)] text-sm text-ink/56">
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
          {postRank ? (
            <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">
              Post #{postRank}
            </span>
          ) : null}
          {confidenceScore ? (
            <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">
              {confidenceScore}% confidence
            </span>
          ) : null}
          {captionStyle ? (
            <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">
              {captionStyle}
            </span>
          ) : null}
        </div>

        {whyThisHits ? (
          <div className="signal-card rounded-[20px] px-3 py-3">
            <p className="mb-1 text-[10px] uppercase tracking-[0.22em] text-muted">Why this lands</p>
            <p className="line-clamp-3 text-xs leading-6 text-ink/78">{whyThisHits}</p>
          </div>
        ) : null}

        {clip.thumbnail_text || clip.cta_suggestion ? (
          <div className="clip-quick-pack grid gap-2">
            {clip.thumbnail_text ? (
              <div className="rounded-[18px] border border-white/8 bg-white/[0.04] px-3 py-2.5">
                <p className="text-[10px] uppercase tracking-[0.22em] text-muted">Thumbnail</p>
                <p className="mt-1 text-xs font-medium text-ink/82">{clip.thumbnail_text}</p>
              </div>
            ) : null}
            {clip.cta_suggestion ? (
              <div className="rounded-[18px] border border-white/8 bg-white/[0.04] px-3 py-2.5">
                <p className="text-[10px] uppercase tracking-[0.22em] text-muted">CTA</p>
                <p className="mt-1 text-xs font-medium text-ink/82">{clip.cta_suggestion}</p>
              </div>
            ) : null}
          </div>
        ) : null}

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => onToggleQueue?.(clip)}
            className={[
              "secondary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium",
              queued ? "border-accentCrimson/35 bg-[linear-gradient(135deg,rgba(255,0,60,0.18),rgba(255,45,166,0.1))] text-white shadow-crimson" : "",
            ].join(" ")}
          >
            {queued ? "Queued" : "Queue clip"}
          </button>
          {downloadUrl ? (
            <a
              href={downloadUrl}
              download
              className="primary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-semibold"
            >
              Export
            </a>
          ) : (
            <span className="rounded-full border border-accentCrimson/24 bg-[linear-gradient(135deg,rgba(255,0,60,0.14),rgba(255,45,166,0.1))] px-4 py-2 text-sm text-[#ffe4eb]">
              Pro export
            </span>
          )}
          <button
            type="button"
            onClick={() => void handleCopyHook()}
            className="secondary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium"
          >
            {copiedHook ? "Hook copied" : "Copy hook"}
          </button>
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
