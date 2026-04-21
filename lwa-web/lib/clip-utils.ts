import type { ClipResult } from "./types";

/**
 * Check if a clip has playable rendered video assets.
 */
export function isRenderedClip(clip: ClipResult): boolean {
  return Boolean(clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url);
}

/**
 * Check if a clip has any useful preview surface, playable or still.
 */
export function hasPreviewAsset(clip: ClipResult): boolean {
  return Boolean(
    clip.preview_url ||
      clip.edited_clip_url ||
      clip.clip_url ||
      clip.raw_clip_url ||
      clip.thumbnail_url ||
      clip.preview_image_url,
  );
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
    clip.preview_url ||
    clip.edited_clip_url ||
    clip.clip_url ||
    clip.raw_clip_url ||
    clip.download_url ||
    undefined
  );
}

/**
 * Sort clips by explicit post order before fallback rank.
 */
export function sortClipsByRank(clips: ClipResult[]): ClipResult[] {
  return [...clips].sort((left, right) => (left.post_rank || left.rank || 0) - (right.post_rank || right.rank || 0));
}
