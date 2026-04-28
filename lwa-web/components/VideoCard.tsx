"use client";

import { useState } from "react";
import { ClipResult } from "../lib/types";
import { LiveClipPreview } from "./results/LiveClipPreview";
import { RetryPreviewButton } from "./results/RetryPreviewButton";
import { hasPreviewAsset } from "../lib/clip-utils";
import { buildLeadReason } from "../lib/result-copy";
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

type ClipBadge = {
  label: string;
  tone: "accent" | "neutral";
};

type ClipMetaLabel = {
  label: string;
  tone: "neutral" | "warning" | "danger";
};

function authorityLabel(rank?: number | null) {
  if (rank === 1) return "Post first";
  if (rank === 2) return "Post next";
  if (rank === 3) return "Post third";
  return "Post later";
}

function clipHasShotPlan(clip: ClipResult) {
  return Boolean(clip.shot_plan?.length);
}

function clipHasRecoverableRender(clip: ClipResult, hasRenderProof: boolean) {
  return !hasRenderProof && (clip.visual_engine_status === "recoverable" || clip.visual_engine_status === "render_failed");
}

function clipHasCaptionArtifacts(clip: ClipResult) {
  return Boolean(
    clip.caption_srt_url ||
      clip.caption_vtt_url ||
      clip.export_bundle?.artifact_types?.includes("subtitle_srt") ||
      clip.export_bundle?.artifact_types?.includes("subtitle_vtt"),
  );
}

function clipHasBundleArtifacts(clip: ClipResult) {
  return Boolean(clip.export_bundle?.manifest_ready || clip.export_bundle?.artifact_types?.length);
}

function clipCampaignStatusLabel(clip: ClipResult): ClipMetaLabel | null {
  const checks = clip.campaign_requirement_checks || [];
  const failCount = checks.filter((check) => check.status === "fail").length;
  const warningCount = checks.filter((check) => check.status === "warning").length;

  if (failCount > 0) {
    return { label: "Campaign issue", tone: "danger" };
  }

  if (warningCount > 0) {
    return { label: "Campaign warning", tone: "warning" };
  }

  return null;
}

function clipApprovalStateLabel(clip: ClipResult): ClipMetaLabel | null {
  const approvalState = clip.approval_state?.trim().toLowerCase();

  if (!approvalState) {
    return null;
  }

  if (approvalState === "approved") {
    return { label: "Approved", tone: "neutral" };
  }

  if (approvalState === "needs_edit" || approvalState === "needs edit" || approvalState === "needs_regen") {
    return { label: "Needs edit", tone: "warning" };
  }

  if (approvalState === "new") {
    return { label: "New", tone: "neutral" };
  }

  return { label: clip.approval_state || "New", tone: "neutral" };
}

function buildBadges(clip: ClipResult, hasRenderProof: boolean): ClipBadge[] {
  const badges: ClipBadge[] = [];
  if ((clip.post_rank || clip.best_post_order || clip.rank) === 1) {
    badges.push({ label: "Best clip first", tone: "accent" });
  }
  if (hasRenderProof) {
    badges.push({ label: clip.visual_engine_status === "ready_now" ? "Visual render ready" : "Rendered", tone: "accent" });
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
    return "rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1 text-[11px] font-semibold text-[var(--gold)]";
  }
  return "rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1 text-[11px] text-ink/78";
}

