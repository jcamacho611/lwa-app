"use client";

import { useState } from "react";
import { ClipResult } from "../lib/types";
import { LiveClipPreview } from "./results/LiveClipPreview";
import { RetryPreviewButton } from "./results/RetryPreviewButton";
import { hasPreviewAsset, isRenderedClip } from "../lib/clip-utils";
import { RESULT_COPY, buildLeadReason } from "../lib/result-copy";

type HeroClipProps = {
  clip: ClipResult;
  queued?: boolean;
  feedbackVote?: "good" | "bad" | null;
  onToggleQueue?: (clip: ClipResult) => void;
  onVote?: (clip: ClipResult, vote: "good" | "bad") => void;
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

function decisionInstruction(rank?: number | null, hasRenderProof?: boolean) {
  if (rank === 1 && hasRenderProof) {
    return "Post this first — clearest interruption and strongest opening momentum.";
  }
  if (rank === 2) {
    return "Post this next — it keeps the story moving after the opener lands.";
  }
  if (rank === 3) {
    return "Continuation clip — useful once the first two establish the frame.";
  }
  return hasRenderProof
    ? "Post this next when you want another cut that is already ready to move."
    : "High viral potential — keep this in your posting plan while the preview finishes.";
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
    `Caption style: ${clip.caption_style || "Short-form native"}`,
    `Hook variants: ${(clip.hook_variants || []).join(" | ") || "Not available"}`,
  ].join("\n");
}

