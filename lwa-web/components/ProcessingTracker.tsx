"use client";

interface ProcessingTrackerProps {
  stage: "ingest" | "cutting" | "analyzing" | "complete" | "error";
  progress: number; // 0-100
  clipsReady: number;
  totalClips: number;
}

const stages = [
  { key: "ingest", label: "Ingesting", description: "Downloading source video" },
  { key: "cutting", label: "Cutting", description: "Removing silence, detecting scenes" },
  { key: "analyzing", label: "Analyzing", description: "Ranking clips, generating hooks" },
  { key: "complete", label: "Complete", description: "Clip pack ready" },
] as const;

export default function ProcessingTracker({
  stage,
  progress,
  clipsReady,
  totalClips,
}: ProcessingTrackerProps) {
  const currentStageIndex = stages.findIndex((s) => s.key === stage);

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-[#0a0a0a] border border-[#1a1a1a] rounded-xl">
      <h3 className="text-lg font-semibold text-white mb-4">Processing Status</h3>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-white/70 mb-2">
          <span>Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="h-2 bg-[#1a1a1a] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#C9A24A] transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Stage Indicators */}
      <div className="space-y-3">
        {stages.map((s, index) => {
          const isComplete = index < currentStageIndex;
          const isCurrent = index === currentStageIndex;
          const _isPending = index > currentStageIndex;

          return (
            <div
              key={s.key}
              className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                isCurrent ? "bg-[#1a1a1a] border border-[#C9A24A]/30" : ""
              }`}
            >
              {/* Status Icon */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                  isComplete
                    ? "bg-green-500/20 text-green-400"
                    : isCurrent
                    ? "bg-[#C9A24A]/20 text-[#C9A24A] animate-pulse"
                    : "bg-[#1a1a1a] text-white/40"
                }`}
              >
                {isComplete ? (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  index + 1
                )}
              </div>

              {/* Stage Info */}
              <div className="flex-1">
                <p
                  className={`font-medium ${
                    isCurrent ? "text-white" : isComplete ? "text-white/80" : "text-white/40"
                  }`}
                >
                  {s.label}
                </p>
                <p className="text-sm text-white/50">{s.description}</p>
              </div>

              {/* Clip Counter for Cutting Stage */}
              {s.key === "cutting" && totalClips > 0 && (
                <div className="text-sm text-white/60">
                  {clipsReady}/{totalClips} clips
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Current Action */}
      {stage !== "complete" && stage !== "error" && (
        <div className="mt-4 p-3 bg-[#C9A24A]/10 border border-[#C9A24A]/20 rounded-lg">
          <p className="text-sm text-[#C9A24A]">
            {stage === "ingest" && "Downloading video from source..."}
            {stage === "cutting" && "Detecting scenes and removing silence..."}
            {stage === "analyzing" && "Ranking clips and generating metadata..."}
          </p>
        </div>
      )}

      {/* Complete State */}
      {stage === "complete" && (
        <div className="mt-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
          <p className="text-sm text-green-400">
            All done! {totalClips} clips ready for review.
          </p>
        </div>
      )}
    </div>
  );
}
