"use client";

import { useState } from "react";

interface CreativeEngine {
  id: string;
  name: string;
  description: string;
  status: "active" | "beta" | "development";
  version: string;
  capabilities: string[];
  processing_time_avg: number;
  success_rate: number;
}

const mockEngines: CreativeEngine[] = [
  {
    id: "engine_clip_core",
    name: "Clip Core Engine",
    description: "Primary AI engine for video analysis and moment detection",
    status: "active",
    version: "2.4.1",
    capabilities: ["video_analysis", "moment_detection", "ranking", "trimming"],
    processing_time_avg: 45.5,
    success_rate: 0.94,
  },
  {
    id: "engine_hook_writer",
    name: "Hook Writer Pro",
    description: "Generates compelling opening lines and video hooks",
    status: "active",
    version: "1.8.2",
    capabilities: ["hook_generation", "tone_adaptation", "platform_optimization", "a_b_variants"],
    processing_time_avg: 3.2,
    success_rate: 0.89,
  },
  {
    id: "engine_caption_pro",
    name: "Caption Pro",
    description: "Advanced caption generation with timing and style optimization",
    status: "beta",
    version: "1.3.0",
    capabilities: ["transcription", "timing", "style_variants", "burn_in_ready"],
    processing_time_avg: 12.8,
    success_rate: 0.92,
  },
  {
    id: "engine_thumbnail_text",
    name: "Thumbnail Text Master",
    description: "Generates scroll-stopping thumbnail text overlays",
    status: "beta",
    version: "1.2.1",
    capabilities: ["text_generation", "font_pairing", "color_suggestions", "layout_hints"],
    processing_time_avg: 2.1,
    success_rate: 0.87,
  },
  {
    id: "engine_campaign_packager",
    name: "Campaign Packager",
    description: "Bundles clips, hooks, captions into complete campaign exports",
    status: "active",
    version: "2.1.0",
    capabilities: ["bundle_creation", "format_conversion", "metadata_tagging", "delivery_optimization"],
    processing_time_avg: 28.5,
    success_rate: 0.96,
  },
];

