"use client";

import { useState } from "react";
import { ClipResult } from "../lib/types";
import ClipPreview from "./results/ClipPreview";
import { hasPreviewAsset, isRenderedClip } from "../lib/clip-utils";
import { RESULT_COPY, buildLeadReason } from "../lib/result-copy";

export type VideoCardProps = {
  clip: ClipResult;
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
  return [
    `Title: ${clip.title}`,
    `Hook: ${clip.hook}`,
    `Caption: ${clip.caption}`,
    `Why this matters: ${clip.why_this_matters || clip.reason || "Not available"}`,
    `Post order: ${authorityLabel(clip.post_rank || clip.best_post_order || clip.rank || null)}`,
    `Packaging angle: ${clip.packaging_angle || "value"}`,
    `Thumbnail text: ${clip.thumbnail_text || "Best Clip"}`,
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
        "group rounded-[28px] border p-4 shadow-card transition-all duration-300 hover:scale-[1.02] hover:shadow-xl",
        hasRenderProof
          ? "border-cyan-300/14 bg-[linear-gradient(180deg,rgba(255,255,255,0.045),rgba(255,255,255,0.015)),linear-gradient(180deg,rgba(8,12,34,0.9),rgba(3,5,16,0.98))] hover:border-cyan-300/24"
          : "border-violet-300/14 bg-[linear-gradient(180deg,rgba(124,58,237,0.07),rgba(56,189,248,0.02)),linear-gradient(180deg,rgba(8,9,28,0.94),rgba(3,5,16,0.98))] opacity-88 hover:border-violet-300/24",
      ].join(" ")}
    >
      <div className="video-shell overflow-hidden rounded-[22px] border border-white/10 bg-black/60">
        <ClipPreview clip={clip} className="aspect-[9/16] transition duration-300 group-hover:scale-[1.02]" />

        <div className="video-overlay pointer-events-none absolute inset-x-0 bottom-0 p-3">
          <div className="flex items-center justify-between gap-3">
            <span
              className={[
                "rounded-full px-3 py-1.5 text-[11px] font-semibold tracking-[0.16em]",
                hasRenderProof ? "bg-cyan-300/12 text-cyan-100" : "bg-violet-300/12 text-violet-100",
              ].join(" ")}
            >
              {hasRenderProof ? "READY NOW" : "HIGH LEVERAGE"}
            </span>
            <span className="rounded-full border border-white/10 bg-black/35 px-3 py-1.5 text-[11px] font-medium text-white/82 backdrop-blur">
              {hasPlayablePreview ? "Preview ready" : hasRenderProof ? RESULT_COPY.previewProcessing : RESULT_COPY.ideasOnly}
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <div className="flex flex-wrap gap-2">
          <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/82">{authority}</span>
          <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">
            {hasRenderProof ? "Ready now" : "High viral potential"}
          </span>
          {captionStyle ? (
            <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/76">{captionStyle}</span>
          ) : null}
        </div>

        <div className="space-y-2">
          <h3 className="line-clamp-2 text-lg font-semibold leading-tight text-ink">{clip.title}</h3>
          <p className="text-sm font-medium uppercase tracking-[0.18em] text-white/62">{decision}</p>
          <p className="line-clamp-2 text-sm leading-6 text-ink/80">{clip.hook}</p>
        </div>

        <div className="grid gap-2">
          {clip.thumbnail_text ? (
            <div className="rounded-[18px] border border-white/8 bg-white/[0.04] px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[0.22em] text-muted">Thumbnail</p>
              <p className="mt-1 text-xs font-medium text-ink/82">{clip.thumbnail_text}</p>
            </div>
          ) : null}
          {clip.cta_suggestion ? (
            <div className="rounded-[18px] border border-white/8 bg-white/[0.04] px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[0.22em] text-muted">Move</p>
              <p className="mt-1 text-xs font-medium text-ink/82">{clip.cta_suggestion}</p>
            </div>
          ) : null}
        </div>

        {whyThisHits ? (
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
              queued ? "border-cyan-300/35 bg-[linear-gradient(135deg,rgba(0,231,255,0.16),rgba(124,58,237,0.12))] text-white shadow-cyan" : "",
            ].join(" ")}
          >
            {queued ? "Queued for post" : "Queue post"}
          </button>

          {downloadUrl ? (
            <a
              href={downloadUrl}
              download
              className="primary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-semibold"
            >
              Export clip
            </a>
          ) : hasPlayablePreview ? (
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
            <button
              type="button"
              onClick={() => onRecover?.(clip)}
              disabled={recoveryState?.status === "queued" || recoveryState?.status === "processing"}
              className="secondary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-60"
            >
              {recoveryState?.status === "processing"
                ? "Recovering..."
                : recoveryState?.status === "queued"
                  ? "Recovery queued"
                  : recoveryState?.status === "failed"
                    ? RESULT_COPY.previewRetry
                    : RESULT_COPY.previewRetry}
            </button>
          ) : null}

          <button
            type="button"
            onClick={() => void handleCopyPackage()}
            className="secondary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium"
          >
            {copiedPackage ? "Package copied" : "Copy package"}
          </button>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => onVote?.(clip, "good")}
            className={[
              "rounded-full border px-3 py-1.5 text-xs font-medium transition",
              feedbackVote === "good"
                ? "border-cyan-300/30 bg-cyan-300/12 text-cyan-100"
                : "border-white/12 bg-white/[0.05] text-ink/76 hover:border-cyan-300/30 hover:bg-cyan-300/10 hover:text-cyan-100",
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
