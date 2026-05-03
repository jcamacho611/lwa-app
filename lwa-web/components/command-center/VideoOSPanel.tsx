"use client";

import { useState } from "react";

interface VideoJob {
  id: string;
  title: string;
  status: string;
  progress: number;
  duration: number;
  platform: string;
  created_at: string;
}

interface VideoSource {
  id: string;
  url: string;
  status: string;
  duration: number;
  processed: boolean;
}

const mockJobs: VideoJob[] = [
  { id: "job_001", title: "Podcast Episode #42", status: "processing", progress: 65, duration: 3600, platform: "youtube", created_at: "2025-05-03T10:00:00Z" },
  { id: "job_002", title: "Tutorial Series #3", status: "completed", progress: 100, duration: 1800, platform: "tiktok", created_at: "2025-05-03T09:30:00Z" },
  { id: "job_003", title: "Product Demo v2", status: "queued", progress: 0, duration: 900, platform: "instagram", created_at: "2025-05-03T11:00:00Z" },
];

const mockSources: VideoSource[] = [
  { id: "src_001", url: "https://youtube.com/watch?v=abc123", status: "ready", duration: 3600, processed: true },
  { id: "src_002", url: "https://tiktok.com/@user/video/456", status: "downloading", duration: 0, processed: false },
  { id: "src_003", url: "https://twitch.tv/videos/789", status: "ready", duration: 7200, processed: true },
];

export function VideoOSPanel() {
  const [activeTab, setActiveTab] = useState<"jobs" | "sources" | "analytics">("jobs");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#FF6B35]/20 text-3xl">
            🎬
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white">Video OS</h3>
            <p className="text-sm text-white/50">Video processing and analysis pipeline</p>
          </div>
          <div className="flex gap-4 text-right">
            <div>
              <div className="text-sm text-white/50">Processing</div>
              <div className="text-xl font-bold text-yellow-400">1</div>
            </div>
            <div>
              <div className="text-sm text-white/50">Completed</div>
              <div className="text-xl font-bold text-green-400">247</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: "jobs", label: "Jobs", icon: "📋" },
          { id: "sources", label: "Sources", icon: "📁" },
          { id: "analytics", label: "Analytics", icon: "📊" },
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

      {/* Jobs Tab */}
      {activeTab === "jobs" && (
        <div className="space-y-4">
          {mockJobs.map((job) => (
            <div key={job.id} className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
              <div className="flex items-start justify-between">
                <div>
                  <div className="mb-1 flex items-center gap-2">
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
                    <span className="text-xs capitalize text-white/30">{job.platform}</span>
                  </div>
                  <h4 className="font-medium text-white">{job.title}</h4>
                </div>
                <div className="text-right">
                  <div className="text-sm text-white/50">{Math.floor(job.duration / 60)}m {job.duration % 60}s</div>
                </div>
              </div>

              {job.status === "processing" && (
                <div className="mt-4">
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="text-white/50">Processing...</span>
                    <span className="text-[#E9C77B]">{job.progress}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/10">
                    <div className="h-full rounded-full bg-[#C9A24A]" style={{ width: `${job.progress}%` }} />
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Sources Tab */}
      {activeTab === "sources" && (
        <div className="space-y-4">
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-4 font-medium text-white">Add Source</h4>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Paste YouTube, TikTok, Twitch URL..."
                className="flex-1 rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-white outline-none placeholder:text-white/30"
              />
              <button className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
                Add
              </button>
            </div>
          </div>

          <div className="space-y-3">
            {mockSources.map((source) => (
              <div key={source.id} className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1 truncate">
                    <div className="text-sm text-white">{source.url}</div>
                    <div className="flex items-center gap-3 text-xs text-white/50">
                      <span>{source.status}</span>
                      {source.duration > 0 && <span>{Math.floor(source.duration / 60)}m</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {source.processed && (
                      <span className="rounded-full bg-green-400/20 px-2 py-1 text-xs text-green-400">processed</span>
                    )}
                    <button className="rounded-lg border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-white transition hover:bg-white/[0.08]">
                      Process
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === "analytics" && (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-4">
            {[
              { label: "Videos Processed", value: "1,247", icon: "🎬" },
              { label: "Total Duration", value: "420h", icon: "⏱️" },
              { label: "Clips Generated", value: "8,932", icon: "✂️" },
              { label: "Success Rate", value: "94.2%", icon: "📈" },
            ].map((stat) => (
              <div key={stat.label} className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-center">
                <div className="mb-1 text-2xl">{stat.icon}</div>
                <div className="text-xl font-bold text-white">{stat.value}</div>
                <div className="text-xs text-white/50">{stat.label}</div>
              </div>
            ))}
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-4 font-medium text-white">Processing History</h4>
            <div className="space-y-2">
              {[
                { time: "10:30 AM", event: "Job #1247 completed", status: "success" },
                { time: "10:15 AM", event: "Source added: YouTube video", status: "info" },
                { time: "9:45 AM", event: "Batch processing started", status: "info" },
                { time: "9:30 AM", event: "Job #1246 completed", status: "success" },
              ].map((log, idx) => (
                <div key={idx} className="flex items-center gap-3 rounded-lg bg-white/[0.02] p-2 text-sm">
                  <span className="text-white/30">{log.time}</span>
                  <span
                    className={`h-2 w-2 rounded-full ${
                      log.status === "success" ? "bg-green-400" : "bg-blue-400"
                    }`}
                  />
                  <span className="text-white/70">{log.event}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        <button className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
          New Job
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Batch Import
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Settings
        </button>
      </div>
    </div>
  );
}
