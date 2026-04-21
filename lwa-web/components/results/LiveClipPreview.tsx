"use client";

import type { ClipResult } from "../../lib/types";

type LiveClipPreviewProps = {
  clip: ClipResult;
  autoPlay?: boolean;
  className?: string;
};

export function LiveClipPreview({ clip, autoPlay = false, className = "aspect-[9/16]" }: LiveClipPreviewProps) {
  const playable = clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url;
  const thumbnail = clip.thumbnail_url || clip.preview_image_url;

  if (!playable) {
    return (
      <div className={`${className} flex items-center justify-center rounded-[inherit] border border-white/10 bg-black/35 text-sm text-white/70`}>
        Preview still processing
      </div>
    );
  }

  return (
    <video
      src={playable}
      poster={thumbnail || undefined}
      controls={!autoPlay}
      autoPlay={autoPlay}
      muted={autoPlay}
      className={className}
    />
  );
}
