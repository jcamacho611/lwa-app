"use client";

import { useState } from "react";
import { ClipResult } from "../lib/types";
import { LiveClipPreview } from "./results/LiveClipPreview";
import { RetryPreviewButton } from "./results/RetryPreviewButton";
import { buildClipPackageText, clipAuthorityLabel, getBestClipUrl, getClipScore, getPreviewUrl, isRenderedClip } from "../lib/clip-utils";
import { getRenderState, CampaignMetaPanel } from "./VideoCard";
import { saveProofAsset, submitClipStyleFeedback } from "../lib/api";
import { buildLeadReason } from "../lib/result-copy";
import { ClipIntelligencePanel } from "./clip-intelligence-panel";
import { AutoEditorBrainPanel } from "./AutoEditorBrainPanel";
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

type ClipMetaLabel = {
  label: string;
  tone: "neutral" | "warning" | "danger";
};

function clipHasShotPlan(clip: ClipResult) {
  return Boolean(clip.shot_plan?.length);
}

function clipHasRecoverableRender(clip: ClipResult, hasRenderProof: boolean) {
  return !hasRenderProof && (clip.visual_engine_status === "recoverable" || clip.visual_engine_status === "render_failed");
}

function clipHasCaptionArtifacts(clip: ClipResult) {
  return Boolean(clip.caption_txt_url || clip.caption_srt_url || clip.caption_vtt_url);
}

function clipCaptionArtifactLinks(clip: ClipResult) {
  return [
    clip.caption_txt_url ? { label: "Caption TXT", href: clip.caption_txt_url } : null,
    clip.caption_srt_url ? { label: "Subtitle SRT", href: clip.caption_srt_url } : null,
    clip.caption_vtt_url ? { label: "Subtitle VTT", href: clip.caption_vtt_url } : null,
  ].filter((item): item is { label: string; href: string } => Boolean(item?.href));
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

  if (approvalState === "needs_review" || approvalState === "needs review") {
    return { label: "Needs review", tone: "warning" };
  }

  if (approvalState === "new") {
    return { label: "New", tone: "neutral" };
  }

  return { label: clip.approval_state || "New", tone: "neutral" };
}