export default function HeroClip({
  clip,
  queued = false,
  feedbackVote = null,
  onToggleQueue,
  onVote,
  recoveryState = null,
  onRecover,
}: HeroClipProps) {
  const [copiedPackage, setCopiedPackage] = useState(false);

  const downloadUrl = clip.download_url || null;
  const hasPlayablePreview = isRenderedClip(clip);
  const hasRenderProof = hasPreviewAsset(clip);
  const postRank = clip.post_rank || clip.best_post_order || clip.rank || null;
  const postAuthority = authorityLabel(postRank);
  const decisionText = decisionInstruction(postRank, hasRenderProof);
  const whyThisHits = buildLeadReason(clip.why_this_matters || clip.reason);
  const hookVariants = (clip.hook_variants || []).filter((variant) => variant && variant !== clip.hook).slice(0, 2);

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
    <section id="lead-clip" className="lead-clip-card clip-card top-pick group relative overflow-hidden rounded-[42px] border p-6 shadow-[0_28px_100px_rgba(0,0,0,0.44)] transition-all duration-300 hover:scale-[1.01] sm:p-7 lg:p-8">
      <div className="-mx-6 -mt-6 mb-6 bg-[var(--gold)] px-6 py-2 text-[10px] font-bold tracking-[0.14em] text-black sm:-mx-7 sm:-mt-7 lg:-mx-8 lg:-mt-8">
        #1 PICK — POST FIRST
      </div>
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(201,162,39,0.12),transparent_36%),radial-gradient(circle_at_80%_20%,rgba(201,162,39,0.08),transparent_32%)]" />

      <div className="relative grid gap-6 xl:grid-cols-[minmax(0,0.62fr),minmax(340px,0.38fr)] xl:items-start">
        <div className="space-y-4">
          <div className="video-shell overflow-hidden rounded-[30px] border border-white/10 bg-black/55 shadow-[0_12px_44px_rgba(0,0,0,0.28)]">
            <LiveClipPreview clip={clip} className="aspect-[9/16] transition-transform duration-300 group-hover:scale-[1.02]" autoPlay />

            <div className="video-overlay pointer-events-none absolute inset-x-0 bottom-0 flex flex-wrap items-end justify-between gap-3 p-4">
              <div className="flex flex-wrap gap-2">
                <span className="status-chip status-approved">{hasRenderProof ? "POST THIS FIRST" : "HIGH VIRAL POTENTIAL"}</span>
                {clip.confidence_label ? <span className="status-chip status-submitted">{clip.confidence_label}</span> : null}
                {clip.caption_style ? <span className="status-chip status-submitted">{clip.caption_style}</span> : null}
              </div>
              <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-4 py-2 text-xs font-semibold tracking-[0.18em] text-[var(--gold)]">
                {postAuthority}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            {downloadUrl ? (
              <a
                href={downloadUrl}
                download
                className="primary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold"
              >
                Export lead clip
              </a>
            ) : (
                <span className="rounded-full border border-accentCrimson/22 bg-[linear-gradient(135deg,rgba(122,16,42,0.24),rgba(124,58,237,0.1))] px-4 py-2.5 text-sm text-[#ffe4eb]">
                Bundle export below
              </span>
            )}

            <button
              type="button"
              onClick={() => void handleCopyPackage()}
              className="secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium"
            >
              {copiedPackage ? "Package copied" : "Copy package"}
            </button>

            <button
              type="button"
              onClick={() => onToggleQueue?.(clip)}
              className={[
                "secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium",
                queued ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]" : "",
              ].join(" ")}
            >
              {queued ? "Queued for post" : "Queue post"}
            </button>

            {!hasRenderProof ? (
              <RetryPreviewButton
                onRetry={() => onRecover?.(clip)}
                disabled={recoveryState?.status === "queued" || recoveryState?.status === "processing"}
                className="px-5 py-3"
                label={recoveryState?.status === "processing"
                  ? "Recovering..."
                  : recoveryState?.status === "queued"
                    ? "Recovery queued"
                    : recoveryState?.status === "failed"
                      ? RESULT_COPY.previewRetry
                      : RESULT_COPY.previewRetry}
              />
            ) : null}
          </div>
        </div>

        <div className="space-y-5">
          <div className="space-y-3">
            <p className="section-kicker">Lead drop</p>
            <h2 className="text-2xl font-semibold leading-tight text-ink sm:text-[2.1rem]">{clip.title}</h2>
            <p className="text-lg leading-8 text-ink/88">{clip.hook}</p>
          </div>

          <div className="rounded-[26px] border border-[var(--gold-border)] bg-[var(--gold-dim)] p-5">
            <p className="mb-2 text-xs uppercase tracking-[0.24em] text-[var(--gold)]">{RESULT_COPY.whyPicked}</p>
            <p className="text-base font-medium leading-7 text-white">{decisionText}</p>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <div className="metric-tile rounded-[24px] p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Move</p>
              <p className="text-sm font-medium text-ink">{postAuthority}</p>
            </div>
            <div className="metric-tile rounded-[24px] p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">High viral potential</p>
              <p className="text-sm font-medium text-ink">{clip.confidence_label || clip.packaging_angle || clip.platform_fit || "Built to travel fast"}</p>
            </div>
            <div className="metric-tile rounded-[24px] p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Thumbnail line</p>
              <p className="text-sm font-medium text-ink">{clip.thumbnail_text || "Best Clip"}</p>
            </div>
            <div className="metric-tile rounded-[24px] p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">CTA</p>
              <p className="text-sm font-medium text-ink">{clip.cta_suggestion || "Ask viewers to comment or follow for the next cut."}</p>
            </div>
          </div>

          <details className="rounded-[24px] border border-white/10 bg-black/20 p-4">
            <summary className="cursor-pointer list-none text-xs uppercase tracking-[0.24em] text-muted transition-colors duration-300 hover:text-ink/76">
              Open package notes
            </summary>
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/80">{postAuthority}</span>
              {clip.platform_fit ? (
                <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/80">{clip.platform_fit}</span>
              ) : null}
              {clip.start_time && clip.end_time ? (
                <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/80">
                  {clip.start_time} - {clip.end_time}
                </span>
              ) : null}
            </div>
            {hookVariants.length ? (
              <div className="mt-4 flex flex-wrap gap-2">
                {hookVariants.map((variant) => (
                  <span key={variant} className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-2 text-xs text-ink/78">
                    {variant}
                  </span>
                ))}
              </div>
            ) : null}
            <p className="mt-4 text-sm leading-6 text-ink/76">{whyThisHits}</p>
          </details>

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
        </div>
      </div>
    </section>
  );
}
