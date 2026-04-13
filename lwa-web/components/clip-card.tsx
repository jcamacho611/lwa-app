"use client";

import { useState } from "react";
import { ClipResult } from "../lib/types";

function formatConfidence(value?: number | null) {
  if (typeof value !== "number") {
    return "N/A";
  }
  return `${Math.round(value * 100)}%`;
}

type ClipCardProps = {
  clip: ClipResult;
  featured?: boolean;
};

export function ClipCard({ clip, featured = false }: ClipCardProps) {
  const [copiedLabel, setCopiedLabel] = useState<string | null>(null);
  const assetUrl = clip.edited_clip_url || clip.clip_url || clip.raw_clip_url;

  async function copyValue(label: string, value: string) {
    try {
      await navigator.clipboard.writeText(value);
      setCopiedLabel(label);
      window.setTimeout(() => setCopiedLabel((current) => (current === label ? null : current)), 1600);
    } catch {
      setCopiedLabel("Copy failed");
      window.setTimeout(() => setCopiedLabel(null), 1600);
    }
  }

  const packageText = [
    `Hook: ${clip.hook}`,
    `Caption: ${clip.caption}`,
    `Timestamp: ${clip.start_time} - ${clip.end_time}`,
    `CTA: ${clip.cta_suggestion || "Prompt viewers to comment or follow."}`,
  ].join("\n");

  return (
    <article
      className={[
        "glass-panel rounded-[28px] p-5 text-left transition-all duration-300",
        featured ? "shadow-glow ring-1 ring-white/10" : "shadow-card",
      ].join(" ")}
    >
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-ink/90">
          #{clip.rank || clip.best_post_order || 1}
        </span>
        <span className="rounded-full border border-accent/20 bg-accent/10 px-3 py-1 text-xs font-medium text-accent">
          Score {clip.score}
        </span>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink/75">
          Confidence {formatConfidence(clip.confidence)}
        </span>
        {clip.packaging_angle ? (
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink/75">
            {clip.packaging_angle}
          </span>
        ) : null}
      </div>

      <div className="mb-4">
        <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Hook</p>
        <h3 className="text-lg font-semibold leading-tight text-ink">{clip.hook}</h3>
      </div>

      <div className="grid gap-4 md:grid-cols-[1.3fr,0.7fr]">
        <div className="space-y-4">
          <div>
            <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Caption</p>
            <p className="text-sm leading-6 text-ink/82">{clip.caption}</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Timestamp</p>
              <p className="text-sm text-ink/82">
                {clip.start_time} - {clip.end_time}
              </p>
            </div>
            <div>
              <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">CTA</p>
              <p className="text-sm text-ink/82">{clip.cta_suggestion || "Prompt viewers to comment or follow."}</p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
            <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Why This Works</p>
            <p className="text-sm leading-6 text-ink/82">{clip.reason || "Strong pacing, clear payoff, and creator-ready packaging."}</p>
          </div>
          <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
            <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Platform Fit</p>
            <p className="text-sm leading-6 text-ink/82">{clip.platform_fit || "Optimized for fast short-form viewing."}</p>
          </div>
        </div>
      </div>

      {assetUrl ? (
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <a
            href={assetUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center rounded-full border border-white/12 bg-white/6 px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Open Clip Asset
          </a>
          <button
            type="button"
            onClick={() => copyValue("Hook copied", clip.hook)}
            className="inline-flex items-center rounded-full border border-white/12 bg-white/6 px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Copy Hook
          </button>
          <button
            type="button"
            onClick={() => copyValue("Caption copied", clip.caption)}
            className="inline-flex items-center rounded-full border border-white/12 bg-white/6 px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Copy Caption
          </button>
          <button
            type="button"
            onClick={() => copyValue("Clip pack copied", packageText)}
            className="inline-flex items-center rounded-full border border-white/12 bg-white/6 px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Copy Pack
          </button>
          {copiedLabel ? <span className="text-sm text-accent">{copiedLabel}</span> : null}
        </div>
      ) : (
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => copyValue("Hook copied", clip.hook)}
            className="inline-flex items-center rounded-full border border-white/12 bg-white/6 px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Copy Hook
          </button>
          <button
            type="button"
            onClick={() => copyValue("Caption copied", clip.caption)}
            className="inline-flex items-center rounded-full border border-white/12 bg-white/6 px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Copy Caption
          </button>
          <button
            type="button"
            onClick={() => copyValue("Clip pack copied", packageText)}
            className="inline-flex items-center rounded-full border border-white/12 bg-white/6 px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Copy Pack
          </button>
          {copiedLabel ? <span className="text-sm text-accent">{copiedLabel}</span> : null}
        </div>
      )}
    </article>
  );
}