function clipEvergreenLabel(clip: ClipResult): ClipMetaLabel | null {
  const status = clip.evergreen_status?.trim().toLowerCase();

  if (status === "evergreen") {
    return { label: "Evergreen", tone: "neutral" };
  }

  if (status === "trend_aware" || status === "trend aware") {
    return { label: "Trend aware", tone: "neutral" };
  }

  if (status === "time_sensitive" || status === "time sensitive") {
    return { label: "Trend tied", tone: "warning" };
  }

  return null;
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

function metaLabelClass(tone: ClipMetaLabel["tone"]) {
  if (tone === "danger") {
    return "rounded-full border border-red-400/30 bg-red-400/10 px-2.5 py-1 text-[11px] font-medium text-red-100";
  }

  if (tone === "warning") {
    return "rounded-full border border-amber-300/30 bg-amber-300/10 px-2.5 py-1 text-[11px] font-medium text-amber-100";
  }

  return "rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-2.5 py-1 text-[11px] font-medium text-ink/68";
}

export function chooseLeadClip(clips: ClipResult[]): ClipResult | null {
  if (!clips.length) return null;

  // Prefer rendered clips, then fall back to any clip
  const rendered = clips.filter((c) => getRenderState(c) === "rendered");
  const candidates = rendered.length > 0 ? rendered : clips;

  // Sort by post_rank/rank, then by score
  return candidates.sort((a, b) => {
    const aRank = a.post_rank || a.rank || 999;
    const bRank = b.post_rank || b.rank || 999;
    const aScore = a.score || a.confidence_score || 0;
    const bScore = b.score || b.confidence_score || 0;
    return aRank - bRank || bScore - aScore;
  })[0];
}

export default function HeroClip({
  clip,
  clips,
  compact = false,
  queued = false,
  feedbackVote = null,
  onToggleQueue,
  onVote,
  recoveryState = null,
  onRecover,
}: HeroClipProps & { clips?: ClipResult[] }) {
  // Use lead selection if clips array provided
  const lead = clips && clips.length > 0 ? chooseLeadClip(clips) : clip;
  const [copiedAction, setCopiedAction] = useState<"hook" | "caption" | "package" | null>(null);
  const [viewerOpen, setViewerOpen] = useState(false);

  const hasRenderProof = isRenderedClip(clip);
  const previewUrl = getPreviewUrl(clip);
  const postRank = clip.post_rank || clip.best_post_order || clip.rank || null;
  const scoreValue = getClipScore(clip);
  const badges = buildBadges(clip, hasRenderProof);
  const hookVariants = (clip.hook_variants || []).filter((variant) => variant && variant !== clip.hook).slice(0, 3);
  const captionVariants = Object.entries(clip.caption_variants || {})
    .filter((entry): entry is [string, string] => Boolean(entry[1]?.trim()))
    .slice(0, 3);
  const campaignLabel = clipCampaignStatusLabel(clip);
  const approvalLabel = clipApprovalStateLabel(clip);
  const evergreenLabel = clipEvergreenLabel(clip);
  const showRetryPreview = Boolean(onRecover) && !hasRenderProof;
  const showQueue = !compact && Boolean(onToggleQueue);
  const showFeedback = !compact && Boolean(onVote);
  const assetUrl = getBestClipUrl(clip) || null;
  const canOpenViewer = Boolean(previewUrl || assetUrl);
  const downloadUrl = clip.download_url || null;
  const artifactLinks = clipCaptionArtifactLinks(clip);
  const displayThumbnail = clip.thumbnail_text?.trim() || clip.title;
  const whyThisMatters = buildLeadReason(clip.why_this_matters || clip.reason);
  const showRecoverRender = clipHasRecoverableRender(clip, hasRenderProof);
  const metaLabels: ClipMetaLabel[] = [
    ...(clipHasCaptionArtifacts(clip) ? [{ label: "Captions ready", tone: "neutral" as const }] : []),
    ...(evergreenLabel ? [evergreenLabel] : []),
    ...(campaignLabel ? [campaignLabel] : []),
    ...(approvalLabel ? [approvalLabel] : []),
  ];

  async function handleCopy(text: string, action: "hook" | "caption" | "package") {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedAction(action);
      window.setTimeout(() => {
        setCopiedAction((current) => (current === action ? null : current));
      }, 1600);
    } catch {
      setCopiedAction(null);
    }
  }

  async function handleSaveWinner() {
    try {
      const mediaUrl = clip.download_url || clip.edited_clip_url || clip.clip_url || null;
      await saveProofAsset({
        asset_type: mediaUrl ? "clip" : "hook",
        clip_url: mediaUrl,
        hook_text: clip.hook,
        caption_text: clip.caption,
        platform: clip.suggested_platform || clip.recommended_platform || clip.target_platform,
        ai_score: clip.score || clip.confidence_score || undefined,
        style_tags: [clip.campaign_role, clip.caption_style, clip.render_status].filter(Boolean) as string[],
      });
      await submitClipStyleFeedback({
        clip_id: clip.clip_id || clip.id || "",
        approved: true,
        feedback_notes: "Saved lead clip as winner.",
        style_tags: ["winner", "lead_clip", clip.campaign_role || "clip"].filter(Boolean),
      });
      // eslint-disable-next-line no-console
      console.log("[HeroClip] Saved lead winner to Proof Vault and Style Memory");
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn("[HeroClip] Failed to save winner:", error);
    }
  }

  async function handleRejectAndLearn() {
    try {
      await submitClipStyleFeedback({
        clip_id: clip.clip_id || clip.id || "",
        approved: false,
        feedback_notes: clip.reason_not_rendered || "Lead clip rejected.",
        style_tags: ["rejected", "lead_clip", clip.render_status || "unknown"].filter(Boolean),
      });
      // eslint-disable-next-line no-console
      console.log("[HeroClip] Submitted lead rejection to Style Memory");
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn("[HeroClip] Failed to submit rejection:", error);
    }
  }

  return (
    <>
      {canOpenViewer ? <ClipViewer clip={clip} isOpen={viewerOpen} onClose={() => setViewerOpen(false)} /> : null}
      <section id="lead-clip" className="clip-card top-pick rounded-[40px] border p-6 shadow-card sm:p-7 lg:p-8">
        <div className="-mx-6 -mt-6 mb-6 bg-[var(--gold)] px-6 py-2 text-[10px] font-bold tracking-[0.14em] text-black sm:-mx-7 sm:-mt-7 lg:-mx-8 lg:-mt-8">
          LEAD CLIP
        </div>

        <div className="grid gap-6 xl:grid-cols-[minmax(0,0.58fr),minmax(320px,0.42fr)]">
          <div className="space-y-4">
            <div className="relative overflow-hidden rounded-[30px] border border-[var(--divider)] bg-[var(--surface-veil-strong)] shadow-[var(--shadow-preview)]">
              {canOpenViewer ? (
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
              ) : null}

              {previewUrl ? (
                <LiveClipPreview clip={clip} className="aspect-[9/16]" autoPlay />
              ) : hasRenderProof ? (
                <div className="flex aspect-[9/16] min-h-[360px] flex-col justify-between bg-[radial-gradient(circle_at_top,rgba(16,185,129,0.18),transparent_24%),linear-gradient(180deg,var(--bg-card)_0%,var(--bg)_100%)] p-6">
                  <div className="flex items-center justify-between gap-3">
                    <span className="rounded-full border border-emerald-300/25 bg-emerald-300/10 px-3 py-1.5 text-xs font-medium text-emerald-50">
                      Rendered file ready
                    </span>
                    <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1.5 text-xs text-ink/62">
                      {clipAuthorityLabel(postRank)}
                    </span>
                  </div>
                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-emerald-100">Ready now</p>
                    <h3 className="mt-4 text-2xl font-semibold leading-8 text-ink">{clip.hook || clip.title}</h3>
                    <p className="mt-3 text-sm leading-7 text-ink/62">
                      A rendered asset is available for this clip. Open it in a new tab if inline preview is limited.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="flex aspect-[9/16] min-h-[360px] flex-col justify-between bg-[radial-gradient(circle_at_top,var(--surface-gold-glow),transparent_26%),linear-gradient(180deg,var(--bg-card)_0%,var(--bg)_100%)] p-6">
                  <div className="flex items-center justify-between gap-3">
                    <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1.5 text-xs font-medium text-ink/78">
                      Strategy only
                    </span>
                    <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1.5 text-xs text-ink/62">
                      {clipAuthorityLabel(postRank)}
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
              ) : assetUrl ? (
                <a
                  href={assetUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="primary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-semibold sm:w-auto"
                >
                  Open lead clip
                </a>
              ) : null}

              <button
                type="button"
                onClick={() => void handleCopy(clip.hook || clip.title || "", "hook")}
                className="secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium sm:w-auto"
              >
                {copiedAction === "hook" ? "Hook copied" : "Copy hook"}
              </button>

              <button
                type="button"
                onClick={() => void handleCopy(clip.caption || clip.transcript || "", "caption")}
                className="secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium sm:w-auto"
              >
                {copiedAction === "caption" ? "Caption copied" : "Copy caption"}
              </button>

              <button
                type="button"
                onClick={() => void handleCopy(buildClipPackageText(clip, clip.target_platform || undefined), "package")}
                className="secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium sm:w-auto"
              >
                {copiedAction === "package" ? "Package copied" : "Copy package"}
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

              {!compact && (
                <button
                  type="button"
                  onClick={() => void handleSaveWinner()}
                  className="rounded-full border border-emerald-300/25 bg-emerald-300/10 px-5 py-3 text-sm font-medium text-emerald-100 transition hover:bg-emerald-300/20"
                >
                  Save winner
                </button>
              )}

              {!compact && (
                <button
                  type="button"
                  onClick={() => void handleRejectAndLearn()}
                  className="rounded-full border border-red-300/20 bg-red-300/10 px-5 py-3 text-sm font-medium text-red-100 transition hover:bg-red-300/20"
                >
                  Reject & learn
                </button>
              )}
            </div>

            {artifactLinks.length ? (
              <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
                {artifactLinks.map((link) => (
                  <a
                    key={link.label}
                    href={link.href}
                    target="_blank"
                    rel="noreferrer"
                    className="secondary-button inline-flex w-full items-center justify-center rounded-full px-4 py-2 text-xs font-medium sm:w-auto"
                  >
                    {link.label}
                  </a>
                ))}
              </div>
            ) : null}
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
              {metaLabels.length ? (
                <div className="flex flex-wrap items-center gap-2">
                  {metaLabels.map((label) => (
                    <span key={label.label} className={metaLabelClass(label.tone)}>
                      {label.label}
                    </span>
                  ))}
                </div>
              ) : null}
              {!compact ? <h2 className="text-2xl font-semibold leading-tight text-ink sm:text-[2.15rem]">{clip.title}</h2> : null}
              <p className="text-lg leading-8 text-ink/90">{clip.hook || clip.title}</p>
              <p className="text-sm leading-7 text-ink/66">{whyThisMatters}</p>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="metric-tile rounded-[22px] p-4">
                <p className="text-[10px] uppercase tracking-[0.22em] text-muted">What to post next</p>
                <p className="mt-2 text-sm font-medium text-ink">{clipAuthorityLabel(postRank)}</p>
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
                        onClick={() => void handleCopy(variant, "hook")}
                        className="secondary-button inline-flex items-center justify-center rounded-full px-3 py-2 text-xs font-medium"
                      >
                        Copy
                      </button>
                    </div>
                  ))}
                </div>
              </details>
            ) : null}

            {captionVariants.length ? (
              <details className="rounded-[22px] border border-[var(--divider)] bg-[var(--surface-veil)] p-4">
                <summary className="cursor-pointer list-none text-xs uppercase tracking-[0.22em] text-muted transition-colors hover:text-[var(--ink-mid)]">
                  Caption variants
                </summary>
                <div className="mt-4 grid gap-3">
                  {captionVariants.map(([label, caption]) => (
                    <div key={label} className="rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-3">
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <p className="text-[10px] uppercase tracking-[0.2em] text-muted">{label}</p>
                          <p className="mt-2 text-sm leading-6 text-ink/82">{caption}</p>
                        </div>
                        <button
                          type="button"
                          onClick={() => void handleCopy(caption, "caption")}
                          className="secondary-button inline-flex shrink-0 items-center justify-center rounded-full px-3 py-2 text-xs font-medium"
                        >
                          Copy
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </details>
            ) : null}

            <ClipIntelligencePanel clip={clip} compact={compact} />

            <AutoEditorBrainPanel clip={clip} compact={compact} />

            <CampaignMetaPanel clip={clip} />

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