export function CreativeEnginesPanel() {
  const [selectedEngine, setSelectedEngine] = useState<string>("engine_clip_core");
  const [activeTab, setActiveTab] = useState<"engines" | "jobs" | "stats">("engines");

  const engine = mockEngines.find((e) => e.id === selectedEngine);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#FF6B35]/20 text-3xl">
            🎨
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white">Creative Engines</h3>
            <p className="text-sm text-white/50">AI-powered creative automation tools</p>
          </div>
          <div className="flex gap-4 text-right">
            <div>
              <div className="text-sm text-white/50">Active</div>
              <div className="text-xl font-bold text-green-400">3</div>
            </div>
            <div>
              <div className="text-sm text-white/50">Beta</div>
              <div className="text-xl font-bold text-yellow-400">2</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: "engines", label: "Engines", icon: "⚙️" },
          { id: "jobs", label: "Jobs", icon: "📋" },
          { id: "stats", label: "Stats", icon: "📊" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all ${
              activeTab === tab.id
                ? "bg-[#C9A24A] text-black"
                : "border border-white/10 bg-white/[0.04] text-white/70 hover:bg-white/[0.08]"
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Engines Tab */}
      {activeTab === "engines" && (
        <div className="grid gap-4 lg:grid-cols-[1fr_300px]">
          {/* Engine List */}
          <div className="space-y-3">
            {mockEngines.map((eng) => (
              <button
                key={eng.id}
                onClick={() => setSelectedEngine(eng.id)}
                className={`w-full rounded-2xl border p-4 text-left transition ${
                  selectedEngine === eng.id
                    ? "border-[#C9A24A] bg-[#C9A24A]/10"
                    : "border-white/10 bg-white/[0.04] hover:bg-white/[0.08]"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="mb-1 flex items-center gap-2">
                      <h4 className="font-medium text-white">{eng.name}</h4>
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs ${
                          eng.status === "active"
                            ? "bg-green-400/20 text-green-400"
                            : eng.status === "beta"
                            ? "bg-yellow-400/20 text-yellow-400"
                            : "bg-white/10 text-white/50"
                        }`}
                      >
                        {eng.status}
                      </span>
                    </div>
                    <p className="text-sm text-white/50">{eng.description}</p>
                  </div>
                  <span className="text-xs text-white/30">v{eng.version}</span>
                </div>

                <div className="mt-3 flex flex-wrap gap-1">
                  {eng.capabilities.slice(0, 3).map((cap) => (
                    <span
                      key={cap}
                      className="rounded-full bg-white/[0.04] px-2 py-0.5 text-xs capitalize text-white/40"
                    >
                      {cap.replace("_", " ")}
                    </span>
                  ))}
                </div>
              </button>
            ))}
          </div>

          {/* Engine Details Sidebar */}
          {engine && (
            <div className="space-y-4">
              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
                <h4 className="mb-4 font-medium text-white">{engine.name}</h4>

                <div className="mb-4 space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/50">Version</span>
                    <span className="text-white">{engine.version}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/50">Status</span>
                    <span
                      className={`capitalize ${
                        engine.status === "active"
                          ? "text-green-400"
                          : engine.status === "beta"
                          ? "text-yellow-400"
                          : "text-white/50"
                      }`}
                    >
                      {engine.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/50">Avg Processing</span>
                    <span className="text-white">{engine.processing_time_avg}s</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/50">Success Rate</span>
                    <span className="text-[#E9C77B]">{(engine.success_rate * 100).toFixed(0)}%</span>
                  </div>
                </div>

                <h5 className="mb-2 text-sm font-medium text-white">Capabilities</h5>
                <div className="flex flex-wrap gap-1">
                  {engine.capabilities.map((cap) => (
                    <span
                      key={cap}
                      className="rounded-full bg-white/[0.04] px-2 py-1 text-xs capitalize text-white/50"
                    >
                      {cap.replace("_", " ")}
                    </span>
                  ))}
                </div>
              </div>

              <button className="w-full rounded-xl bg-[#C9A24A] py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
                Run Engine
              </button>
            </div>
          )}
        </div>
      )}

      {/* Jobs Tab */}
      {activeTab === "jobs" && (
        <div className="space-y-4">
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-4 font-medium text-white">Recent Jobs</h4>
            <div className="space-y-3">
              {[
                { engine: "Clip Core Engine", status: "completed", time: "2 min ago", video: "Tutorial #3" },
                { engine: "Hook Writer Pro", status: "processing", time: "5 min ago", video: "Podcast #42" },
                { engine: "Caption Pro", status: "completed", time: "15 min ago", video: "Demo Reel" },
                { engine: "Thumbnail Text Master", status: "queued", time: "Just now", video: "Viral Clip #1" },
              ].map((job, idx) => (
                <div key={idx} className="flex items-center justify-between rounded-xl bg-white/[0.02] p-3">
                  <div>
                    <div className="text-sm text-white">{job.engine}</div>
                    <div className="text-xs text-white/30">{job.video}</div>
                  </div>
                  <div className="text-right">
                    <span
                      className={`rounded-full px-2 py-1 text-xs ${
                        job.status === "completed"
                          ? "bg-green-400/20 text-green-400"
                          : job.status === "processing"
                          ? "bg-yellow-400/20 text-yellow-400"
                          : "bg-white/10 text-white/50"
                      }`}
                    >
                      {job.status}
                    </span>
                    <div className="mt-1 text-xs text-white/30">{job.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Stats Tab */}
      {activeTab === "stats" && (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "Total Jobs", value: "1,247", change: "+12%" },
              { label: "Avg Success Rate", value: "91.6%", change: "+2.3%" },
              { label: "Active Engines", value: "5", change: "+1" },
              { label: "Total Processing Time", value: "92.1 min", change: "-8%" },
            ].map((stat) => (
              <div key={stat.label} className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 text-center">
                <div className="text-2xl font-bold text-white">{stat.value}</div>
                <div className="text-sm text-white/50">{stat.label}</div>
                <div className="mt-1 text-xs text-green-400">{stat.change}</div>
              </div>
            ))}
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-4 font-medium text-white">Engine Performance</h4>
            <div className="space-y-4">
              {mockEngines.map((eng) => (
                <div key={eng.id}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="text-white/70">{eng.name}</span>
                    <span className="text-[#E9C77B]">{(eng.success_rate * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/10">
                    <div
                      className="h-full rounded-full bg-[#C9A24A]"
                      style={{ width: `${eng.success_rate * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        <button className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
          Run All Engines
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Batch Processing
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Engine Logs
        </button>
      </div>
    </div>
  );
}
