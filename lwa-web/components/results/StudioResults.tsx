"use client";

import type { ClipResult } from "../../lib/types";
import { RESULT_COPY } from "../../lib/result-copy";
import { useClipPreviewPolling } from "../../hooks/useClipPreviewPolling";
import { LiveClipPreview } from "./LiveClipPreview";
import { RetryPreviewButton } from "./RetryPreviewButton";

type StudioResultsProps = {
  result: ClipResult | null;
  isLoading: boolean;
  loadingStageIndex: number;
  error: string | null;
  onRetry?: () => void;
};

export function StudioResults({ result, isLoading, loadingStageIndex, error, onRetry }: StudioResultsProps) {
  const liveClip = useClipPreviewPolling(result);
  const playable = liveClip.preview_url || liveClip.edited_clip_url || liveClip.clip_url || liveClip.raw_clip_url;

  const renderStatus = liveClip.render_status || "pending";
  const isPending = renderStatus === "pending";
  const isRendering = renderStatus === "rendering";
  const isReady = renderStatus === "ready";
  const isFailed = renderStatus === "failed";

  const showRetry = isFailed && onRetry;

  return (
    <div className="space-y-4">
      {/* Status Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-ink/90">
          {isLoading ? "Processing..." : isReady ? "Ready" : isFailed ? "Failed" : "Pending"}
        </h3>
        {showRetry && (
          <RetryPreviewButton onRetry={onRetry} />
        )}
      </div>

      {/* Preview */}
      {playable && (
        <LiveClipPreview
          clip={liveClip}
          autoPlay={false}
          className="aspect-[9/16] w-full max-w-md mx-auto"
        />
      )}

      {/* Status Details */}
      <div className="bg-ink/5 rounded-lg p-4 space-y-3">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-ink/60">Status:</span>
            <span className={`font-medium ${
              isReady ? "text-green-400" : 
              isFailed ? "text-red-400" : 
              isRendering ? "text-yellow-400" : 
              "text-ink/90"
            }`}>
              {renderStatus}
            </span>
          </div>
          <div>
            <span className="text-ink/60">Progress:</span>
            <span className="font-medium text-ink/90">
              {isLoading ? `${loadingStageIndex + 1}/3` : isReady ? "3/3" : isFailed ? "Failed" : "0/3"}
            </span>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-3 bg-red-500/10 rounded-lg text-red-100">
            <p className="text-sm font-medium">Error: {error}</p>
          </div>
        )}

        {/* Loading Stages */}
        {isLoading && (
          <div className="mt-4 space-y-2">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                loadingStageIndex >= 0 ? "bg-blue-500" : "bg-ink/20"
              }`} />
              <div className={`w-2 h-2 rounded-full ${
                loadingStageIndex >= 1 ? "bg-blue-500" : "bg-ink/20"
              }`} />
              <div className={`w-2 h-2 rounded-full ${
                loadingStageIndex >= 2 ? "bg-blue-500" : "bg-ink/20"
              }`} />
            </div>
            <div className="text-xs text-ink/60 space-x-4">
              <span className={loadingStageIndex >= 0 ? "text-blue-400" : ""}>Reading source</span>
              <span>-></span>
              <span className={loadingStageIndex >= 1 ? "text-blue-400" : ""}>Finding clips</span>
              <span>-></span>
              <span className={loadingStageIndex >= 2 ? "text-blue-400" : ""}>Preparing outputs</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
