"use client";

import { useState } from "react";
import { ClipResult } from "../lib/types";
import { LiveClipPreview } from "./results/LiveClipPreview";
import { RetryPreviewButton } from "./results/RetryPreviewButton";
import { hasPreviewAsset, isRenderedClip } from "../lib/clip-utils";
import { RESULT_COPY, buildLeadReason } from "../lib/result-copy";

export type VideoCardProps = {
  clip: ClipResult;
  compact?: boolean;
  feedbackVote?: "good" | "bad" | null;
  onVote?: (clip: ClipResult, vote: "good" | "bad") => void;
  queued?: boolean;
  onToggleQueue?: (clip: ClipResult) => void;
  recoveryState?: {
    status: "queued" | "processing" | "recovered" | "failed";
    message: string;
    error?: string | null;
  } | null;
  onRecover?: (clip: ClipResult) => void;
};

function authorityLabel(rank?: number | null) {
  if (rank === 1) return "POST FIRST";
  if (rank === 2) return "POST SECOND";
  if (rank === 3) return "TEST THIRD";
  return "MOVE LATER";
}

function buildPackageText(clip: ClipResult) {
  const thumbnailText = clip.thumbnail_text && clip.thumbnail_text !== "Best Clip"
    ? clip.thumbnail_text
    : clip.hook?.slice(0, 40) || clip.title;
  return [
    `Title: ${clip.title}`,
    `Hook: ${clip.hook}`,
    `Caption: ${clip.caption}`,
    `Why this matters: ${clip.why_this_matters || clip.reason || "Not available"}`,
    `Post order: ${authorityLabel(clip.post_rank || clip.best_post_order || clip.rank || null)}`,
    `Packaging angle: ${clip.packaging_angle || "value"}`,
    `Thumbnail text: ${thumbnailText}`,
    `CTA: ${clip.cta_suggestion || "Ask viewers to comment or follow."}`,
  ].join("\n");
}

function decisionText(rank?: number | null, hasRenderProof?: boolean) {
  if (rank === 1) return "Post this first";
  if (rank === 2) return "Post this next";
  if (rank === 3) return "Continuation clip";
  return hasRenderProof ? "Ready to move" : "High viral potential";
}

