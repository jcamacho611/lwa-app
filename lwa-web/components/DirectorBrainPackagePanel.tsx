"use client";

import { ClipResult } from "../lib/types";

type DirectorBrainClipFields = ClipResult & {
  algorithm_version?: string | null;
  recommended_platform?: string | null;
  recommended_content_type?: string | null;
  recommended_output_style?: string | null;
  platform_recommendation_reason?: string | null;
  reason_not_rendered?: string | null;
  quality_gate_status?: string | null;
  quality_gate_warnings?: string[] | null;
  revenue_intent_score?: number | null;
  offer_fit_score?: number | null;
  suggested_caption_position?: string | null;
  emphasis_words?: string[] | null;
  caption_style_reason?: string | null;
  campaign_role?: string | null;
  campaign_reason?: string | null;
  funnel_stage?: string | null;
  suggested_post_order?: number | null;
  suggested_platform?: string | null;
  suggested_caption_style?: string | null;
  suggested_cta?: string | null;
};

function displayLabel(value: string | null | undefined) {
  return value?.replace(/_/g, " ").trim() || null;
}

function metricLabel(label: string, value: number | null | undefined) {
  if (value === null || value === undefined) return null;
  return (
    <div className="rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] px-3 py-2">
      <p className="text-[10px] uppercase tracking-[0.2em] text-muted">{label}</p>
      <p className="mt-1 text-sm font-semibold text-ink">{value}</p>
    </div>
  );
}

export function DirectorBrainPackagePanel({ clip }: { clip: ClipResult }) {
  const smartClip = clip as DirectorBrainClipFields;
  const platform = displayLabel(smartClip.recommended_platform || smartClip.target_platform || smartClip.suggested_platform);
  const outputStyle = displayLabel(smartClip.recommended_output_style || smartClip.caption_style || smartClip.suggested_caption_style || smartClip.caption_preset);
  const qualityStatus = displayLabel(smartClip.quality_gate_status || smartClip.render_status || smartClip.rendered_status);
  const campaignRole = displayLabel(smartClip.campaign_role);
  const funnelStage = displayLabel(smartClip.funnel_stage);
  const notRenderedReason = smartClip.reason_not_rendered || smartClip.strategy_only_reason || smartClip.render_error || null;
  const warnings = smartClip.quality_gate_warnings || [];
  const emphasisWords = smartClip.emphasis_words || [];
  const hasAnyDirectorBrainField = Boolean(
    smartClip.algorithm_version ||
      platform ||
      outputStyle ||
      qualityStatus ||
      campaignRole ||
      funnelStage ||
      smartClip.offer_fit_score !== undefined ||
      smartClip.revenue_intent_score !== undefined ||
      notRenderedReason ||
      warnings.length ||
      emphasisWords.length,
  );

  if (!hasAnyDirectorBrainField) {
    return null;
  }

  return (
    <section className="rounded-[20px] border border-[var(--divider)] bg-[var(--surface-soft)] p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--gold)]">Director Brain</p>
        {smartClip.algorithm_version ? (
          <span className="rounded-full border border-[var(--divider)] bg-[var(--surface-veil)] px-2.5 py-1 text-[10px] text-ink/62">
            {smartClip.algorithm_version}
          </span>
        ) : null}
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2">
        {metricLabel("Offer fit", smartClip.offer_fit_score)}
        {metricLabel("Revenue intent", smartClip.revenue_intent_score)}
      </div>

      <div className="mt-3 grid gap-2 text-xs leading-5 text-ink/76">
        {platform ? <p><span className="text-muted">Platform:</span> {platform}</p> : null}
        {outputStyle ? <p><span className="text-muted">Style:</span> {outputStyle}</p> : null}
        {qualityStatus ? <p><span className="text-muted">Quality gate:</span> {qualityStatus}</p> : null}
        {campaignRole ? <p><span className="text-muted">Campaign role:</span> {campaignRole}</p> : null}
        {funnelStage ? <p><span className="text-muted">Funnel stage:</span> {funnelStage}</p> : null}
        {smartClip.suggested_post_order ? <p><span className="text-muted">Suggested post order:</span> {smartClip.suggested_post_order}</p> : null}
        {smartClip.platform_recommendation_reason ? <p><span className="text-muted">Why this platform:</span> {smartClip.platform_recommendation_reason}</p> : null}
        {smartClip.campaign_reason ? <p><span className="text-muted">Campaign reason:</span> {smartClip.campaign_reason}</p> : null}
        {smartClip.caption_style_reason ? <p><span className="text-muted">Caption logic:</span> {smartClip.caption_style_reason}</p> : null}
        {notRenderedReason ? <p><span className="text-muted">Render note:</span> {notRenderedReason}</p> : null}
      </div>

      {emphasisWords.length ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {emphasisWords.slice(0, 6).map((word) => (
            <span key={word} className="rounded-full border border-[var(--divider)] bg-[var(--surface-veil)] px-2.5 py-1 text-[10px] text-ink/70">
              {word}
            </span>
          ))}
        </div>
      ) : null}

      {warnings.length ? (
        <div className="mt-3 rounded-[14px] border border-amber-300/25 bg-amber-300/10 px-3 py-2 text-xs leading-5 text-amber-50">
          {warnings.slice(0, 3).map((warning) => (
            <p key={warning}>{warning}</p>
          ))}
        </div>
      ) : null}
    </section>
  );
}
