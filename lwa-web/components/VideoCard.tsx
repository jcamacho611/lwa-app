"use client";

import { useState } from "react";
import { ClipResult } from "../lib/types";
import { LiveClipPreview } from "./results/LiveClipPreview";
import { RetryPreviewButton } from "./results/RetryPreviewButton";
import { hasPreviewAsset, isRenderedClip } from "../lib/clip-utils";
import { RESULT_COPY, buildLeadReason } from "../lib/result-copy";
import { ClipViewer } from "./ClipViewer";

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

function clipHasShotPlan(clip: ClipResult) {
  return Boolean(clip.shot_plan?.length);
}

function clipHasRecoverableRender(clip: ClipResult, hasRenderProof: boolean) {
  return !hasRenderProof && (clip.visual_engine_status === "recoverable" || clip.visual_engine_status === "render_failed");
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
  const [copiedHook, setCopiedHook] = useState(false);
  const [viewerOpen, setViewerOpen] = useState(false);

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
  const showScore = !compact && scoreValue >= 50;
  const showFeedback = !compact && Boolean(onVote);
  const showRetryPreview = Boolean(onRecover) && !hasRenderProof;
  const showQueue = !compact && Boolean(onToggleQueue);
  const displayThumbnail = clip.thumbnail_text && clip.thumbnail_text !== "Best Clip"
    ? clip.thumbnail_text
    : clip.hook?.slice(0, 40) || clip.title;
  const hasShotPlan = clipHasShotPlan(clip);
  const showRenderedByLWA = hasRenderProof && clip.rendered_by === "LWA Omega Visual Engine";
  const showVisualRenderReady = clip.visual_engine_status === "ready_now";
  const showRecoverRender = clipHasRecoverableRender(clip, hasRenderProof);

  async function handleCopyHook() {
    try {
      await navigator.clipboard.writeText(clip.hook || clip.title || "");
      setCopiedHook(true);
      window.setTimeout(() => setCopiedHook(false), 1600);
    } catch {
      setCopiedHook(false);
    }
  }

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
    <>
      <ClipViewer clip={clip} isOpen={viewerOpen} onClose={() => setViewerOpen(false)} />
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
      <div className="video-shell relative overflow-hidden rounded-[22px] border border-[var(--divider)] bg-[var(--surface-veil-strong)]">
        {/* Omega expand button */}
        <button
          type="button"
          onClick={() => setViewerOpen(true)}
          className="absolute right-2.5 top-2.5 z-10 flex h-7 w-7 items-center justify-center rounded-full border border-white/15 bg-black/50 text-white/70 backdrop-blur-sm transition hover:border-[var(--gold-border)] hover:bg-[var(--gold-dim)] hover:text-[var(--gold)]"
          aria-label="Expand clip"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 16 16">
            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M2 10v4h4M14 6V2h-4M10 6l4-4M6 10l-4 4" />
          </svg>
        </button>

        {compact && !hasRenderProof ? (
          <div className="flex aspect-[9/16] min-h-[260px] flex-col items-start justify-end bg-[radial-gradient(circle_at_top,var(--surface-gold-glow),transparent_26%),linear-gradient(180deg,var(--bg-card)_0%,var(--bg)_100%)] px-5 pb-6">
            <div className="flex flex-wrap gap-2">
              <span className="inline-block rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1 text-xs font-bold tracking-widest text-[var(--gold)]">
                {authority}
              </span>
              {scoreValue >= 70 ? <span className="score-badge">{scoreValue}/10</span> : null}
              <span className="rounded-full border border-[var(--gold-border)] bg-[var(--surface-veil)] px-3 py-1 text-xs font-medium text-[var(--ink-mid)]">
                {clip.platform_fit || "Short-form"}
              </span>
            </div>
            <p className="mt-4 text-lg font-semibold leading-7 text-[var(--gold)]">{clip.hook || clip.title}</p>
            <p className="mt-2 line-clamp-2 text-sm leading-6 text-[var(--ink-mid)]">{clip.caption}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {postRank === 1 ? (
                <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1 text-[11px] font-semibold text-[var(--gold)]">
                  Best clip first
                </span>
              ) : null}
              {Boolean(clip.is_strategy_only) ? (
                <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1 text-[11px] text-ink/82">
                  Strategy only
                </span>
              ) : null}
              {hasShotPlan ? (
                <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1 text-[11px] text-ink/82">
                  Shot plan ready
                </span>
              ) : null}
            </div>
            <p className="mt-2 text-xs text-[var(--ink-faint)]">{clip.timestamp_start || clip.start_time} — {clip.timestamp_end || clip.end_time}</p>
          </div>
        ) : (
          <LiveClipPreview clip={clip} className="aspect-[9/16] transition duration-300 group-hover:scale-[1.02]" />
        )}

        {!compact ? (
          <div className="video-overlay pointer-events-none absolute inset-x-0 bottom-0 p-3">
          <div className="flex items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              <span
                className={[
                  "rounded-full px-3 py-1.5 text-[11px] font-semibold tracking-[0.16em]",
                  hasRenderProof ? "bg-[var(--gold-dim)] text-[var(--gold)]" : "bg-white/[0.07] text-white/55",
                ].join(" ")}
              >
                {hasRenderProof ? RESULT_COPY.renderedReady : RESULT_COPY.strategyOnly}
              </span>
              {showRenderedByLWA ? (
                <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1.5 text-[11px] font-semibold tracking-[0.16em] text-[var(--gold)]">
                  Rendered by LWA
                </span>
              ) : null}
              {showVisualRenderReady ? (
                <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1.5 text-[11px] font-semibold tracking-[0.16em] text-[var(--gold)]">
                  Visual render ready
                </span>
              ) : null}
            </div>
            <span className="rounded-full border border-white/10 bg-black/35 px-3 py-1.5 text-[11px] font-medium text-white/82 backdrop-blur">
              {hasPlayablePreview ? "Preview ready" : hasRenderProof ? RESULT_COPY.recoverRender : RESULT_COPY.strategyOnlyShort}
            </span>
          </div>
        </div>
        ) : null}
      </div>

      <div className="mt-4 space-y-3">
        <div className="flex flex-wrap gap-2">
          {showScore ? <span className="score-badge">{scoreValue}/10</span> : null}
              <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1.5 text-xs text-ink/82">{authority}</span>
              {!compact ? (
                <>
                  <span
                    className={[
                      "rounded-full border px-3 py-1.5 text-xs",
                      hasRenderProof
                        ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]"
                        : "border-[var(--divider)] bg-[var(--surface-soft)] text-ink/55",
                    ].join(" ")}
                  >
                    {hasRenderProof ? "Ready now" : RESULT_COPY.strategyOnlyShort}
                  </span>
                  {postRank === 1 ? (
                    <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1.5 text-xs text-[var(--gold)]">
                      Best clip first
                    </span>
                  ) : null}
                  {showRenderedByLWA ? (
                    <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1.5 text-xs text-[var(--gold)]">
                      Rendered by LWA
                    </span>
                  ) : null}
                  {showVisualRenderReady ? (
                    <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1.5 text-xs text-[var(--gold)]">
                      Visual render ready
                    </span>
                  ) : null}
                  {Boolean(clip.is_strategy_only) ? (
                    <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1.5 text-xs text-ink/76">
                      Strategy only
                    </span>
                  ) : null}
                  {hasShotPlan ? (
                    <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1.5 text-xs text-ink/76">
                      Shot plan ready
                    </span>
                  ) : null}
                  {showRecoverRender ? (
                    <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1.5 text-xs text-ink/76">
                      Recover render
                    </span>
                  ) : null}
                  {clip.confidence_label ? (
                    <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1.5 text-xs text-[var(--gold)]">
                      {clip.confidence_label}
                    </span>
                  ) : null}
                  {captionStyle ? (
                    <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1.5 text-xs text-ink/76">{captionStyle}</span>
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
            <div className="rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[0.22em] text-muted">Thumbnail</p>
              <p className="mt-1 text-xs font-medium text-ink/82">{displayThumbnail}</p>
            </div>
          ) : null}
          {clip.cta_suggestion ? (
            <div className="rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[0.22em] text-muted">CTA</p>
              <p className="mt-1 text-xs font-medium text-ink/82">{clip.cta_suggestion}</p>
            </div>
          ) : null}
        </div>

        {!compact && whyThisHits ? (
          <details className="rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
            <summary className="cursor-pointer list-none text-[10px] uppercase tracking-[0.22em] text-muted transition-colors duration-300 hover:text-[var(--ink-mid)]">
              {RESULT_COPY.packageNotes}
            </summary>
            <p className="mt-2 text-xs leading-6 text-ink/62">{whyThisHits}</p>
          </details>
        ) : null}

        {!compact && hasShotPlan ? (
          <details className="rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
            <summary className="cursor-pointer list-none text-[10px] uppercase tracking-[0.22em] text-muted transition-colors duration-300 hover:text-[var(--ink-mid)]">
              Shot plan ready
            </summary>
            <div className="mt-3 grid gap-2">
              {clip.shot_plan?.map((step) => (
                <div key={`${clip.id}-${step.role}`} className="rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] px-3 py-2.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--gold)]">
                      {step.role}
                    </span>
                    {step.duration_seconds ? (
                      <span className="text-[11px] text-ink/58">{step.duration_seconds}s</span>
                    ) : null}
                  </div>
                  <p className="mt-2 text-xs leading-6 text-ink/76">{step.visual_direction || step.retention_goal || "Director note pending."}</p>
                </div>
              ))}
              {clip.recovery_recommendation ? (
                <p className="text-xs leading-6 text-ink/58">{clip.recovery_recommendation}</p>
              ) : null}
            </div>
          </details>
        ) : null}

        {/* Quick-copy strip — Omega one-tap actions */}
        {!compact && clip.hook ? (
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => void handleCopyHook()}
              className="inline-flex items-center gap-1.5 rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3.5 py-1.5 text-[11px] font-semibold text-[var(--gold)] transition hover:bg-[var(--gold)] hover:text-black"
            >
              {copiedHook ? "Copied!" : "Copy hook"}
            </button>
            <button
              type="button"
              onClick={() => setViewerOpen(true)}
              className="inline-flex items-center gap-1.5 rounded-full border border-white/12 bg-white/[0.04] px-3.5 py-1.5 text-[11px] font-medium text-white/60 transition hover:border-white/20 hover:text-white/90"
            >
              Full screen
            </button>
          </div>
        ) : null}

        <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
          {showQueue ? (
            <button
              type="button"
              onClick={() => onToggleQueue?.(clip)}
              className={[
                "secondary-button inline-flex w-full items-center justify-center rounded-full px-4 py-2 text-sm font-medium sm:w-auto",
                queued ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]" : "",
              ].join(" ")}
            >
              {queued ? RESULT_COPY.queued : RESULT_COPY.queuePost}
            </button>
          ) : null}

          {!compact && downloadUrl ? (
            <a
              href={downloadUrl}
              download
              className="primary-button inline-flex w-full items-center justify-center rounded-full px-4 py-2 text-sm font-semibold sm:w-auto"
            >
              Download
            </a>
          ) : !compact && hasPlayablePreview ? (
            <a
              href={previewUrl || undefined}
              target="_blank"
              rel="noreferrer"
              className="secondary-button inline-flex w-full items-center justify-center rounded-full px-4 py-2 text-sm font-medium sm:w-auto"
            >
              Open preview
            </a>
          ) : null}

          {showRetryPreview ? (
            <RetryPreviewButton
              onRetry={() => onRecover?.(clip)}
              disabled={recoveryState?.status === "queued" || recoveryState?.status === "processing"}
              className="w-full sm:w-auto"
              label={recoveryState?.status === "processing"
                ? "Recovering..."
                : recoveryState?.status === "queued"
                  ? "Recovery queued"
                  : "Recover render"}
            />
          ) : null}

          <button
            type="button"
            onClick={() => void handleCopyPackage()}
            className="secondary-button inline-flex w-full items-center justify-center rounded-full px-4 py-2 text-sm font-medium sm:w-auto"
          >
            {copiedPackage ? RESULT_COPY.packageCopied : RESULT_COPY.copyPackage}
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
    </>
  );
}
