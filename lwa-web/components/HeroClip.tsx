"use client";

import { useState } from "react";
import { ClipResult } from "../lib/types";
import { LiveClipPreview } from "./results/LiveClipPreview";
import { RetryPreviewButton } from "./results/RetryPreviewButton";
import { hasPreviewAsset } from "../lib/clip-utils";
import { buildLeadReason } from "../lib/result-copy";
import { ClipViewer } from "./ClipViewer";

type HeroClipProps = {
  clip: ClipResult;
  compact?: boolean;
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

type ClipBadge = {
  label: string;
  tone: "accent" | "neutral";
};

function authorityLabel(rank?: number | null) {
  if (rank === 1) return "Post first";
  if (rank === 2) return "Post next";
  if (rank === 3) return "Post third";
  return "Post later";
}

function buildPackageText(clip: ClipResult) {
  const thumbnailText = clip.thumbnail_text?.trim() || clip.hook?.slice(0, 42) || clip.title;
  return [
    `Title: ${clip.title}`,
    `Hook: ${clip.hook}`,
    `Why this matters: ${clip.why_this_matters || clip.reason || "Not available"}`,
    `Thumbnail text: ${thumbnailText}`,
    `CTA: ${clip.cta_suggestion || "Ask viewers what they want next."}`,
    `Post order: ${authorityLabel(clip.post_rank || clip.best_post_order || clip.rank || null)}`,
    `Other hooks: ${(clip.hook_variants || []).filter((variant) => variant && variant !== clip.hook).join(" | ") || "None"}`,
  ].join("\n");
}

function clipHasShotPlan(clip: ClipResult) {
  return Boolean(clip.shot_plan?.length);
}

function clipHasRecoverableRender(clip: ClipResult, hasRenderProof: boolean) {
  return !hasRenderProof && (clip.visual_engine_status === "recoverable" || clip.visual_engine_status === "render_failed");
}

function buildBadges(clip: ClipResult, hasRenderProof: boolean): ClipBadge[] {
  const badges: ClipBadge[] = [];
  if ((clip.post_rank || clip.best_post_order || clip.rank) === 1) {
    badges.push({ label: "Best clip first", tone: "accent" });
  }
  if (hasRenderProof) {
    badges.push({ label: clip.visual_engine_status === "ready_now" ? "Visual render ready" : "Rendered by LWA", tone: "accent" });
  } else if (clipHasRecoverableRender(clip, hasRenderProof)) {
    badges.push({ label: "Recover render", tone: "neutral" });
  } else {
    badges.push({ label: "Strategy only", tone: "neutral" });
  }
  if (clipHasShotPlan(clip)) {
    badges.push({ label: "Shot plan ready", tone: "neutral" });
  }
  return badges.slice(0, 3);
}

function badgeClass(tone: ClipBadge["tone"]) {
  if (tone === "accent") {
    return "rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1.5 text-xs font-semibold text-[var(--gold)]";
  }
  return "rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1.5 text-xs text-ink/78";
}

function scoreClass(score: number) {
  return score >= 80
    ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]"
    : "border-[var(--divider)] bg-[var(--surface-soft)] text-ink/82";
}

