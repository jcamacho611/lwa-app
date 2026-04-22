"use client";

import type { ClipResult } from "../../lib/types";
import ClipPreview from "./ClipPreview";

type LiveClipPreviewProps = {
  clip: ClipResult;
  autoPlay?: boolean;
  className?: string;
};

export function LiveClipPreview({ clip, autoPlay = false, className = "aspect-[9/16]" }: LiveClipPreviewProps) {
  return <ClipPreview clip={clip} autoPlay={autoPlay} className={className} />;
}
