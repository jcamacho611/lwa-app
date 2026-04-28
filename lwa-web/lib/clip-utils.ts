import type { ClipResult } from "./types";

const LOCAL_FILE_PREFIXES = ["file://", "/Users/", "/tmp/", "/var/", "C:\\"];

function cleanUrl(value?: string | null): string | undefined {
  const normalized = value?.trim();
  if (!normalized || LOCAL_FILE_PREFIXES.some((prefix) => normalized.startsWith(prefix))) {
    return undefined;
  }
  return normalized;
}

/**
 * Check if a clip has playable rendered video assets.
 */
export function isRenderedClip(clip: ClipResult): boolean {
  return Boolean(
    cleanUrl(clip.edited_clip_url) ||
      cleanUrl(clip.clip_url) ||
      cleanUrl(clip.preview_url) ||
      cleanUrl(clip.raw_clip_url) ||
      cleanUrl(clip.download_url),
  );
}

/**
 * Check if a clip has playable preview/export media. Thumbnail-only assets are
 * useful visual proof, but they must not make a strategy clip look rendered.
 */
export function hasPreviewAsset(clip: ClipResult): boolean {
  return isRenderedClip(clip);
}

export function hasVisualPreviewAsset(clip: ClipResult): boolean {
  return Boolean(isRenderedClip(clip) || cleanUrl(clip.thumbnail_url) || cleanUrl(clip.preview_image_url));
}

/**
 * Split clips into rendered and strategy-only categories.
 */
export function splitClips(clips: ClipResult[]) {
  const rendered = clips.filter(isRenderedClip);
  const strategy = clips.filter((clip) => !isRenderedClip(clip));

  return { rendered, strategy };
}

/**
 * Get the best available URL for a clip preview or download.
 */
export function getBestClipUrl(clip: ClipResult): string | undefined {
  return (
    cleanUrl(clip.edited_clip_url) ||
    cleanUrl(clip.clip_url) ||
    cleanUrl(clip.preview_url) ||
    cleanUrl(clip.raw_clip_url) ||
    cleanUrl(clip.download_url) ||
    undefined
  );
}

export function getPreviewUrl(clip: ClipResult): string | undefined {
  return cleanUrl(clip.preview_url) || cleanUrl(clip.edited_clip_url) || cleanUrl(clip.clip_url) || cleanUrl(clip.raw_clip_url);
}

export function getClipScore(clip: ClipResult): number {
  return Math.round(clip.virality_score ?? clip.score ?? 0);
}

export function clipAuthorityLabel(rank?: number | null): string {
  if (rank === 1) return "Post first";
  if (rank === 2) return "Post next";
  if (rank === 3) return "Post third";
  return "Post later";
}

export function getClipFallbackMessage(clip: ClipResult): string | null {
  return clip.strategy_only_reason || clip.fallback_reason || clip.render_error || clip.recovery_recommendation || null;
}

function packageStatusLabel(clip: ClipResult): string {
  if (clip.rendered_status === "render_failed" || clip.render_status === "failed" || clip.visual_engine_status === "render_failed") {
    return "Render failed";
  }
  return isRenderedClip(clip) ? "Rendered" : "Strategy only";
}

function addLine(lines: string[], label: string, value?: string | number | null) {
  if (value == null) {
    return;
  }
  const normalized = String(value).trim();
  if (!normalized || normalized === "undefined" || normalized === "null") {
    return;
  }
  lines.push(`${label}: ${normalized}`);
}

export function buildClipPackageText(clip: ClipResult, fallbackPlatform?: string): string {
  const postRank = clip.post_rank || clip.best_post_order || clip.rank || null;
  const thumbnailText = clip.thumbnail_text?.trim() || clip.export_package?.thumbnail_text?.trim();
  const lines: string[] = [];

  addLine(lines, "Title", clip.title || clip.hook || "Untitled clip");
  addLine(lines, "Status", packageStatusLabel(clip));
  if (!isRenderedClip(clip)) {
    addLine(lines, "Package Type", "Strategy only");
  }
  addLine(lines, "Score", getClipScore(clip));
  addLine(lines, "Hook", clip.hook || clip.title);
  addLine(lines, "Caption", clip.caption || clip.export_package?.caption);
  addLine(lines, "Why this matters", clip.why_this_matters || clip.reason || clip.retention_reason);
  addLine(lines, "Thumbnail Text", thumbnailText);
  addLine(lines, "CTA", clip.cta_suggestion || clip.cta || clip.export_package?.cta);
  addLine(lines, "Post Order", clipAuthorityLabel(postRank));
  addLine(lines, "Platform", clip.target_platform || clip.platform_fit || fallbackPlatform || "Auto");
  addLine(lines, "Packaging Angle", clip.packaging_angle);
  addLine(lines, "Clip URL", getBestClipUrl(clip));

  return lines.join("\n");
}

export function buildAllPackagesText(clips: ClipResult[], fallbackPlatform?: string): string {
  return clips.map((clip) => buildClipPackageText(clip, fallbackPlatform)).filter(Boolean).join("\n\n---\n\n");
}

/**
 * Sort clips by explicit post order before fallback rank.
 */
export function sortClipsByRank(clips: ClipResult[]): ClipResult[] {
  return [...clips].sort((left, right) => {
    const leftOrder = left.post_rank || left.best_post_order || left.rank || Number.MAX_SAFE_INTEGER;
    const rightOrder = right.post_rank || right.best_post_order || right.rank || Number.MAX_SAFE_INTEGER;
    if (leftOrder !== rightOrder) {
      return leftOrder - rightOrder;
    }
    return getClipScore(right) - getClipScore(left);
  });
}