export default function HeroClip({
  clip,
  compact = false,
  queued = false,
  feedbackVote = null,
  onToggleQueue,
  onVote,
  recoveryState = null,
  onRecover,
}: HeroClipProps) {
  const [copiedPackage, setCopiedPackage] = useState(false);
  const [copiedHook, setCopiedHook] = useState(false);
  const [viewerOpen, setViewerOpen] = useState(false);

  const hasRenderProof = hasPreviewAsset(clip);
  const postRank = clip.post_rank || clip.best_post_order || clip.rank || null;
  const scoreValue = Math.round(clip.virality_score ?? clip.score ?? 0);
  const badges = buildBadges(clip, hasRenderProof);
  const hookVariants = (clip.hook_variants || []).filter((variant) => variant && variant !== clip.hook).slice(0, 3);
  const showRetryPreview = Boolean(onRecover) && !hasRenderProof;
  const showQueue = !compact && Boolean(onToggleQueue);
  const showFeedback = !compact && Boolean(onVote);
  const downloadUrl = clip.download_url || null;
  const displayThumbnail = clip.thumbnail_text?.trim() || clip.title;
  const whyThisMatters = buildLeadReason(clip.why_this_matters || clip.reason);
  const showRecoverRender = clipHasRecoverableRender(clip, hasRenderProof);

  async function handleCopyHook(text: string) {
    try {
      await navigator.clipboard.writeText(text);
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
      <section id="lead-clip" className="clip-card top-pick rounded-[40px] border p-6 shadow-card sm:p-7 lg:p-8">
        <div className="-mx-6 -mt-6 mb-6 bg-[var(--gold)] px-6 py-2 text-[10px] font-bold tracking-[0.14em] text-black sm:-mx-7 sm:-mt-7 lg:-mx-8 lg:-mt-8">
          LEAD CLIP
        </div>

        <div className="grid gap-6 xl:grid-cols-[minmax(0,0.58fr),minmax(320px,0.42fr)]">
          <div className="space-y-4">
            <div className="relative overflow-hidden rounded-[30px] border border-[var(--divider)] bg-[var(--surface-veil-strong)] shadow-[var(--shadow-preview)]">
              <button
                type="button"
                onClick={() => setViewerOpen(true)}
                className="absolute right-3 top-3 z-10 flex h-8 w-8 items-center justify-center rounded-full border border-white/15 bg-black/50 text-white/70 backdrop-blur-sm transition hover:border-[var(--gold-border)] hover:bg-[var(--gold-dim)] hover:text-[var(--gold)]"
                aria-label="Expand clip"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 16 16">
                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M2 10v4h4M14 6V2h-4M10 6l4-4M6 10l-4 4" />
                </svg>
              </button>

              {hasRenderProof ? (
                <LiveClipPreview clip={clip} className="aspect-[9/16]" autoPlay />
              ) : (
                <div className="flex aspect-[9/16] min-h-[360px] flex-col justify-between bg-[radial-gradient(circle_at_top,var(--surface-gold-glow),transparent_26%),linear-gradient(180deg,var(--bg-card)_0%,var(--bg)_100%)] p-6">
                  <div className="flex items-center justify-between gap-3">
                    <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1.5 text-xs font-medium text-ink/78">
                      Strategy only
                    </span>
                    <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1.5 text-xs text-ink/62">
                      {authorityLabel(postRank)}
                    </span>
                  </div>
                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-[var(--gold)]">Post next</p>
                    <h3 className="mt-4 text-2xl font-semibold leading-8 text-ink">{clip.hook || clip.title}</h3>
                    <p className="mt-3 text-sm leading-7 text-ink/62">
                      {clip.strategy_only_reason || "Shot plan ready. Use this as a strategy lane clip until media is available."}
                    </p>
                  </div>
                </div>
              )}
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              {downloadUrl ? (
                <a href={downloadUrl} download className="primary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-semibold sm:w-auto">
                  Export lead clip
                </a>
              ) : null}

              <button
                type="button"
                onClick={() => void handleCopyHook(clip.hook || clip.title || "")}
                className="secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium sm:w-auto"
              >
                {copiedHook ? "Hook copied" : "Copy hook"}
              </button>

              <button
                type="button"
                onClick={() => void handleCopyPackage()}
                className="secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium sm:w-auto"
              >
                {copiedPackage ? "Package copied" : "Copy package"}
              </button>

              {showQueue ? (
                <button
                  type="button"
                  onClick={() => onToggleQueue?.(clip)}
                  className={[
                    "secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium sm:w-auto",
                    queued ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]" : "",
                  ].join(" ")}
                >
                  {queued ? "Queued for post" : "Queue post"}
                </button>
              ) : null}

              {showRetryPreview ? (
                <RetryPreviewButton
                  onRetry={() => onRecover?.(clip)}
                  disabled={recoveryState?.status === "queued" || recoveryState?.status === "processing"}
                  className="w-full px-5 py-3 sm:w-auto"
                  label={
                    recoveryState?.status === "processing"
                      ? "Recovering..."
                      : recoveryState?.status === "queued"
                        ? "Recovery queued"
                        : "Recover render"
                  }
                />
              ) : null}
            </div>
          </div>

          <div className="space-y-5">
            <div className="space-y-3">
              <p className="section-kicker">Best clip first</p>
              <div className="flex flex-wrap items-center gap-2">
                <span className={["rounded-full border px-3 py-1.5 text-sm font-semibold", scoreClass(scoreValue)].join(" ")}>{scoreValue}</span>
                {badges.map((badge) => (
                  <span key={badge.label} className={badgeClass(badge.tone)}>
                    {badge.label}
                  </span>
                ))}
              </div>
              {!compact ? <h2 className="text-2xl font-semibold leading-tight text-ink sm:text-[2.15rem]">{clip.title}</h2> : null}
              <p className="text-lg leading-8 text-ink/90">{clip.hook || clip.title}</p>
              <p className="text-sm leading-7 text-ink/66">{whyThisMatters}</p>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="metric-tile rounded-[22px] p-4">
                <p className="text-[10px] uppercase tracking-[0.22em] text-muted">What to post next</p>
                <p className="mt-2 text-sm font-medium text-ink">{authorityLabel(postRank)}</p>
              </div>
              <div className="metric-tile rounded-[22px] p-4">
                <p className="text-[10px] uppercase tracking-[0.22em] text-muted">Thumbnail text</p>
                <p className="mt-2 text-sm font-medium text-ink">{displayThumbnail}</p>
              </div>
              <div className="metric-tile rounded-[22px] p-4">
                <p className="text-[10px] uppercase tracking-[0.22em] text-muted">CTA</p>
                <p className="mt-2 text-sm font-medium text-ink">{clip.cta_suggestion || "Ask viewers what they want next."}</p>
              </div>
              <div className="metric-tile rounded-[22px] p-4">
                <p className="text-[10px] uppercase tracking-[0.22em] text-muted">Why it matters</p>
                <p className="mt-2 text-sm font-medium text-ink">{clip.why_this_matters || clip.reason || "This is the strongest lead for the current stack."}</p>
              </div>
            </div>

            {hookVariants.length ? (
              <details className="rounded-[22px] border border-[var(--divider)] bg-[var(--surface-veil)] p-4">
                <summary className="cursor-pointer list-none text-xs uppercase tracking-[0.22em] text-muted transition-colors hover:text-[var(--ink-mid)]">
                  Other hooks
                </summary>
                <div className="mt-4 grid gap-3">
                  {hookVariants.map((variant) => (
                    <div key={variant} className="flex flex-col gap-3 rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-3 sm:flex-row sm:items-center sm:justify-between">
                      <p className="text-sm leading-6 text-ink/82">{variant}</p>
                      <button
                        type="button"
                        onClick={() => void handleCopyHook(variant)}
                        className="secondary-button inline-flex items-center justify-center rounded-full px-3 py-2 text-xs font-medium"
                      >
                        Copy
                      </button>
                    </div>
                  ))}
                </div>
              </details>
            ) : null}

            {clipHasShotPlan(clip) ? (
              <details className="rounded-[22px] border border-[var(--divider)] bg-[var(--surface-veil)] p-4">
                <summary className="cursor-pointer list-none text-xs uppercase tracking-[0.22em] text-muted transition-colors hover:text-[var(--ink-mid)]">
                  Shot plan ready
                </summary>
                <div className="mt-4 grid gap-3">
                  {clip.shot_plan?.map((step) => (
                    <div key={`${clip.id}-${step.role}`} className="rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--gold)]">
                          {step.role}
                        </span>
                        {step.duration_seconds ? <span className="text-[11px] text-ink/58">{step.duration_seconds}s</span> : null}
                      </div>
                      <p className="mt-2 text-xs leading-6 text-ink/76">
                        {step.visual_direction || step.text_overlay || step.retention_goal || "Director note pending."}
                      </p>
                    </div>
                  ))}
                  {showRecoverRender && clip.recovery_recommendation ? (
                    <p className="text-xs leading-6 text-ink/58">{clip.recovery_recommendation}</p>
                  ) : null}
                </div>
              </details>
            ) : null}

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
        </div>
      </section>
    </>
  );
}
