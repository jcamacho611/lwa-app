"use client";

import { useState, useEffect, useCallback } from "react";
import {
  clipStudioEventBridge,
  clipStudioStateManager,
  type ClipStudioEvent,
  type ClipStudioState,
  emitClipUpload,
  emitProcessingStarted,
  emitProgress,
  emitComplete,
  emitError,
} from "../../lib/clip-studio-event-bridge";

export default function ClipStudioEventBridge() {
  const [selectedClipId, setSelectedClipId] = useState<string>("");
  const [events, setEvents] = useState<ClipStudioEvent[]>([]);
  const [states, setStates] = useState<ClipStudioState[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);

  // Subscribe to events
  useEffect(() => {
    const unsubscribeAll = [
      clipStudioEventBridge.on("clip_upload", (event) => {
        setEvents(prev => [...prev.slice(-9), event]);
      }),
      clipStudioEventBridge.on("processing_started", (event) => {
        setEvents(prev => [...prev.slice(-9), event]);
      }),
      clipStudioEventBridge.on("processing_progress", (event) => {
        setEvents(prev => [...prev.slice(-9), event]);
      }),
      clipStudioEventBridge.on("processing_complete", (event) => {
        setEvents(prev => [...prev.slice(-9), event]);
      }),
      clipStudioEventBridge.on("processing_error", (event) => {
        setEvents(prev => [...prev.slice(-9), event]);
      }),
    ];

    return () => {
      unsubscribeAll.forEach(unsubscribe => unsubscribe());
    };
  }, []);

  // Update states periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setStates(clipStudioStateManager.getAllStates());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const simulateUpload = useCallback(() => {
    const clipId = `clip_${Date.now()}`;
    setSelectedClipId(clipId);
    setIsSimulating(true);

    // Simulate upload
    emitClipUpload(clipId, "https://example.com/source.mp4", "user123");

    // Simulate processing stages
    setTimeout(() => emitProcessingStarted(clipId, "upload"), 500);
    setTimeout(() => emitProgress(clipId, 25, "upload"), 1000);
    setTimeout(() => emitProcessingStarted(clipId, "trim"), 1500);
    setTimeout(() => emitProgress(clipId, 50, "trim"), 2000);
    setTimeout(() => emitProcessingStarted(clipId, "effects"), 2500);
    setTimeout(() => emitProgress(clipId, 75, "effects"), 3000);
    setTimeout(() => emitProcessingStarted(clipId, "export"), 3500);
    setTimeout(() => emitProgress(clipId, 90, "export"), 4000);
    setTimeout(() => emitComplete(clipId, "https://example.com/result.mp4", { duration: 30 }), 4500);
    setTimeout(() => setIsSimulating(false), 5000);
  }, []);

  const simulateError = useCallback(() => {
    const clipId = `clip_error_${Date.now()}`;
    setSelectedClipId(clipId);
    setIsSimulating(true);

    emitClipUpload(clipId, "https://example.com/source.mp4", "user123");
    setTimeout(() => emitProcessingStarted(clipId, "upload"), 500);
    setTimeout(() => emitProgress(clipId, 30, "upload"), 1000);
    setTimeout(() => emitError(clipId, "Upload failed: Invalid file format"), 1500);
    setTimeout(() => setIsSimulating(false), 2000);
  }, []);

  const clearAll = useCallback(() => {
    clipStudioEventBridge.clear();
    clipStudioStateManager.clearAllStates();
    setEvents([]);
    setStates([]);
    setSelectedClipId("");
  }, []);

  const getSelectedState = () => {
    return states.find(state => state.clipId === selectedClipId);
  };

  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case "clip_upload": return "text-blue-400";
      case "processing_started": return "text-yellow-400";
      case "processing_progress": return "text-green-400";
      case "processing_complete": return "text-emerald-400";
      case "processing_error": return "text-red-400";
      default: return "text-gray-400";
    }
  };

  return (
    <section className="relative mx-auto max-w-7xl px-6 py-12 text-[#F5F1E8]">
      <div className="max-w-4xl">
        <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">
          Clip Studio Event Bridge
        </p>
        <h2 className="mt-5 text-[clamp(2.4rem,5vw,5rem)] font-black uppercase leading-[0.92] tracking-normal text-white">
          Real-time event processing for clip studio operations.
        </h2>
        <p className="mt-6 text-base leading-8 text-white/62">
          This bridge connects frontend clip studio interactions to the backend generation pipeline,
          enabling real-time progress tracking and state synchronization.
        </p>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[minmax(0,0.6fr)_minmax(0,1.4fr)]">
        {/* Control Panel */}
        <section className="rounded-[28px] border border-white/10 bg-black/35 p-6 shadow-[0_28px_90px_-60px_rgba(126,58,242,0.9)]">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
            Event Simulation
          </p>

          <div className="mt-5 space-y-4">
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Clip ID
              </label>
              <input
                type="text"
                value={selectedClipId}
                onChange={(e) => setSelectedClipId(e.target.value)}
                placeholder="Enter clip ID..."
                className="w-full rounded-lg border border-white/10 bg-white/[0.05] px-3 py-2 text-white placeholder-white/40 focus:border-[#C9A24A]/40 focus:outline-none"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={simulateUpload}
                disabled={isSimulating}
                className="rounded-full border border-[#C9A24A]/40 bg-[#C9A24A]/15 px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#C9A24A]/25 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Simulate Upload
              </button>
              <button
                onClick={simulateError}
                disabled={isSimulating}
                className="rounded-full border border-red-400/40 bg-red-400/15 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-400/25 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Simulate Error
              </button>
              <button
                onClick={clearAll}
                className="rounded-full border border-white/10 bg-white/[0.05] px-4 py-2 text-sm font-semibold text-white/70 transition hover:border-white/20 hover:bg-white/[0.1]"
              >
                Clear All
              </button>
            </div>
          </div>

          {/* Current State */}
          {selectedClipId && (
            <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/35 mb-3">
                Current State
              </p>
              {(() => {
                const state = getSelectedState();
                if (!state) {
                  return <p className="text-sm text-white/50">No state found</p>;
                }
                return (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-white/60">Status:</span>
                      <span className={`font-medium ${
                        state.status === "completed" ? "text-emerald-400" :
                        state.status === "error" ? "text-red-400" :
                        state.status === "processing" ? "text-yellow-400" :
                        "text-blue-400"
                      }`}>
                        {state.status}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/60">Progress:</span>
                      <span className="font-medium text-white">{state.progress}%</span>
                    </div>
                    {state.stage && (
                      <div className="flex justify-between">
                        <span className="text-white/60">Stage:</span>
                        <span className="font-medium text-white">{state.stage}</span>
                      </div>
                    )}
                    {state.resultUrl && (
                      <div className="mt-2">
                        <span className="text-white/60">Result:</span>
                        <a
                          href={state.resultUrl}
                          className="ml-2 text-blue-400 hover:text-blue-300 underline"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          View Result
                        </a>
                      </div>
                    )}
                    {state.error && (
                      <div className="mt-2">
                        <span className="text-red-400">Error: {state.error}</span>
                      </div>
                    )}
                  </div>
                );
              })()}
            </div>
          )}
        </section>

        {/* Events Log */}
        <section className="rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
            Events Log
          </p>

          <div className="mt-5 max-h-96 overflow-y-auto space-y-2">
            {events.length === 0 ? (
              <p className="text-sm text-white/50">No events yet. Click &quot;Simulate Upload&quot; to start.</p>
            ) : (
              events.map((event, _index) => (
                <div
                  key={event.id}
                  className="rounded-lg border border-white/10 bg-black/25 p-3 text-sm"
                >
                  <div className="flex items-center justify-between">
                    <span className={`font-mono ${getEventColor(event.type)}`}>
                      {event.type}
                    </span>
                    <span className="text-white/40 text-xs">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="mt-1 text-white/60">
                    Clip: {event.clipId}
                  </div>
                  {event.payload.stage && (
                    <div className="text-white/60">
                      Stage: {event.payload.stage}
                    </div>
                  )}
                  {event.payload.progress !== undefined && (
                    <div className="text-white/60">
                      Progress: {event.payload.progress}%
                    </div>
                  )}
                  {event.payload.error && (
                    <div className="text-red-400">
                      Error: {event.payload.error}
                    </div>
                  )}
                  {event.payload.resultUrl && (
                    <div className="text-blue-400">
                      Result: {event.payload.resultUrl}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      {/* All States */}
      {states.length > 0 && (
        <section className="mt-8 rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
            All Clip States
          </p>

          <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {states.map((state) => (
              <div
                key={state.clipId}
                className="rounded-lg border border-white/10 bg-black/25 p-4 text-sm"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-white/80 text-xs">
                    {state.clipId}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    state.status === "completed" ? "bg-emerald-400/20 text-emerald-300" :
                    state.status === "error" ? "bg-red-400/20 text-red-300" :
                    state.status === "processing" ? "bg-yellow-400/20 text-yellow-300" :
                    "bg-blue-400/20 text-blue-300"
                  }`}>
                    {state.status}
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-white/60">Progress:</span>
                    <span className="text-white">{state.progress}%</span>
                  </div>
                  {state.stage && (
                    <div className="flex justify-between">
                      <span className="text-white/60">Stage:</span>
                      <span className="text-white">{state.stage}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-white/60">Events:</span>
                    <span className="text-white">{state.events.length}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </section>
  );
}
