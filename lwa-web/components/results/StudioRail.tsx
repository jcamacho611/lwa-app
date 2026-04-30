"use client";

import type { ClipResult } from "../../lib/types";
import { LiveClipPreview } from "./LiveClipPreview";
import { RetryPreviewButton } from "./RetryPreviewButton";

type StudioRailProps = {
  clips: ClipResult[];
  onClipSelect?: (clip: ClipResult) => void;
  onRetryClip?: (clip: ClipResult) => void;
  onDownloadClip?: (clip: ClipResult) => void;
  selectedClipId?: string;
};

function secondsFromTime(value?: string | number | null) {
  if (typeof value === "number") return value;
  if (!value) return null;
  const parts = value.split(":").map((part) => Number(part));
  if (parts.some((part) => Number.isNaN(part))) return null;
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  return null;
}

function durationLabel(clip: ClipResult) {
  const start = secondsFromTime(clip.start_time);
  const end = secondsFromTime(clip.end_time);
  if (start == null || end == null || end <= start) return null;
  const duration = end - start;
  return `${Math.floor(duration / 60)}:${String(Math.floor(duration % 60)).padStart(2, "0")}`;
}

export function StudioRail({ clips, onClipSelect, onRetryClip, onDownloadClip, selectedClipId }: StudioRailProps) {
  return (
    <div className="flex flex-col gap-3 p-4 bg-ink/5 rounded-xl">
      <h3 className="text-lg font-semibold text-ink/90 mb-4">
        Clip Library
      </h3>
      
      <div className="space-y-3">
        {clips.map((clip, index) => {
          const isSelected = selectedClipId === clip.id || selectedClipId === clip.clip_id;
          const renderStatus = clip.render_status || "pending";
          const isStrategyOnly = Boolean(clip.is_strategy_only) && !clip.preview_url && !clip.clip_url;
          const isReady = renderStatus === "ready" && !isStrategyOnly;
          const isFailed = renderStatus === "failed";
          const isPending = !isStrategyOnly && renderStatus === "pending";
          const isRendering = renderStatus === "rendering";
          const duration = durationLabel(clip);
          const exportUrl = clip.download_url || clip.clip_url || clip.preview_url || undefined;
          
          return (
            <div
              key={clip.id || clip.clip_id}
              className={`
                relative cursor-pointer transition-all duration-200
                ${isSelected ? "ring-2 ring-blue-500" : "hover:ring-2 hover:ring-ink/30"}
                p-4 rounded-lg border border-ink/20
                ${isSelected ? "bg-ink/10" : "bg-white"}
                ${isStrategyOnly ? "border-accent/20" : isFailed ? "border-red-200" : isReady ? "border-green-200" : ""}
              `}
              onClick={() => onClipSelect?.(clip)}
            >
              {/* Clip Preview */}
              <div className="aspect-[9/16] w-32 h-56 bg-ink/10 rounded-md mb-3 overflow-hidden">
                <LiveClipPreview
                  clip={clip}
                  autoPlay={false}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Clip Info */}
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-ink/90 truncate">
                    {clip.title || clip.hook || "Untitled Clip"}
                  </h4>
                  
                  {/* Status Badge */}
                  <div className={`
                    px-2 py-1 rounded-full text-xs font-semibold tracking-wide
                    ${isStrategyOnly ? "bg-accent/15 text-accent border border-accent/30" :
                      isReady ? "bg-green-100 text-green-800" :
                      isFailed ? "bg-red-100 text-red-800" :
                      isRendering ? "bg-yellow-100 text-yellow-800" :
                      "bg-gray-100 text-gray-600"}
                  `}>
                    {isStrategyOnly ? "Ideas only" :
                      isReady ? "Ready" :
                      isFailed ? "Failed" :
                      isRendering ? "Rendering" :
                      "Pending"}
                  </div>
                </div>

                {/* Timing Info */}
                {duration ? (
                  <div className="text-sm text-ink/60">
                    <span className="font-medium">Duration:</span>{" "}
                    {duration}
                  </div>
                ) : null}

                {/* Hook/CTA */}
                {clip.hook && (
                  <div className="text-sm text-ink/80 italic">
                    &ldquo;{clip.hook}&rdquo;
                  </div>
                )}
                
                {clip.cta && (
                  <div className="text-sm text-ink/60 font-medium">
                    CTA: {clip.cta}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center gap-2 mt-3">
                  {isFailed && onRetryClip ? (
                    <RetryPreviewButton onRetry={() => onRetryClip(clip)} />
                  ) : null}
                  
                  {isReady && onDownloadClip ? (
                    <button
                      type="button"
                      className="px-3 py-1 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors"
                      onClick={() => onDownloadClip(clip)}
                    >
                      Download
                    </button>
                  ) : null}

                  {isReady && !onDownloadClip && exportUrl ? (
                    <button
                      type="button"
                      className="px-3 py-1 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors"
                      onClick={() => window.open(exportUrl, "_blank", "noopener,noreferrer")}
                    >
                      Download
                    </button>
                  ) : null}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