function metaLabelClass(tone: ClipMetaLabel["tone"]) {
  if (tone === "danger") {
    return "rounded-full border border-red-400/30 bg-red-400/10 px-2.5 py-1 text-[10px] font-medium text-red-100";
  }

  if (tone === "warning") {
    return "rounded-full border border-amber-300/30 bg-amber-300/10 px-2.5 py-1 text-[10px] font-medium text-amber-100";
  }

  return "rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-2.5 py-1 text-[10px] font-medium text-ink/68";
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
  const [copiedHook, setCopiedHook] = useState(false);
  const [viewerOpen, setViewerOpen] = useState(false);

  const hasRenderProof = hasPreviewAsset(clip);
  const previewUrl = clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url || null;
  const downloadUrl = clip.download_url || null;
  const postRank = clip.post_rank || clip.best_post_order || clip.rank || null;
  const scoreValue = Math.round(clip.virality_score ?? clip.score ?? 0);
  const badges = buildBadges(clip, hasRenderProof);
  const hookVariants = (clip.hook_variants || []).filter((variant) => variant && variant !== clip.hook).slice(0, 3);
  const campaignLabel = clipCampaignStatusLabel(clip);
  const approvalLabel = clipApprovalStateLabel(clip);
  const whyThisMatters = buildLeadReason(clip.why_this_matters || clip.reason);
  const displayThumbnail = clip.thumbnail_text?.trim() || clip.title;
  const showRetryPreview = Boolean(onRecover) && !hasRenderProof;
  const showQueue = !compact && Boolean(onToggleQueue);
  const showFeedback = !compact && Boolean(onVote);
  const showRecoverRender = clipHasRecoverableRender(clip, hasRenderProof);
  const metaLabels: ClipMetaLabel[] = [
    ...(clipHasBundleArtifacts(clip) ? [{ label: "Bundle ready", tone: "neutral" as const }] : []),
    ...(clipHasCaptionArtifacts(clip) ? [{ label: "Captions ready", tone: "neutral" as const }] : []),
    ...(campaignLabel ? [campaignLabel] : []),
    ...(approvalLabel ? [approvalLabel] : []),
  ];

  async function handleCopyHook(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedHook(true);
      window.setTimeout(() => setCopiedHook(false), 1600);
    } catch {
      setCopiedHook(false);
    }
  }

  return (
    <>
      <ClipViewer clip={clip} isOpen={viewerOpen} onClose={() => setViewerOpen(false)} />
      <article className="clip-card rounded-[28px] border p-4 shadow-card transition-all duration-300 hover:scale-[1.01]">
        <div className="relative overflow-hidden rounded-[22px] border border-[var(--divider)] bg-[var(--surface-veil-strong)]">
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

          {hasRenderProof ? (
            <LiveClipPreview clip={clip} className="aspect-[9/16]" />
          ) : (
            <div className="flex aspect-[9/16] min-h-[260px] flex-col justify-between bg-[radial-gradient(circle_at_top,var(--surface-gold-glow),transparent_24%),linear-gradient(180deg,var(--bg-card)_0%,var(--bg)_100%)] p-5">
              <div className="flex items-center justify-between gap-3">
                <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1 text-[11px] font-medium text-ink/78">
                  Strategy only
                </span>
                <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1 text-[11px] text-ink/62">
                  {authorityLabel(postRank)}
                </span>
              </div>
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--gold)]">Next idea</p>
                <h3 className="mt-4 text-lg font-semibold leading-7 text-ink">{clip.hook || clip.title}</h3>
                <p className="mt-3 text-sm leading-6 text-ink/62">
                  {clip.strategy_only_reason || "Shot plan ready. Use this as a strategy lane clip until media is available."}
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="mt-4 space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1 text-xs font-semibold text-ink/82">
              {scoreValue}
            </span>
            {badges.map((badge) => (
              <span key={badge.label} className={badgeClass(badge.tone)}>
                {badge.label}
              </span>
            ))}
          </div>
          {metaLabels.length ? (
            <div className="flex flex-wrap items-center gap-2">
              {metaLabels.map((label) => (
                <span key={label.label} className={metaLabelClass(label.tone)}>
                  {label.label}
                </span>
              ))}
            </div>
          ) : null}

          {!compact ? <h3 className="line-clamp-2 text-lg font-semibold leading-tight text-ink">{clip.title}</h3> : null}
          <p className={compact ? "text-base font-semibold leading-7 text-ink" : "text-sm leading-6 text-ink/88"}>
            {clip.hook || clip.title}
          </p>
          <p className="text-sm leading-6 text-ink/62">{whyThisMatters}</p>

          <div className="grid gap-2">
            <div className="rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[0.22em] text-muted">Thumbnail</p>
              <p className="mt-1 text-xs font-medium text-ink/82">{displayThumbnail}</p>
            </div>
            <div className="rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[0.22em] text-muted">CTA</p>
              <p className="mt-1 text-xs font-medium text-ink/82">{clip.cta_suggestion || "Ask viewers what they want next."}</p>
            </div>
          </div>

          {hookVariants.length ? (
            <details className="rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
              <summary className="cursor-pointer list-none text-[10px] uppercase tracking-[0.22em] text-muted transition-colors hover:text-[var(--ink-mid)]">
                Other hooks
              </summary>
              <div className="mt-3 grid gap-2">
                {hookVariants.map((variant) => (
                  <div key={variant} className="flex flex-col gap-2 rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] px-3 py-2.5 sm:flex-row sm:items-center sm:justify-between">
                    <p className="text-xs leading-6 text-ink/78">{variant}</p>
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
            <details className="rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
              <summary className="cursor-pointer list-none text-[10px] uppercase tracking-[0.22em] text-muted transition-colors hover:text-[var(--ink-mid)]">
                Shot plan
              </summary>
              <div className="mt-3 grid gap-2">
                {clip.shot_plan?.map((step) => (
                  <div key={`${clip.id}-${step.role}`} className="rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] px-3 py-2.5">
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

          <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
            {downloadUrl ? (
              <a href={downloadUrl} download className="primary-button inline-flex w-full items-center justify-center rounded-full px-4 py-2 text-sm font-semibold sm:w-auto">
                Export clip
              </a>
            ) : previewUrl ? (
              <a
                href={previewUrl}
                target="_blank"
                rel="noreferrer"
                className="secondary-button inline-flex w-full items-center justify-center rounded-full px-4 py-2 text-sm font-medium sm:w-auto"
              >
                Open preview
              </a>
            ) : null}

            <button
              type="button"
              onClick={() => void handleCopyHook(clip.hook || clip.title || "")}
              className="secondary-button inline-flex w-full items-center justify-center rounded-full px-4 py-2 text-sm font-medium sm:w-auto"
            >
              {copiedHook ? "Hook copied" : "Copy hook"}
            </button>

            {showQueue ? (
              <button
                type="button"
                onClick={() => onToggleQueue?.(clip)}
                className={[
                  "secondary-button inline-flex w-full items-center justify-center rounded-full px-4 py-2 text-sm font-medium sm:w-auto",
                  queued ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]" : "",
                ].join(" ")}
              >
                {queued ? "Queued" : "Queue"}
              </button>
            ) : null}

            {showRetryPreview ? (
              <RetryPreviewButton
                onRetry={() => onRecover?.(clip)}
                disabled={recoveryState?.status === "queued" || recoveryState?.status === "processing"}
                className="w-full sm:w-auto"
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
