"use client";

import { useMemo, useState } from "react";
import type { ClipResult } from "../../lib/types";
import {
  getRecoveryActionsForClip,
  getRecoveryDecision,
  type LwaRecoveryDecision,
  type LwaRecoveryIssueType,
} from "../../lib/lwa-recovery-engine";

const issueButtons: { issueType: LwaRecoveryIssueType; label: string }[] = [
  { issueType: "render_failed", label: "Render failed" },
  { issueType: "strategy_only", label: "Strategy only" },
  { issueType: "missing_preview", label: "Missing preview" },
  { issueType: "provider_unavailable", label: "Provider down" },
  { issueType: "export_failed", label: "Export failed" },
  { issueType: "asset_missing", label: "Asset missing" },
  { issueType: "invalid_source", label: "Invalid source" },
  { issueType: "unknown_error", label: "Unknown error" },
];

const mockClips: Array<{ label: string; clip: ClipResult }> = [
  {
    label: "Rendered clip",
    clip: {
      id: "clip_rendered",
      title: "Rendered proof",
      hook: "Strong first three seconds",
      caption: "Ready to post.",
      score: 88,
      is_rendered: true,
      render_status: "ready",
      preview_url: "/generated/req_demo/clip_rendered.mp4",
      download_url: "/generated/req_demo/clip_rendered.mp4",
      burned_caption_url: "/generated/req_demo/clip_rendered.mp4",
      render_error: null,
      recovery_recommendation: "This one is ready for review.",
    } as ClipResult,
  },
  {
    label: "Strategy-only clip",
    clip: {
      id: "clip_strategy",
      title: "Strategy only",
      hook: "Useful hook idea",
      caption: "Export the package, then recover later.",
      score: 61,
      is_strategy_only: true,
      strategy_only: true,
      render_status: "strategy_only",
      render_error: null,
      recovery_recommendation: "Keep the ranked idea and recover render when available.",
    } as ClipResult,
  },
  {
    label: "Render failed clip",
    clip: {
      id: "clip_failed",
      title: "Render failed",
      hook: "Clip with missing media",
      caption: "Recovery path needed.",
      score: 44,
      render_status: "failed",
      render_error: "ffmpeg failed",
      recovery_recommendation: "Retry render or downgrade quality.",
    } as ClipResult,
  },
];

export default function LwaRecoveryPanel() {
  const [selectedIssue, setSelectedIssue] =
    useState<LwaRecoveryIssueType>("strategy_only");
  const [selectedClipIndex, setSelectedClipIndex] = useState(0);

  const issueDecision = useMemo(
    () => getRecoveryDecision(selectedIssue),
    [selectedIssue],
  );
  const clipDecision = useMemo(
    () => getRecoveryActionsForClip(mockClips[selectedClipIndex].clip),
    [selectedClipIndex],
  );

  return (
    <section className="relative mx-auto max-w-7xl px-6 py-12 text-[#F5F1E8]">
      <div className="max-w-4xl">
        <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">
          Recovery engine
        </p>
        <h2 className="mt-5 text-[clamp(2.4rem,5vw,5rem)] font-black uppercase leading-[0.92] tracking-normal text-white">
          Failure should still move the run forward.
        </h2>
        <p className="mt-6 text-base leading-8 text-white/62">
          This engine turns render failures, strategy-only results, missing
          previews, provider problems, and source problems into useful next
          actions instead of dead ends.
        </p>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <section className="rounded-[28px] border border-white/10 bg-black/35 p-6 shadow-[0_28px_90px_-60px_rgba(126,58,242,0.9)]">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
            Issue picker
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            {issueButtons.map((item) => (
              <button
                key={item.issueType}
                type="button"
                onClick={() => setSelectedIssue(item.issueType)}
                className={[
                  "rounded-full border px-3 py-2 text-xs font-semibold transition",
                  selectedIssue === item.issueType
                    ? "border-[#C9A24A]/40 bg-[#C9A24A]/15 text-white"
                    : "border-white/10 bg-white/[0.05] text-white/72 hover:border-[#C9A24A]/30 hover:bg-[#C9A24A]/10 hover:text-white",
                ].join(" ")}
              >
                {item.label}
              </button>
            ))}
          </div>

          <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-white/45">
                {issueDecision.severity}
              </span>
              <span className="rounded-full border border-[#C9A24A]/25 bg-[#C9A24A]/10 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-[#E9C77B]">
                {issueDecision.issueType}
              </span>
            </div>
            <h3 className="mt-4 text-2xl font-semibold text-white">
              {issueDecision.userMessage}
            </h3>
            <p className="mt-3 text-sm leading-6 text-white/62">
              {issueDecision.technicalReason}
            </p>
            <p className="mt-3 text-sm leading-6 text-[#E9C77B]">
              {issueDecision.leeWuhLine}
            </p>
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                primary action
              </p>
              <p className="mt-2 text-sm font-semibold text-white">
                {issueDecision.primaryAction.replaceAll("_", " ")}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                continue
              </p>
              <p className="mt-2 text-sm font-semibold text-white">
                {issueDecision.canContinue ? "yes" : "no"}
              </p>
            </div>
          </div>
        </section>

        <section className="rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
            Clip recovery examples
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            {mockClips.map((item, index) => (
              <button
                key={item.label}
                type="button"
                onClick={() => setSelectedClipIndex(index)}
                className={[
                  "rounded-full border px-3 py-2 text-xs font-semibold transition",
                  selectedClipIndex === index
                    ? "border-[#C9A24A]/40 bg-[#C9A24A]/15 text-white"
                    : "border-white/10 bg-white/[0.05] text-white/72 hover:border-[#C9A24A]/30 hover:bg-[#C9A24A]/10 hover:text-white",
                ].join(" ")}
              >
                {item.label}
              </button>
            ))}
          </div>

          <div className="mt-6 rounded-2xl border border-white/10 bg-black/25 p-5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-white/45">
                {mockClips[selectedClipIndex].clip.render_status ?? "unknown"}
              </span>
              <span className="rounded-full border border-[#C9A24A]/25 bg-[#C9A24A]/10 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-[#E9C77B]">
                {clipDecision.issueType}
              </span>
            </div>
            <h3 className="mt-4 text-2xl font-semibold text-white">
              {mockClips[selectedClipIndex].clip.title}
            </h3>
            <p className="mt-3 text-sm leading-6 text-white/62">
              {mockClips[selectedClipIndex].clip.recovery_recommendation}
            </p>
            <p className="mt-3 text-sm leading-6 text-[#E9C77B]">
              {clipDecision.leeWuhLine}
            </p>
          </div>

          <div className="mt-5 grid gap-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                recommended actions
              </p>
              <p className="mt-2 text-sm leading-6 text-white/68">
                {issueDecision.recommendedActions.join(", ")}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                export blocked
              </p>
              <p className="mt-2 text-sm leading-6 text-white/68">
                {issueDecision.shouldBlockExport ? "yes" : "no"}
              </p>
            </div>
          </div>
        </section>
      </div>
    </section>
  );
}

