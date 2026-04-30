"use client";

import { getClipFallbackMessage, getClipScore } from "../lib/clip-utils";
import { buildLeadReason } from "../lib/result-copy";
import { ClipResult } from "../lib/types";

type ClipIntelligencePanelProps = {
  clip: ClipResult;
  compact?: boolean;
};

type BadgeValue = string | { badge?: string; label?: string; color?: string; priority?: string; placement?: string };

function labelize(value: string) {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function normalizeBadges(values?: BadgeValue[] | null) {
  return (values || [])
    .map((value) => (typeof value === "string" ? value : value.label || value.badge || value.priority || ""))
    .map((value) => value.trim())
    .filter(Boolean)
    .slice(0, 4);
}

function scoreRows(clip: ClipResult, compact?: boolean) {
  const maxRows = compact ? 4 : 6;
  return Object.entries(clip.score_breakdown || {})
    .filter((entry): entry is [string, number] => typeof entry[1] === "number" && Number.isFinite(entry[1]))
    .sort((left, right) => right[1] - left[1])
    .slice(0, maxRows);
}

function metricValue(value?: string | number | null) {
  if (value === null || value === undefined) return null;
  const normalized = typeof value === "number" ? String(Math.round(value)) : value.trim();
  return normalized || null;
}

function directorMetric(label: string, value?: string | number | null) {
  const normalized = metricValue(value);
  if (!normalized) return null;
  return (
    <div className="rounded-[16px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
      <p className="text-[10px] uppercase tracking-[0.2em] text-muted">{label}</p>
      <p className="mt-1 text-xs font-medium text-ink/82">{labelize(normalized)}</p>
    </div>
  );
}

export function ClipIntelligencePanel({ clip, compact = false }: ClipIntelligencePanelProps) {
  const rows = scoreRows(clip, compact);
  const badges = normalizeBadges(clip.frontend_badges);
  const fallbackMessage = getClipFallbackMessage(clip);
  const whyThisRanks = buildLeadReason(clip.why_this_matters || clip.reason || clip.retention_reason || clip.scoring_explanation);
  const directorMetrics = [
    directorMetric("Platform", clip.recommended_platform || clip.suggested_platform || clip.platform_fit),
    directorMetric("Content type", clip.recommended_content_type),
    directorMetric("Output style", clip.recommended_output_style || clip.caption_style || clip.suggested_caption_style || clip.caption_preset),
    directorMetric("Quality gate", clip.quality_gate_status),
    directorMetric("Offer fit", clip.offer_fit_score),
    directorMetric("Revenue intent", clip.revenue_intent_score),
  ].filter(Boolean);
  const directorNotes = [
    clip.platform_recommendation_reason ? `Platform logic: ${clip.platform_recommendation_reason}` : null,
    clip.caption_style_reason ? `Caption logic: ${clip.caption_style_reason}` : null,
    clip.reason_not_rendered ? `Render note: ${clip.reason_not_rendered}` : null,
  ].filter((note): note is string => Boolean(note));
  const warnings = (clip.quality_gate_warnings || []).slice(0, 3);
  const hasDirectorDetails = Boolean(clip.algorithm_version || directorMetrics.length || directorNotes.length || warnings.length);
  const hasDetails = Boolean(
    rows.length ||
      badges.length ||
      whyThisRanks ||
      clip.confidence_score ||
      clip.confidence_label ||
      clip.first_three_seconds_assessment ||
      clip.hook_strength ||
      clip.platform_fit ||
      fallbackMessage ||
      hasDirectorDetails,
  );

  if (!hasDetails) {
    return null;
  }

  return (
    <section className="rounded-[22px] border border-[var(--divider)] bg-[var(--surface-veil)] p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-[10px] uppercase tracking-[0.22em] text-muted">Why this ranks</p>
          <p className="mt-2 text-sm leading-6 text-ink/76">{whyThisRanks}</p>
        </div>
        <span className="inline-flex w-fit rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1 text-xs font-semibold text-[var(--gold)]">
          {getClipScore(clip)}
        </span>
      </div>

      {hasDirectorDetails ? (
        <div className="mt-4 rounded-[18px] border border-[var(--gold-border)] bg-[var(--gold-dim)] p-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--gold)]">Director Brain</p>
            {clip.algorithm_version ? <span className="text-[10px] text-ink/58">{clip.algorithm_version}</span> : null}
          </div>
          {directorMetrics.length ? <div className="mt-3 grid gap-2 sm:grid-cols-2">{directorMetrics}</div> : null}
          {directorNotes.length ? (
            <div className="mt-3 space-y-1 text-xs leading-5 text-ink/72">
              {directorNotes.map((note) => (
                <p key={note}>{note}</p>
              ))}
            </div>
          ) : null}
          {warnings.length ? (
            <div className="mt-3 rounded-[14px] border border-amber-300/25 bg-amber-300/10 px-3 py-2 text-xs leading-5 text-amber-50">
              {warnings.map((warning) => (
                <p key={warning}>{warning}</p>
              ))}
            </div>
          ) : null}
        </div>
      ) : null}

      {clip.confidence_score || clip.confidence_label || clip.platform_fit ? (
        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          {clip.confidence_score ? (
            <div className="rounded-[16px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[0.2em] text-muted">Confidence</p>
              <p className="mt-1 text-xs font-medium text-ink/82">{Math.round(clip.confidence_score)}</p>
            </div>
          ) : null}
          {clip.confidence_label ? (
            <div className="rounded-[16px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[0.2em] text-muted">Signal</p>
              <p className="mt-1 text-xs font-medium text-ink/82">{clip.confidence_label}</p>
            </div>
          ) : null}
          {clip.platform_fit ? (
            <div className="rounded-[16px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[0.2em] text-muted">Platform fit</p>
              <p className="mt-1 text-xs font-medium text-ink/82">{clip.platform_fit}</p>
            </div>
          ) : null}
        </div>
      ) : null}

      {rows.length ? (
        <div className="mt-4 grid gap-2">
          {rows.map(([label, value]) => (
            <div key={label} className="grid grid-cols-[minmax(0,1fr),44px] items-center gap-3">
              <div className="min-w-0">
                <div className="flex items-center justify-between gap-3">
                  <p className="truncate text-xs font-medium text-ink/78">{labelize(label)}</p>
                  <p className="text-xs font-semibold text-ink/72">{Math.round(value)}</p>
                </div>
                <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-[var(--surface-soft)]">
                  <div className="h-full rounded-full bg-[var(--gold)]" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : null}

      {badges.length ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {badges.map((badge) => (
            <span key={badge} className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-2.5 py-1 text-[11px] text-ink/72">
              {labelize(badge)}
            </span>
          ))}
        </div>
      ) : null}

      {clip.first_three_seconds_assessment || clip.hook_strength || fallbackMessage ? (
        <div className="mt-4 space-y-2 text-xs leading-6 text-ink/62">
          {clip.first_three_seconds_assessment ? <p>{clip.first_three_seconds_assessment}</p> : null}
          {clip.hook_strength ? <p>Hook strength: {clip.hook_strength}</p> : null}
          {fallbackMessage ? <p>{fallbackMessage}</p> : null}
        </div>
      ) : null}
    </section>
  );
}
