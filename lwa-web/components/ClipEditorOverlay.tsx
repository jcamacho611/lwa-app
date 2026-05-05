"use client";

interface Segment {
  start: number; // 0-1 (percentage of video)
  end: number;   // 0-1
  type: "kept" | "removed" | "suggested";
}

interface ClipEditorOverlayProps {
  segments: Segment[];
  duration: number; // in seconds
  currentTime?: number;
  onSegmentClick?: (_segment: Segment, _index: number) => void;
}

const typeColors = {
  kept: "bg-green-500",
  removed: "bg-red-500",
  suggested: "bg-[#C9A24A]",
};

const typeLabels = {
  kept: "Kept",
  removed: "Removed",
  suggested: "Suggested",
};

export default function ClipEditorOverlay({
  segments,
  duration,
  currentTime = 0,
  onSegmentClick,
}: ClipEditorOverlayProps) {
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="w-full">
      {/* Timeline Bar */}
      <div className="relative w-full h-12 bg-[#1a1a1a] rounded-lg overflow-hidden">
        {/* Segments */}
        {segments.map((segment, index) => {
          const left = segment.start * 100;
          const width = (segment.end - segment.start) * 100;

          return (
            <button
              key={index}
              onClick={() => onSegmentClick?.(segment, index)}
              className={`absolute top-0 h-full ${typeColors[segment.type]} hover:opacity-80 transition-opacity cursor-pointer border-r border-[#0a0a0a]`}
              style={{
                left: `${left}%`,
                width: `${width}%`,
              }}
              title={`${typeLabels[segment.type]}: ${formatTime(segment.start * duration)} - ${formatTime(segment.end * duration)}`}
            />
          );
        })}

        {/* Current Time Indicator */}
        <div
          className="absolute top-0 w-0.5 h-full bg-white z-10 pointer-events-none"
          style={{ left: `${(currentTime / duration) * 100}%` }}
        >
          <div className="absolute -top-1 -left-1 w-2.5 h-2.5 bg-white rounded-full" />
        </div>
      </div>

      {/* Time Scale */}
      <div className="flex justify-between mt-2 text-xs text-white/50">
        <span>{formatTime(0)}</span>
        <span>{formatTime(duration / 2)}</span>
        <span>{formatTime(duration)}</span>
      </div>

      {/* Legend */}
      <div className="flex gap-4 mt-3">
        {(Object.keys(typeColors) as Array<keyof typeof typeColors>).map((type) => (
          <div key={type} className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded ${typeColors[type]}`} />
            <span className="text-xs text-white/70">{typeLabels[type]}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