export default function VideoCard({
  clip,
  compact = false,
  feedbackVote = null,
  onVote,
  queued = false,
  onToggleQueue,
  recoveryState = null,
  onRecover,
}: VideoCardProps) {
  const [copiedPackage, setCopiedPackage] = useState(false);

  const previewUrl = clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url || null;
  const downloadUrl = clip.download_url || null;
  const hasPlayablePreview = isRenderedClip(clip);
  const hasRenderProof = hasPreviewAsset(clip);
  const whyThisHits = buildLeadReason(clip.why_this_matters || clip.reason);
  const captionStyle = clip.caption_style || null;
  const postRank = clip.post_rank || clip.best_post_order || clip.rank || null;
  const authority = authorityLabel(postRank);
  const decision = decisionText(postRank, hasRenderProof);
  const scoreValue = Math.round(clip.virality_score ?? clip.score ?? 0);
  const showScore = !compact && scoreValue >= 70;
  const showFeedback = !compact && Boolean(onVote);
  const displayThumbnail = clip.thumbnail_text && clip.thumbnail_text !== "Best Clip"
    ? clip.thumbnail_text
    : clip.hook?.slice(0, 40) || clip.title;

  async function handleCopyPackage() {
    try {
      await navigator.clipboard.writeText(buildPackageText(clip));
      setCopiedPackage(true);
      window.setTimeout(() => setCopiedPackage(false), 1600);
    } catch {
      setCopiedPackage(false);
    }
  }

  return (
    <article
      className={[
        "clip-card result-clip-card group rounded-[28px] border p-4 shadow-card transition-all duration-300 hover:scale-[1.02] hover:shadow-xl",
        postRank === 1 ? "top-pick" : "",
        hasRenderProof
          ? "hover:border-[var(--gold-border)]"
          : "opacity-88 hover:border-[var(--gold-border)]",
      ].join(" ")}
    >
      {postRank === 1 ? (
        <div className="-mx-4 -mt-4 mb-4 bg-[var(--gold)] px-4 py-2 text-[10px] font-bold tracking-[0.14em] text-black">
          #1 PICK — POST FIRST
        </div>
      ) : null}
      <div className="video-shell overflow-hidden rounded-[22px] border border-white/10 bg-black/60">
        {compact && !hasRenderProof ? (
          <div className="flex aspect-[9/16] min-h-[260px] flex-col items-start justify-end bg-gradient-to-b from-[#0d0d14] to-[#050508] px-5 pb-6">
            <span className="mb-3 inline-block rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1 text-xs font-bold tracking-widest text-[var(--gold)]">
              {authority}
            </span>
            <p className="text-lg font-semibold leading-7 text-white">{clip.hook || clip.title}</p>
            <p className="mt-2 text-xs text-white/35">{clip.timestamp_start || clip.start_time} — {clip.timestamp_end || clip.end_time}</p>
          </div>
        ) : (
          <LiveClipPreview clip={clip} className="aspect-[9/16] transition duration-300 group-hover:scale-[1.02]" />
        )}

        {!compact ? (
          <div className="video-overlay pointer-events-none absolute inset-x-0 bottom-0 p-3">
          <div className="flex items-center justify-between gap-3">
            <span
              className={[
                "rounded-full px-3 py-1.5 text-[11px] font-semibold tracking-[0.16em]",
                hasRenderProof ? "bg-[var(--gold-dim)] text-[var(--gold)]" : "bg-[var(--crimson-dim)] text-red-100",
              ].join(" ")}
            >
              {hasRenderProof ? "READY NOW" : "RENDERING AVAILABLE ON PRO"}
            </span>
            <span className="rounded-full border border-white/10 bg-black/35 px-3 py-1.5 text-[11px] font-medium text-white/82 backdrop-blur">
              {hasPlayablePreview ? "Preview ready" : hasRenderProof ? RESULT_COPY.previewProcessing : RESULT_COPY.ideasOnly}
            </span>
          </div>
        </div>
        ) : null}
      </div>

      <div className="mt-4 space-y-3">
        <div className="flex flex-wrap gap-2">
          {showScore ? <span className="score-badge">{scoreValue}/10</span> : null}
          <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/82">{authority}</span>
          {!compact ? (
            <>
              <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">
                {hasRenderProof ? "Ready now" : "Rendering available on Pro"}
              </span>
              {clip.confidence_label ? (
                <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1.5 text-xs text-[var(--gold)]">
                  {clip.confidence_label}
                </span>
              ) : null}
              {captionStyle ? (
                <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">{captionStyle}</span>
              ) : null}
            </>
          ) : null}
        </div>

        <div className="space-y-2">
          {!compact ? <h3 className="line-clamp-2 text-lg font-semibold leading-tight text-ink">{clip.title}</h3> : null}
          {!compact ? <p className="text-sm font-medium uppercase tracking-[0.18em] text-white/62">{decision}</p> : null}
          <p className={compact ? "text-xl font-semibold leading-7 text-white" : "line-clamp-2 text-sm leading-6 text-ink/80"}>
            {clip.hook || clip.title}
          </p>
        </div>

        <div className="grid gap-2">
          {displayThumbnail ? (
            <div className="rounded-[18px] border border-white/8 bg-white/[0.04] px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[0.22em] text-muted">Thumbnail</p>
              <p className="mt-1 text-xs font-medium text-ink/82">{displayThumbnail}</p>
            </div>
          ) : null}
          {clip.cta_suggestion ? (
            <div className="rounded-[18px] border border-white/8 bg-white/[0.04] px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[0.22em] text-muted">Move</p>
              <p className="mt-1 text-xs font-medium text-ink/82">{clip.cta_suggestion}</p>
            </div>
          ) : null}
        </div>

        {!compact && whyThisHits ? (
          <details className="rounded-[18px] border border-white/8 bg-white/[0.04] px-3 py-2.5">
            <summary className="cursor-pointer list-none text-[10px] uppercase tracking-[0.22em] text-muted transition-colors duration-300 hover:text-ink/76">
              Open package notes
            </summary>
            <p className="mt-2 text-xs leading-6 text-ink/62">{whyThisHits}</p>
          </details>
        ) : null}

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => onToggleQueue?.(clip)}
            className={[
              "secondary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium",
              queued ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]" : "",
            ].join(" ")}
          >
            {queued ? "Queued" : "Add to Queue"}
          </button>

          {!compact && downloadUrl ? (
            <a
              href={downloadUrl}
              download
              className="primary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-semibold"
            >
              Download
            </a>
          ) : !compact && hasPlayablePreview ? (
            <a
              href={previewUrl || undefined}
              target="_blank"
              rel="noreferrer"
              className="secondary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium"
            >
              Open preview
            </a>
          ) : null}

          {!hasRenderProof ? (
            <RetryPreviewButton
              onRetry={() => onRecover?.(clip)}
              disabled={recoveryState?.status === "queued" || recoveryState?.status === "processing"}
              label={recoveryState?.status === "processing"
                ? "Recovering..."
                : recoveryState?.status === "queued"
                  ? "Recovery queued"
                  : recoveryState?.status === "failed"
                    ? RESULT_COPY.previewRetry
                    : RESULT_COPY.previewRetry}
            />
          ) : null}

          <button
            type="button"
            onClick={() => void handleCopyPackage()}
            className="secondary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium"
          >
            {copiedPackage ? "Package copied" : "Copy package"}
          </button>
        </div>

        {showFeedback ? (
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => onVote?.(clip, "good")}
            className={[
              "rounded-full border px-3 py-1.5 text-xs font-medium transition",
              feedbackVote === "good"
                ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]"
                : "border-white/12 bg-white/[0.05] text-ink/76 hover:border-[var(--gold-border)] hover:bg-[var(--gold-dim)] hover:text-[var(--gold)]",
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
        ) : null}
      </div>
    </article>
  );
}
