"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ClipResult } from "../lib/types";

type HeroClipProps = {
  clip: ClipResult;
  queued?: boolean;
  feedbackVote?: "good" | "bad" | null;
  onToggleQueue?: (clip: ClipResult) => void;
  onVote?: (clip: ClipResult, vote: "good" | "bad") => void;
};

function formatConfidence(value?: number | null) {
  if (typeof value !== "number") {
    return null;
  }

  return `${Math.round(value * 100)}% confidence`;
}

export default function HeroClip({
  clip,
  queued = false,
  feedbackVote = null,
  onToggleQueue,
  onVote,
}: HeroClipProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(true);

  const previewUrl = clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url || null;
  const thumbnailUrl = clip.thumbnail_url || clip.preview_image_url || null;
  const downloadUrl = clip.download_url || null;
  const whyThisHits = clip.why_this_matters || clip.reason || "Clear setup, quick payoff, and packaging built to travel.";
  const confidenceScore = clip.confidence_score ?? (typeof clip.confidence === "number" ? Math.round(clip.confidence * 100) : null);
  const confidenceLabel = confidenceScore ? `${confidenceScore}% confidence` : formatConfidence(clip.confidence);
  const scoreLabel = useMemo(() => clip.virality_score ?? clip.score, [clip.score, clip.virality_score]);
  const postRank = clip.post_rank || clip.best_post_order || clip.rank || null;
  const captionStyle = clip.caption_style || clip.caption_style_override || null;
  const hookVariants = (clip.hook_variants || []).filter((variant) => variant && variant !== clip.hook).slice(0, 2);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !previewUrl) {
      return;
    }

    video.muted = true;
    const playPromise = video.play();
    if (playPromise) {
      void playPromise.then(() => setIsPlaying(true)).catch(() => setIsPlaying(false));
    }
  }, [previewUrl]);

  async function togglePlayback() {
    const video = videoRef.current;
    if (!video) {
      return;
    }

    if (video.paused) {
      try {
        await video.play();
        setIsPlaying(true);
      } catch {
        setIsPlaying(false);
      }
      return;
    }

    video.pause();
    setIsPlaying(false);
  }

  return (
    <section className="hero-card rounded-[34px] p-5 sm:p-6 lg:p-7 animate-fade-in">
      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.68fr),minmax(320px,0.32fr)] xl:items-start">
        <div className="space-y-4">
          <div className="video-shell overflow-hidden rounded-[28px] border border-white/10 bg-black/50">
            {previewUrl ? (
              <video
                ref={videoRef}
                src={previewUrl}
                poster={thumbnailUrl || undefined}
                className="aspect-[9/16] w-full bg-black object-cover"
                autoPlay
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

            <div className="video-overlay pointer-events-none absolute inset-x-0 bottom-0 flex items-end justify-between gap-3 p-4">
              <div className="flex flex-wrap gap-2">
                <span className="status-chip status-approved">Lead clip</span>
                <span className="status-chip status-submitted">Score {scoreLabel}</span>
                {clip.platform_fit ? <span className="status-chip status-ready">{clip.platform_fit}</span> : null}
              </div>
              {postRank ? <span className="status-chip status-draft">Post #{postRank}</span> : null}
            </div>
          </div>
        </div>

        <div className="space-y-5">
          <div className="space-y-3">
            <p className="section-kicker">Top result</p>
            <h2 className="text-2xl font-semibold leading-tight text-ink sm:text-[2rem]">{clip.hook}</h2>
            <p className="text-sm leading-7 text-ink/72">{clip.caption}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            {clip.packaging_angle ? (
              <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">
                {clip.packaging_angle}
              </span>
            ) : null}
            {confidenceLabel ? (
              <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">
                {confidenceLabel}
              </span>
            ) : null}
            {captionStyle ? (
              <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">
                {captionStyle}
              </span>
            ) : null}
            {clip.start_time && clip.end_time ? (
              <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">
                {clip.start_time} - {clip.end_time}
              </span>
            ) : null}
          </div>

          <div className="signal-card rounded-[24px] p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Why this lands</p>
              <p className="text-sm leading-6 text-ink/82">{whyThisHits}</p>
            </div>

          <div className="grid gap-3 md:grid-cols-2">
            {clip.thumbnail_text ? (
              <div className="metric-tile rounded-[24px] p-4">
                <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Thumbnail line</p>
                <p className="text-sm font-medium text-ink">{clip.thumbnail_text}</p>
              </div>
            ) : null}
            {clip.cta_suggestion ? (
              <div className="metric-tile rounded-[24px] p-4">
                <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">CTA</p>
                <p className="text-sm font-medium text-ink">{clip.cta_suggestion}</p>
              </div>
            ) : null}
          </div>

          {hookVariants.length ? (
            <div className="metric-tile rounded-[24px] p-4">
              <p className="mb-3 text-xs uppercase tracking-[0.24em] text-muted">Alternate hooks</p>
              <div className="flex flex-wrap gap-2">
                {hookVariants.map((variant) => (
                  <span key={variant} className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-2 text-xs text-ink/78">
                    {variant}
                  </span>
                ))}
              </div>
            </div>
          ) : null}

          <div className="flex flex-wrap gap-3">
            {previewUrl ? (
              <button
                type="button"
                onClick={() => void togglePlayback()}
                className="primary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold"
              >
                {isPlaying ? "Pause clip" : "Play clip"}
              </button>
            ) : null}
            {downloadUrl ? (
              <a
                href={downloadUrl}
                download
                className="secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium"
              >
                Export clip
              </a>
            ) : (
              <span className="rounded-full border border-neonPurple/20 bg-neonPurple/10 px-4 py-3 text-sm text-[#fff4d4]">
                Pro export
              </span>
            )}
            <button
              type="button"
              onClick={() => onToggleQueue?.(clip)}
              className={[
                "secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium",
                queued ? "border-neonPurple/30 bg-neonPurple/15 text-white shadow-neon" : "",
              ].join(" ")}
            >
              {queued ? "Queued" : "Queue clip"}
            </button>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => onVote?.(clip, "good")}
              className={[
                "rounded-full border px-4 py-2 text-sm font-medium transition",
                feedbackVote === "good"
                  ? "border-emerald-400/30 bg-emerald-400/12 text-emerald-200"
                  : "border-white/12 bg-white/[0.06] text-ink hover:border-emerald-400/30 hover:bg-emerald-400/10 hover:text-emerald-200",
              ].join(" ")}
            >
              Good clip
            </button>
            <button
              type="button"
              onClick={() => onVote?.(clip, "bad")}
              className={[
                "rounded-full border px-4 py-2 text-sm font-medium transition",
                feedbackVote === "bad"
                  ? "border-red-400/30 bg-red-400/10 text-red-100"
                  : "border-white/12 bg-white/[0.06] text-ink hover:border-red-400/30 hover:bg-red-400/10 hover:text-red-100",
              ].join(" ")}
            >
              Bad clip
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
