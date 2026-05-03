"use client";

import { useState } from "react";

interface TimelineEvent {
  id: string;
  timestamp: number;
  type: string;
  label: string;
  description: string;
  ai_score?: number;
}

interface SourceTrack {
  id: string;
  name: string;
  events: TimelineEvent[];
  color: string;
}

const mockTracks: SourceTrack[] = [
  {
    id: "track_moments",
    name: "Key Moments",
    color: "#C9A24A",
    events: [
      { id: "evt_001", timestamp: 45, type: "hook", label: "Strong Hook", description: "Opening statement captures attention", ai_score: 0.92 },
      { id: "evt_002", timestamp: 180, type: "moment", label: "Viral Moment", description: "High engagement potential", ai_score: 0.88 },
      { id: "evt_003", timestamp: 340, type: "cta", label: "Call-to-Action", description: "Clear viewer direction", ai_score: 0.85 },
    ],
  },
  {
    id: "track_captions",
    name: "Captions",
    color: "#6D3BFF",
    events: [
      { id: "cap_001", timestamp: 45, type: "caption", label: "Caption Start", description: "First caption block" },
      { id: "cap_002", timestamp: 120, type: "caption", label: "Caption Block 2", description: "Continuation" },
      { id: "cap_003", timestamp: 240, type: "caption", label: "Caption Block 3", description: "Mid-point" },
      { id: "cap_004", timestamp: 340, type: "caption", label: "Final Caption", description: "Closing text" },
    ],
  },
  {
    id: "track_audio",
    name: "Audio Peaks",
    color: "#00D9FF",
    events: [
      { id: "aud_001", timestamp: 45, type: "peak", label: "Volume Peak", description: "High engagement audio" },
      { id: "aud_002", timestamp: 180, type: "peak", label: "Volume Peak", description: "Emphasis moment" },
    ],
  },
];

export function SourceTimelinePanel() {
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const totalDuration = 360; // 6 minutes

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#6D3BFF]/20 text-3xl">
            📁
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white">Source Timeline</h3>
            <p className="text-sm text-white/50">Visualize key moments, captions, and audio peaks</p>
          </div>
          <div className="flex gap-4 text-right">
            <div>
              <div className="text-sm text-white/50">Duration</div>
              <div className="text-xl font-bold text-[#6D3BFF]">6:00</div>
            </div>
            <div>
              <div className="text-sm text-white/50">Moments</div>
              <div className="text-xl font-bold text-[#6D3BFF]">8</div>
            </div>
          </div>
        </div>
      </div>

      {/* Video Preview Placeholder */}
      <div className="relative aspect-video rounded-2xl border border-white/10 bg-black/40">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="mb-2 text-4xl">🎬</div>
            <p className="text-white/50">Video Preview</p>
            <p className="text-sm text-white/30">Timeline visualization below</p>
          </div>
        </div>

        {/* Playhead */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-[#C9A24A]"
          style={{ left: `${(currentTime / totalDuration) * 100}%` }}
        >
          <div className="absolute -top-1 -left-1.5 h-3 w-3 rounded-full bg-[#C9A24A]" />
        </div>
      </div>

      {/* Timeline */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
        <h4 className="mb-4 font-medium text-white">Timeline Tracks</h4>

        {/* Time ruler */}
        <div className="mb-4 flex justify-between border-b border-white/10 pb-2 text-xs text-white/30">
          {[0, 60, 120, 180, 240, 300, 360].map((t) => (
            <span key={t}>{formatTime(t)}</span>
          ))}
        </div>

        {/* Tracks */}
        <div className="space-y-4">
          {mockTracks.map((track) => (
            <div key={track.id}>
              <div className="mb-2 flex items-center gap-2">
                <div className="h-3 w-3 rounded-full" style={{ backgroundColor: track.color }} />
                <span className="text-sm text-white/70">{track.name}</span>
              </div>

              <div className="relative h-12 rounded-lg bg-white/[0.02]">
                {/* Track background markers */}
                <div className="absolute inset-0 flex">
                  {[0, 1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="flex-1 border-r border-white/5" />
                  ))}
                </div>

                {/* Events */}
                {track.events.map((event) => (
                  <button
                    key={event.id}
                    onClick={() => setSelectedEvent(selectedEvent === event.id ? null : event.id)}
                    className={`absolute top-1 bottom-1 rounded px-2 py-1 text-xs transition-all ${
                      selectedEvent === event.id
                        ? "ring-2 ring-white/30"
                        : "hover:opacity-80"
                    }`}
                    style={{
                      left: `${(event.timestamp / totalDuration) * 100}%`,
                      width: "80px",
                      backgroundColor: track.color + "40",
                      borderLeft: `3px solid ${track.color}`,
                    }}
                  >
                    <div className="truncate font-medium text-white">{event.label}</div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Scrubber */}
        <div className="mt-6">
          <input
            type="range"
            min="0"
            max={totalDuration}
            value={currentTime}
            onChange={(e) => setCurrentTime(Number(e.target.value))}
            className="w-full accent-[#C9A24A]"
          />
          <div className="mt-2 text-center text-sm text-white/50">{formatTime(currentTime)}</div>
        </div>
      </div>

      {/* Event Details */}
      {selectedEvent && (
        <div className="rounded-2xl border border-[#C9A24A]/30 bg-[#C9A24A]/10 p-5">
          {mockTracks.flatMap((t) => t.events)
            .filter((e) => e.id === selectedEvent)
            .map((event) => (
              <div key={event.id}>
                <div className="mb-2 flex items-center justify-between">
                  <h4 className="font-medium text-white">{event.label}</h4>
                  <span className="text-sm text-white/50">{formatTime(event.timestamp)}</span>
                </div>
                <p className="mb-3 text-sm text-white/70">{event.description}</p>
                {event.ai_score && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-white/50">AI Score:</span>
                    <span className="font-medium text-[#E9C77B]">{(event.ai_score * 100).toFixed(0)}%</span>
                  </div>
                )}
                <div className="mt-4 flex gap-2">
                  <button className="rounded-lg bg-[#C9A24A] px-3 py-2 text-sm font-medium text-black transition hover:bg-[#E9C77B]">
                    Preview
                  </button>
                  <button className="rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-white transition hover:bg-white/[0.08]">
                    Use in Clip
                  </button>
                </div>
              </div>
            ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        <button className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
          Add Marker
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Export Timeline
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Auto-Detect Moments
        </button>
      </div>
    </div>
  );
}
