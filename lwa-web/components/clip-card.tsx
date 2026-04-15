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
  feedbackVote?: "good" | "bad" | null;
  onVote?: (clip: ClipResult, vote: "good" | "bad") => void;
  queued?: boolean;
  onToggleQueue?: (clip: ClipResult) => void;
};

const captionVariantLabels: Record<string, string> = {
  viral: "Viral",
  story: "Story",
  educational: "Educational",
  controversial: "Controversial",
};

export function ClipCard({ clip, featured = false, feedbackVote = null, onVote, queued = false, onToggleQueue }: ClipCardProps) {
  const [copiedLabel, setCopiedLabel] = useState<string | null>(null);
  const previewAssetUrl = clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url;
  const downloadAssetUrl = clip.download_url;
  const thumbnailUrl = clip.thumbnail_url || clip.preview_image_url;
  const viralityScore = clip.virality_score ?? clip.score;
  const whyThisHits = clip.why_this_matters || clip.reason || "Strong pacing, clear payoff, and creator-ready packaging.";

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
    `Reason: ${clip.reason || "Strong packaging and creator-ready payoff."}`,
    `Packaging Angle: ${clip.packaging_angle || "value"}`,
    `Post Order: ${clip.best_post_order || clip.rank || 1}`,
    `Timestamp: ${clip.start_time} - ${clip.end_time}`,
    `CTA: ${clip.cta_suggestion || "Prompt viewers to comment or follow."}`,
    clip.hook_variants?.length ? `Hook Variants:\n- ${clip.hook_variants.join("\n- ")}` : "",
    clip.caption_variants
      ? `Caption Variants:\n${Object.entries(clip.caption_variants)
          .map(([key, value]) => `- ${captionVariantLabels[key] || key}: ${value}`)
          .join("\n")}`
      : "",
  ].join("\n");

  return (
    <article
      className={[
        "overflow-hidden rounded-[30px] border p-5 text-left transition-all duration-300",
        featured
          ? "hero-card shadow-glow"
          : "glass-panel border-white/10 shadow-card hover:-translate-y-0.5 hover:border-white/16",
      ].join(" ")}
    >
      {/* Header row: rank badge + score + confidence + platform fit + packaging angle */}
      <div className="mb-5 flex flex-wrap items-center gap-2">
        {featured ? (
          <span className="status-chip status-approved flex items-center gap-1.5">
            <span>🏆</span>
            <span>Top clip · Post #{clip.best_post_order || clip.rank || 1}</span>
          </span>
        ) : (
          <span className="status-chip status-ready">
            Post #{clip.best_post_order || clip.rank || 1}
          </span>
        )}
        <span className={["status-chip", featured ? "status-approved" : "status-submitted"].join(" ")}>
          Score {viralityScore}
        </span>
        <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/75">
          {formatConfidence(clip.confidence)} confidence
        </span>
        {clip.platform_fit ? (
          <span className="rounded-full border border-accent/20 bg-accent/[0.07] px-3 py-1.5 text-xs text-accent/90">
            {clip.platform_fit}
          </span>
        ) : null}
        {clip.packaging_angle ? (
          <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs text-ink/75">
            {clip.packaging_angle}
          </span>
        ) : null}
        {clip.thumbnail_text ? (
          <span className="rounded-full border border-neonPurple/20 bg-neonPurple/[0.08] px-3 py-1.5 text-xs text-white/80">
            🖼 {clip.thumbnail_text}
          </span>
        ) : null}
      </div>

      {/* Hook */}
      <div className="mb-5">
        <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">{featured ? "Top hook" : "Hook"}</p>
        <h3 className={["font-semibold leading-tight text-ink", featured ? "text-2xl sm:text-[2rem]" : "text-xl"].join(" ")}>{clip.hook}</h3>
        <p className="mt-3 text-sm text-accent">
          {clip.best_post_order === 1
            ? "Post this first."
            : `Run this after clip ${Math.max((clip.best_post_order || clip.rank || 2) - 1, 1)}.`}
        </p>
      </div>

      {previewAssetUrl || thumbnailUrl ? (
        <div className="mb-5 overflow-hidden rounded-[24px] border border-white/10 bg-[#050816]">
          {previewAssetUrl ? (
            <video
              className="aspect-[9/16] w-full bg-black object-cover"
              src={previewAssetUrl}
              poster={thumbnailUrl || undefined}
              controls
              playsInline
              preload="metadata"
            />
          ) : thumbnailUrl ? (
            <img src={thumbnailUrl} alt={clip.hook} className="aspect-[9/16] w-full bg-black object-cover" />
          ) : null}
        </div>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[1.28fr,0.72fr]">
        <div className="space-y-4">
          <div>
            <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Caption</p>
            <p className="text-sm leading-7 text-ink/82">{clip.caption}</p>
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
          {clip.transcript ? (
            <div>
              <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Clip transcript</p>
              <p className="text-sm leading-7 text-ink/74">{clip.transcript}</p>
            </div>
          ) : null}
        </div>

        <div className="space-y-3">
          {/* Why this hits — prominent signal card */}
          <div className="signal-card rounded-[24px] p-4">
            <div className="mb-3 flex items-center gap-2">
              <span className="text-base">⚡</span>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[rgba(251,113,133,0.9)]">Why this hits</p>
            </div>
            <p className="text-sm leading-6 text-ink/90">{whyThisHits}</p>
          </div>
          {/* Platform fit */}
          <div className="metric-tile rounded-[24px] p-4">
            <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">Platform fit</p>
            <p className="text-sm leading-6 text-ink/82">{clip.platform_fit || "Optimized for fast short-form viewing."}</p>
          </div>
        </div>
      </div>

      {clip.hook_variants?.length ? (
        <div className="mt-5 metric-tile rounded-[24px] p-4">
          <div className="mb-3 flex items-center justify-between gap-3">
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Hook Variants</p>
            <span className="text-xs text-ink/50">Tap to copy.</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {clip.hook_variants.map((variant, index) => (
              <button
                key={`${clip.id}-hook-${index}`}
                type="button"
                onClick={() => copyValue("Hook variant copied", variant)}
                className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-2 text-left text-xs text-ink/82 transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
              >
                {variant}
              </button>
            ))}
          </div>
        </div>
      ) : null}

      {clip.caption_variants && Object.keys(clip.caption_variants).length ? (
        <div className="mt-4 metric-tile rounded-[24px] p-4">
          <div className="mb-3 flex items-center justify-between gap-3">
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Caption Styles</p>
            <span className="text-xs text-ink/50">Built to test fast.</span>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {Object.entries(clip.caption_variants).map(([key, value]) => (
              <button
                key={`${clip.id}-caption-${key}`}
                type="button"
                onClick={() => copyValue(`${captionVariantLabels[key] || key} caption copied`, value)}
                className="rounded-[22px] border border-white/10 bg-white/[0.05] p-3 text-left transition hover:border-accent/30 hover:bg-accent/10"
              >
                <p className="text-xs uppercase tracking-[0.22em] text-muted">{captionVariantLabels[key] || key}</p>
                <p className="mt-2 text-sm leading-6 text-ink/82">{value}</p>
              </button>
            ))}
          </div>
        </div>
      ) : null}

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={() => onVote?.(clip, "good")}
          className={[
            "inline-flex items-center rounded-full border px-4 py-2 text-sm font-medium transition",
            feedbackVote === "good"
              ? "border-emerald-400/30 bg-emerald-400/12 text-emerald-200"
              : "border-white/12 bg-white/[0.06] text-ink hover:border-emerald-400/30 hover:bg-emerald-400/10 hover:text-emerald-200",
          ].join(" ")}
        >
          Good Clip
        </button>
        <button
          type="button"
          onClick={() => onVote?.(clip, "bad")}
          className={[
            "inline-flex items-center rounded-full border px-4 py-2 text-sm font-medium transition",
            feedbackVote === "bad"
              ? "border-red-400/30 bg-red-400/10 text-red-100"
              : "border-white/12 bg-white/[0.06] text-ink hover:border-red-400/30 hover:bg-red-400/10 hover:text-red-100",
          ].join(" ")}
        >
          Bad Clip
        </button>
        <button
          type="button"
          onClick={() => onToggleQueue?.(clip)}
          className={[
            "inline-flex items-center rounded-full border px-4 py-2 text-sm font-medium transition",
            queued
              ? "border-neonPurple/30 bg-neonPurple/15 text-white shadow-neon"
              : "border-white/12 bg-white/[0.06] text-ink hover:border-neonPurple/30 hover:bg-neonPurple/10 hover:text-white",
          ].join(" ")}
        >
          {queued ? "Queued" : "Mark Ready"}
        </button>
        <span className="text-sm text-ink/56">Mark what hits. Future runs learn from it.</span>
      </div>

      {previewAssetUrl || downloadAssetUrl ? (
        <div className="mt-5 flex flex-wrap items-center gap-3">
          {previewAssetUrl ? (
            <a
              href={previewAssetUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center rounded-full border border-white/12 bg-white/[0.06] px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
            >
              Preview
            </a>
          ) : null}
          {downloadAssetUrl ? (
            <a
              href={downloadAssetUrl}
              download
              className="inline-flex items-center rounded-full border border-neonPurple/20 bg-neonPurple/12 px-4 py-2 text-sm font-medium text-white transition hover:bg-neonPurple/18"
            >
              Download
            </a>
          ) : (
            <span className="rounded-full border border-neonPurple/18 bg-neonPurple/10 px-4 py-2 text-sm text-white/78">
              Pro unlocks download
            </span>
          )}
          <button
            type="button"
            onClick={() => copyValue("Hook copied", clip.hook)}
            className="inline-flex items-center rounded-full border border-white/12 bg-white/[0.06] px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Copy Hook
          </button>
          <button
            type="button"
            onClick={() => copyValue("Caption copied", clip.caption)}
            className="inline-flex items-center rounded-full border border-white/12 bg-white/[0.06] px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Copy Caption
          </button>
          <button
            type="button"
            onClick={() => copyValue("Clip pack copied", packageText)}
            className="inline-flex items-center rounded-full border border-white/12 bg-white/[0.06] px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
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
            className="inline-flex items-center rounded-full border border-white/12 bg-white/[0.06] px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Copy Hook
          </button>
          <button
            type="button"
            onClick={() => copyValue("Caption copied", clip.caption)}
            className="inline-flex items-center rounded-full border border-white/12 bg-white/[0.06] px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Copy Caption
          </button>
          <button
            type="button"
            onClick={() => copyValue("Clip pack copied", packageText)}
            className="inline-flex items-center rounded-full border border-white/12 bg-white/[0.06] px-4 py-2 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent"
          >
            Copy Pack
          </button>
          {copiedLabel ? <span className="text-sm text-accent">{copiedLabel}</span> : null}
        </div>
      )}
    </article>
  );
}
