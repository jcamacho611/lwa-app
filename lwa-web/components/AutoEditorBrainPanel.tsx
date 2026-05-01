"use client";

import { ClipResult } from "../lib/types";

type AutoEditorBrainPanelProps = {
  clip: ClipResult;
  compact?: boolean;
};

function normalizeScore(score?: number | null): string {
  if (score === null || score === undefined) return "N/A";
  return Math.round(score).toString();
}

function formatViralScore(score?: number | null): string {
  if (score === null || score === undefined) return "No score";
  return `${Math.round(score)}%`;
}

export function AutoEditorBrainPanel({ clip, compact = false }: AutoEditorBrainPanelProps) {
  const autoEditor = clip.auto_editor;
  
  if (!autoEditor) {
    return null;
  }

  const status = autoEditor.status || "unknown";
  const viralScore = autoEditor.viral_score;
  const confidence = autoEditor.confidence_score;
  const processingStages = autoEditor.processing_stages || [];
  const recommendations = autoEditor.recommendations || [];
  const issues = autoEditor.issues || [];

  return (
    <section className="rounded-[22px] border border-[var(--divider)] bg-[var(--surface-veil)] p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-[10px] uppercase tracking-[0.22em] text-muted">Auto Editor Brain</p>
          <p className="mt-2 text-sm leading-6 text-ink/76">
            AI-powered editing analysis and recommendations
          </p>
        </div>
        <span className={[
          "inline-flex w-fit rounded-full border px-3 py-1 text-xs font-semibold",
          status === "completed" 
            ? "border-emerald-300/25 bg-emerald-300/10 text-emerald-50"
            : status === "processing"
            ? "border-amber-300/25 bg-amber-300/10 text-amber-50"
            : "border-[var(--divider)] bg-[var(--surface-soft)] text-ink/72"
        ].join(" ")}>
          {status === "completed" ? "Analysis complete" : status === "processing" ? "Processing..." : status}
        </span>
      </div>

      {/* Viral Score */}
      {viralScore !== null && viralScore !== undefined && (
        <div className="mt-4 rounded-[18px] border border-[var(--gold-border)] bg-[var(--gold-dim)] p-3">
          <div className="flex items-center justify-between">
            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--gold)]">Viral Potential</p>
            <span className="text-[10px] text-[var(--gold)]">{formatViralScore(viralScore)}</span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-[var(--surface-soft)]">
            <div 
              className="h-full rounded-full bg-[var(--gold)]" 
              style={{ width: `${Math.max(0, Math.min(100, viralScore))}%` }} 
            />
          </div>
        </div>
      )}

      {/* Processing Stages */}
      {processingStages.length > 0 && (
        <div className="mt-4">
          <p className="text-[10px] uppercase tracking-[0.22em] text-muted mb-3">Processing Stages</p>
          <div className="space-y-2">
            {processingStages.map((stage: any, index: number) => (
              <div key={index} className="flex items-center gap-3">
                <div className={[
                  "w-2 h-2 rounded-full shrink-0",
                  stage.completed ? "bg-emerald-400" : "bg-amber-400"
                ].join(" ")} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-ink/82">{stage.name}</p>
                  <p className="text-[10px] text-ink/58">{stage.description}</p>
                </div>
                {stage.completed && (
                  <span className="text-[10px] text-emerald-50">✓</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="mt-4">
          <p className="text-[10px] uppercase tracking-[0.22em] text-muted mb-3">Recommendations</p>
          <div className="space-y-2">
            {recommendations.map((rec: any, index: number) => (
              <div key={index} className="rounded-[16px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
                <p className="text-xs font-medium text-ink/82">{rec.title}</p>
                <p className="mt-1 text-[10px] text-ink/58">{rec.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Issues */}
      {issues.length > 0 && (
        <div className="mt-4">
          <p className="text-[10px] uppercase tracking-[0.22em] text-muted mb-3">Issues Detected</p>
          <div className="space-y-2">
            {issues.map((issue: any, index: number) => (
              <div key={index} className="rounded-[16px] border border-red-400/30 bg-red-400/10 px-3 py-2.5">
                <p className="text-xs font-medium text-red-100">{issue.title}</p>
                <p className="mt-1 text-[10px] text-red-50">{issue.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Confidence Score */}
      {confidence !== null && confidence !== undefined && (
        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          <div className="rounded-[16px] border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-2.5">
            <p className="text-[10px] uppercase tracking-[0.2em] text-muted">Confidence</p>
            <p className="mt-1 text-xs font-medium text-ink/82">{normalizeScore(confidence)}</p>
          </div>
        </div>
      )}
    </section>
  );
}
