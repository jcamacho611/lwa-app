"use client";

import { useState } from "react";
import {
  useLwaEvents,
  createClipGeneratedEvent,
  createClipSavedEvent,
  createProofSavedEvent,
  createCampaignExportedEvent,
  createLeeWuhAssetSelectedEvent,
  createRecoveryActionSelectedEvent,
  createSignalSprintCompletedEvent,
} from "../../lib/lwa-event-bridge";

export default function LwaEventBridgePanel() {
  const { events, summary, emit, clear, cleanup } = useLwaEvents();

  const [selectedEventId, setSelectedEventId] = useState<string>("");
  const [isSimulating, setIsSimulating] = useState(false);

  // Simulate different types of events
  const simulateClipGeneration = () => {
    setIsSimulating(true);
    emit(createClipGeneratedEvent({
      clipId: `clip_${Date.now()}`,
      url: "https://cdn.example.com/demo.mp4",
      duration: 30,
      metadata: { platform: "tiktok", quality: "high" },
    }, "creator_engine"));
    
    setTimeout(() => setIsSimulating(false), 1000);
  };

  const simulateClipSave = () => {
    setIsSimulating(true);
    emit(createClipSavedEvent({
      clipId: `clip_${Date.now()}`,
      userId: "user_123",
      location: "/user/clips",
    }, "clip_studio"));
    
    setTimeout(() => setIsSimulating(false), 800);
  };

  const simulateProofSave = () => {
    setIsSimulating(true);
    emit(createProofSavedEvent({
      proofId: `proof_${Date.now()}`,
      type: "clip",
      userId: "user_123",
    }, "proof_engine"));
    
    setTimeout(() => setIsSimulating(false), 600);
  };

  const simulateCampaignExport = () => {
    setIsSimulating(true);
    emit(createCampaignExportedEvent({
      campaignId: `campaign_${Date.now()}`,
      format: "csv",
      userId: "user_123",
    }, "marketplace_engine"));
    
    setTimeout(() => setIsSimulating(false), 1200);
  };

  const simulateAssetSelection = () => {
    setIsSimulating(true);
    emit(createLeeWuhAssetSelectedEvent({
      assetId: `asset_${Date.now()}`,
      assetType: "character",
      realm: "genesis_realm",
    }, "world_engine"));
    
    setTimeout(() => setIsSimulating(false), 400);
  };

  const simulateRecoveryAction = () => {
    setIsSimulating(true);
    emit(createRecoveryActionSelectedEvent({
      action: "restore_backup",
      targetId: "backup_123",
      outcome: "success",
    }, "recovery_engine"));
    
    setTimeout(() => setIsSimulating(false), 700);
  };

  const simulateSignalSprint = () => {
    setIsSimulating(true);
    emit(createSignalSprintCompletedEvent({
      sprintId: `sprint_${Date.now()}`,
      score: 850,
      rank: 3,
      userId: "user_123",
    }, "world_engine"));
    
    setTimeout(() => setIsSimulating(false), 900);
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case "clip_generated": return "🎬";
      case "clip_saved": return "💾";
      case "proof_saved": return "📋";
      case "campaign_exported": return "📊";
      case "lee_wuh_asset_selected": return "⚔️";
      case "recovery_action_selected": return "🔄";
      case "signal_sprint_completed": return "🏁";
      default: return "📝";
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case "clip_generated": return "text-blue-400";
      case "clip_saved": return "text-green-400";
      case "proof_saved": return "text-purple-400";
      case "campaign_exported": return "text-orange-400";
      case "lee_wuh_asset_selected": return "text-yellow-400";
      case "recovery_action_selected": return "text-pink-400";
      case "signal_sprint_completed": return "text-emerald-400";
      default: return "text-gray-400";
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const selectedEvent = events.find(event => event.id === selectedEventId);

  return (
    <section className="relative mx-auto max-w-7xl px-6 py-12 text-[#F5F1E8]">
      <div className="max-w-4xl">
        <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">
          LWA Event Bridge
        </p>
        <h2 className="mt-5 text-[clamp(2.4rem,5vw,5rem)] font-black uppercase leading-[0.92] tracking-normal text-white">
          Real-time event coordination without backend dependency.
        </h2>
        <p className="mt-6 text-base leading-8 text-white/62">
          This bridge allows Clip Studio and Lee-Wuh systems to emit typed local events,
          enabling real-time coordination between different parts of LWA while maintaining
          type safety and avoiding backend coupling.
        </p>
      </div>

      {/* Event Summary */}
      <div className="mt-8 grid gap-6 md:grid-cols-4">
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">Total Events</p>
          <p className="mt-2 text-3xl font-black text-white">{summary.total}</p>
        </div>
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">Last Hour</p>
          <p className="mt-2 text-3xl font-black text-white">{summary.recent.lastHour}</p>
        </div>
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">Last Day</p>
          <p className="mt-2 text-3xl font-black text-white">{summary.recent.lastDay}</p>
        </div>
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">Queue Size</p>
          <p className="mt-2 text-3xl font-black text-white">{events.length}</p>
        </div>
      </div>

      {/* Event Type Breakdown */}
      <div className="mt-8 rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
          Event Types
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-3">
          {Object.entries(summary.byType).map(([type, count]) => (
            <div key={type} className="flex items-center justify-between rounded-lg border border-white/10 bg-black/25 p-3">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getEventIcon(type)}</span>
                <div>
                  <p className="font-medium text-white">{type.replace(/_/g, " ")}</p>
                  <p className="text-xs text-white/60">{count} events</p>
                </div>
              </div>
              <span className="text-xs text-white/40">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Event Source Breakdown */}
      <div className="mt-8 rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
          Event Sources
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {Object.entries(summary.bySource).map(([source, count]) => (
            <div key={source} className="flex items-center justify-between rounded-lg border border-white/10 bg-black/25 p-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded bg-white/10 flex items-center justify-center text-sm font-mono">
                  {source.substring(0, 2).toUpperCase()}
                </div>
                <div>
                  <p className="font-medium text-white capitalize">{source}</p>
                  <p className="text-xs text-white/60">{count} events</p>
                </div>
              </div>
              <span className="text-xs text-white/40">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Control Panel */}
      <div className="mt-8 rounded-[28px] border border-white/10 bg-black/35 p-6 shadow-[0_28px_90px_-60px_rgba(126,58,242,0.9)]">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
          Event Simulation
        </p>
        
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <button
            onClick={simulateClipGeneration}
            disabled={isSimulating}
            className="rounded-lg border border-blue-400/40 bg-blue-400/15 px-4 py-3 text-sm font-medium text-blue-300 transition hover:bg-blue-400/25 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Generate Clip Event
          </button>
          
          <button
            onClick={simulateClipSave}
            disabled={isSimulating}
            className="rounded-lg border border-green-400/40 bg-green-400/15 px-4 py-3 text-sm font-medium text-green-300 transition hover:bg-green-400/25 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Save Clip Event
          </button>
          
          <button
            onClick={simulateProofSave}
            disabled={isSimulating}
            className="rounded-lg border border-purple-400/40 bg-purple-400/15 px-4 py-3 text-sm font-medium text-purple-300 transition hover:bg-purple-400/25 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Save Proof Event
          </button>
          
          <button
            onClick={simulateCampaignExport}
            disabled={isSimulating}
            className="rounded-lg border border-orange-400/40 bg-orange-400/15 px-4 py-3 text-sm font-medium text-orange-300 transition hover:bg-orange-400/25 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Export Campaign Event
          </button>
          
          <button
            onClick={simulateAssetSelection}
            disabled={isSimulating}
            className="rounded-lg border border-yellow-400/40 bg-yellow-400/15 px-4 py-3 text-sm font-medium text-yellow-300 transition hover:bg-yellow-400/25 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Select Asset Event
          </button>
          
          <button
            onClick={simulateRecoveryAction}
            disabled={isSimulating}
            className="rounded-lg border border-pink-400/40 bg-pink-400/15 px-4 py-3 text-sm font-medium text-pink-300 transition hover:bg-pink-400/25 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Recovery Action Event
          </button>
          
          <button
            onClick={simulateSignalSprint}
            disabled={isSimulating}
            className="rounded-lg border border-emerald-400/40 bg-emerald-400/15 px-4 py-3 text-sm font-medium text-emerald-300 transition hover:bg-emerald-400/25 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Complete Sprint Event
          </button>
        </div>

        <div className="mt-6 flex gap-4">
          <button
            onClick={() => clear()}
            className="rounded-full border border-white/20 bg-white/[0.05] px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/[0.1]"
          >
            Clear All Events
          </button>
          
          <button
            onClick={() => cleanup()}
            className="rounded-full border border-white/20 bg-white/[0.05] px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/[0.1]"
          >
            Cleanup Expired Events
          </button>
        </div>
      </div>

      {/* Recent Events */}
      <div className="mt-8 rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
          Recent Events
        </p>

        <div className="mt-5 max-h-96 overflow-y-auto space-y-2">
          {events.length === 0 ? (
            <p className="text-sm text-white/50">No events yet. Click simulation buttons to start.</p>
          ) : (
            events.slice(0, 20).map((event) => (
              <div
                key={event.id}
                onClick={() => setSelectedEventId(event.id)}
                className={`rounded-lg border p-4 cursor-pointer transition ${
                  selectedEventId === event.id
                    ? "border-[#C9A24A]/40 bg-[#C9A24A]/10"
                    : "border-white/10 bg-black/25 hover:border-white/20"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`text-2xl ${getEventColor(event.type)}`}>
                      {getEventIcon(event.type)}
                    </span>
                    <div>
                      <p className="font-medium text-white capitalize">{event.type.replace(/_/g, " ")}</p>
                      <p className="text-xs text-white/60">
                        {formatTimestamp(event.timestamp)}
                      </p>
                    </div>
                  </div>
                  <div className="text-xs text-white/40">
                    {event.source}
                  </div>
                </div>
                
                {selectedEventId === event.id && (
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <p className="text-xs text-white/60 mb-2">Event Details:</p>
                    <div className="bg-black/50 rounded p-3 text-xs">
                      <pre className="text-white/80 overflow-x-auto">
                        {JSON.stringify(event.data, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  );
}
