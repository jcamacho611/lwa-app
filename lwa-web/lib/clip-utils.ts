import { ClipResult } from "@/lib/types";

/**
 * Check if a clip has any rendered video assets.
 */
export function isRenderedClip(clip: ClipResult): boolean {
  return !!(
    clip.preview_url ||
    clip.edited_clip_url ||
    clip.clip_url ||
    clip.raw_clip_url ||
    clip.download_url
  );
}

/**
 * Split clips into rendered and strategy-only categories.
 */
export function splitClips(clips: ClipResult[]) {
  const rendered = clips.filter(isRenderedClip);
  const strategy = clips.filter((c) => !isRenderedClip(c));

  return { rendered, strategy };
}

/**
 * Get the best available URL for a clip (for preview/download).
 */
export function getBestClipUrl(clip: ClipResult): string | undefined {
  return (
    clip.preview_url ||
    clip.edited_clip_url ||
    clip.clip_url ||
    clip.raw_clip_url ||
    clip.download_url
  );
}

/**
 * Sort clips by post_rank or rank.
 */
export function sortClipsByRank(clips: ClipResult[]): ClipResult[] {
  return [...clips].sort((a, b) => (a.post_rank || a.rank || 0) - (b.post_rank || b.rank || 0));
}