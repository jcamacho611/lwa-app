"use client";

import { AutoEditorBrain } from "../lib/types";

type Props = {
  brain: AutoEditorBrain;
};

function ScoreBar({
  label,
  value,
  invert = false,
}: {
  label: string;
  value: number;
  invert?: boolean;
}) {
  const pct = Math.round(Math.max(0, Math.min(100, value)));
  // invert=true means higher is worse — color red at high values
  const color = invert
    ? pct >= 70
      ? "bg-red-400/70"
      : pct >= 40
      ? "bg-amber-400/70"
      : "bg-emerald-400/60"
    : pct >= 70
    ? "bg-emerald-400/70"
    : pct >= 40
    ? "bg-amber-400/70"
    : "bg-red-400/60";

  return (
    <div>
      <div className="flex items-center justify-between gap-2">
        <p className="text-[10px] font-medium text-ink/52">{label}</p>
        <p className="text-[10px] font-semibold text-ink/70">{pct}</p>
      </div>
      <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-white/[0.08]">
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function Chip({ text }: { text: string }) {
  return (
    <span className="inline-block rounded-full border border-white/10 bg-white/[0.06] px-2.5 py-1 text-[10px] font-medium text-ink/62">
      {text}
    </span>
  );
}

export function AutoEditorBrainPanel({ brain }: Props) {
  const { scores, recommendations, export_profile_recommendation, customization, next_edit_actions, risk_flags, status, provider } = brain;

  const isAI = status === "ai";

  return (
    <details className="group rounded-[20px] border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(109,92,255,0.08),transparent_50%)] bg-white/[0.025]">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-4 py-3 transition-colors hover:bg-white/[0.03]">
        <div className="flex items-center gap-2.5">
          <p className="text-xs font-semibold text-ink/72">Auto Editor Brain</p>
          <span
            className={`rounded-full border px-2 py-0.5 text-[9px] font-semibold uppercase tracking-[0.18em] ${
              isAI
                ? "border-purple-300/30 bg-purple-300/12 text-purple-200"
                : "border-white/12 bg-white/[0.05] text-ink/44"
            }`}
          >
            {isAI ? `AI · ${provider}` : "Heuristic"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-semibold text-[var(--gold)]">
            {Math.round(scores.viral_score)} viral
          </span>
          <svg className="h-3.5 w-3.5 text-ink/30 transition-transform group-open:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </summary>

      <div className="space-y-5 px-4 pb-5 pt-1">
        {/* Score bars */}
        <div>
          <p className="mb-3 text-[9px] font-semibold uppercase tracking-[0.22em] text-ink/36">
            Editorial scores
          </p>
          <div className="grid gap-2.5 sm:grid-cols-2">
            <ScoreBar label="Viral potential" value={scores.viral_score} />
            <ScoreBar label="Hook strength" value={scores.hook_score} />
            <ScoreBar label="Retention" value={scores.retention_score} />
            <ScoreBar label="Clarity" value={scores.clarity_score} />
            <ScoreBar label="Focus" value={scores.focus_score} />
            <ScoreBar label="Pacing" value={scores.pacing_score} />
            <ScoreBar label="Silence risk" value={scores.silence_risk_score} invert />
            <ScoreBar label="Dead scene risk" value={scores.dead_scene_risk_score} invert />
          </div>
        </div>

        {/* Edit recommendations */}
        <div className="grid gap-2 sm:grid-cols-2">
          {recommendations.caption_style_recommendation && (
            <div className="rounded-[14px] border border-white/8 bg-black/10 px-3 py-2.5">
              <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-ink/36">Caption style</p>
              <p className="mt-1 text-xs font-medium text-ink/72">{recommendations.caption_style_recommendation}</p>
            </div>
          )}
          {recommendations.font_style_recommendation && (
            <div className="rounded-[14px] border border-white/8 bg-black/10 px-3 py-2.5">
              <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-ink/36">Font</p>
              <p className="mt-1 text-xs font-medium text-ink/72">{recommendations.font_style_recommendation}</p>
            </div>
          )}
          {recommendations.edit_style_recommendation && (
            <div className="rounded-[14px] border border-white/8 bg-black/10 px-3 py-2.5">
              <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-ink/36">Edit style</p>
              <p className="mt-1 text-xs font-medium text-ink/72">{recommendations.edit_style_recommendation}</p>
            </div>
          )}
          {recommendations.filter_recommendation && (
            <div className="rounded-[14px] border border-white/8 bg-black/10 px-3 py-2.5">
              <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-ink/36">Filter / color</p>
              <p className="mt-1 text-xs font-medium text-ink/72">{recommendations.filter_recommendation}</p>
            </div>
          )}
        </div>

        {/* Export profile */}
        <div className="rounded-[14px] border border-white/8 bg-black/10 px-3 py-2.5">
          <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-ink/36">Export profile</p>
          <p className="mt-1 text-xs font-semibold text-ink/72">{export_profile_recommendation.label}</p>
          <p className="mt-0.5 text-[10px] text-ink/42">
            {export_profile_recommendation.width}×{export_profile_recommendation.height} · {export_profile_recommendation.fps}fps · {export_profile_recommendation.bitrate} · {export_profile_recommendation.container}
          </p>
        </div>

        {/* Music sync */}
        {recommendations.music_sync_notes && (
          <div className="rounded-[14px] border border-white/8 bg-black/10 px-3 py-2.5">
            <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-ink/36">Music sync</p>
            <p className="mt-1 text-xs leading-5 text-ink/62">{recommendations.music_sync_notes}</p>
          </div>
        )}

        {/* Pacing notes */}
        {recommendations.pacing_notes && (
          <div className="rounded-[14px] border border-white/8 bg-black/10 px-3 py-2.5">
            <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-ink/36">Pacing</p>
            <p className="mt-1 text-xs leading-5 text-ink/62">{recommendations.pacing_notes}</p>
          </div>
        )}

        {/* B-roll */}
        {recommendations.b_roll_suggestions.length > 0 && (
          <div>
            <p className="mb-2 text-[9px] font-semibold uppercase tracking-[0.22em] text-ink/36">B-roll ideas</p>
            <div className="space-y-1.5">
              {recommendations.b_roll_suggestions.map((s, i) => (
                <p key={i} className="text-xs leading-5 text-ink/58">· {s}</p>
              ))}
            </div>
          </div>
        )}

        {/* Next actions */}
        {next_edit_actions.length > 0 && (
          <div>
            <p className="mb-2 text-[9px] font-semibold uppercase tracking-[0.22em] text-ink/36">Next actions</p>
            <div className="space-y-1.5">
              {next_edit_actions.map((a, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="mt-0.5 h-4 w-4 shrink-0 rounded-full bg-[var(--gold)]/20 text-center text-[9px] font-bold leading-4 text-[var(--gold)]">
                    {i + 1}
                  </span>
                  <p className="text-xs leading-5 text-ink/68">{a}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Customization toggles */}
        {customization.options.length > 0 && (
          <div>
            <p className="mb-2 text-[9px] font-semibold uppercase tracking-[0.22em] text-ink/36">Editor toggles</p>
            <div className="flex flex-wrap gap-1.5">
              {customization.options.map((opt) => (
                <Chip key={opt} text={opt.replace(/_/g, " ")} />
              ))}
            </div>
          </div>
        )}

        {/* Risk flags */}
        {risk_flags.length > 0 && (
          <div>
            <p className="mb-2 text-[9px] font-semibold uppercase tracking-[0.22em] text-red-400/60">Risk flags</p>
            <div className="flex flex-wrap gap-1.5">
              {risk_flags.map((flag) => (
                <span
                  key={flag}
                  className="inline-block rounded-full border border-red-400/20 bg-red-400/8 px-2.5 py-1 text-[10px] font-medium text-red-300/70"
                >
                  {flag.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </details>
  );
}
