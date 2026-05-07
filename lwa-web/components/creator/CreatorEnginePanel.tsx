"use client";

import { useState, useEffect, useCallback } from "react";
import {
  creatorEngine,
  type CreatorEngineJob,
  type CreatorEngineJobType,
} from "../../lib/creator-engine";

export default function CreatorEnginePanel() {
  const [jobs, setJobs] = useState<CreatorEngineJob[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [stats, setStats] = useState(creatorEngine.getStatistics());

  // Subscribe to job updates
  useEffect(() => {
    const updateJobs = () => {
      setJobs(creatorEngine.getAllJobs());
      setStats(creatorEngine.getStatistics());
    };

    updateJobs();
    const interval = setInterval(updateJobs, 1000);
    return () => clearInterval(interval);
  }, []);

  const createJob = useCallback((type: CreatorEngineJobType) => {
    const jobId = creatorEngine.createJob(
      type,
      "user123",
      "https://example.com/source.mp4",
      type === "clip_generation" 
        ? { maxClips: 5 }
        : type === "render_job"
        ? { clipId: "clip_123" }
        : type === "export_bundle"
        ? { clipIds: ["clip_1", "clip_2"] }
        : undefined
    );
    setSelectedJobId(jobId);
    return jobId;
  }, []);

  const processJob = useCallback(async (jobId: string) => {
    const job = creatorEngine.getJob(jobId);
    if (!job) return;

    setIsProcessing(true);
    try {
      switch (job.type) {
        case "clip_generation":
          await creatorEngine.processClipGeneration(jobId);
          break;
        case "hook_extraction":
          await creatorEngine.processHookExtraction(jobId);
          break;
        case "caption_generation":
          await creatorEngine.processCaptionGeneration(jobId);
          break;
        case "scoring":
          await creatorEngine.processScoring(jobId);
          break;
        case "render_job":
          await creatorEngine.processRenderJob(jobId);
          break;
        case "export_bundle":
          await creatorEngine.processExportBundle(jobId);
          break;
      }
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const processAllJobs = useCallback(async () => {
    const pendingJobs = jobs.filter(job => job.status === "pending");
    if (pendingJobs.length === 0) return;

    setIsProcessing(true);
    try {
      await creatorEngine.processBatchJobs(pendingJobs.map(job => job.id));
    } finally {
      setIsProcessing(false);
    }
  }, [jobs]);

  const clearCompleted = useCallback(() => {
    creatorEngine.clearCompletedJobs();
  }, []);

  const getSelectedJob = () => {
    return jobs.find(job => job.id === selectedJobId);
  };

  const getJobTypeColor = (type: CreatorEngineJobType) => {
    switch (type) {
      case "clip_generation": return "text-blue-400";
      case "hook_extraction": return "text-green-400";
      case "caption_generation": return "text-yellow-400";
      case "scoring": return "text-purple-400";
      case "render_job": return "text-orange-400";
      case "export_bundle": return "text-pink-400";
      default: return "text-gray-400";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "text-emerald-400";
      case "failed": return "text-red-400";
      case "processing": return "text-yellow-400";
      case "pending": return "text-blue-400";
      default: return "text-gray-400";
    }
  };

  return (
    <section className="relative mx-auto max-w-7xl px-6 py-12 text-[#F5F1E8]">
      <div className="max-w-4xl">
        <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">
          Creator Engine
        </p>
        <h2 className="mt-5 text-[clamp(2.4rem,5vw,5rem)] font-black uppercase leading-[0.92] tracking-normal text-white">
          Turn source content into clips, hooks, captions, scores, and exports.
        </h2>
        <p className="mt-6 text-base leading-8 text-white/62">
          This engine processes source content to generate viral clips, extract hooks,
          create captions, score content, render videos, and bundle exports for creators.
        </p>
      </div>

      {/* Statistics */}
      <div className="mt-8 grid gap-4 md:grid-cols-5">
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">Total Jobs</p>
          <p className="mt-2 text-3xl font-black text-white">{stats.totalJobs}</p>
        </div>
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">Completed</p>
          <p className="mt-2 text-3xl font-black text-emerald-400">{stats.completedJobs}</p>
        </div>
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">Failed</p>
          <p className="mt-2 text-3xl font-black text-red-400">{stats.failedJobs}</p>
        </div>
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">Avg Time</p>
          <p className="mt-2 text-3xl font-black text-white">
            {Math.round(stats.averageProcessingTime / 1000)}s
          </p>
        </div>
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">Success Rate</p>
          <p className="mt-2 text-3xl font-black text-white">
            {stats.totalJobs > 0 ? Math.round((stats.completedJobs / stats.totalJobs) * 100) : 0}%
          </p>
        </div>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[minmax(0,0.6fr)_minmax(0,1.4fr)]">
        {/* Control Panel */}
        <section className="rounded-[28px] border border-white/10 bg-black/35 p-6 shadow-[0_28px_90px_-60px_rgba(126,58,242,0.9)]">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
            Job Control
          </p>

          <div className="mt-5 space-y-4">
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Create New Job
              </label>
              <div className="grid gap-2">
                <button
                  onClick={() => createJob("clip_generation")}
                  className="rounded-lg border border-blue-400/40 bg-blue-400/15 px-3 py-2 text-sm font-medium text-blue-300 transition hover:bg-blue-400/25"
                >
                  Clip Generation
                </button>
                <button
                  onClick={() => createJob("hook_extraction")}
                  className="rounded-lg border border-green-400/40 bg-green-400/15 px-3 py-2 text-sm font-medium text-green-300 transition hover:bg-green-400/25"
                >
                  Hook Extraction
                </button>
                <button
                  onClick={() => createJob("caption_generation")}
                  className="rounded-lg border border-yellow-400/40 bg-yellow-400/15 px-3 py-2 text-sm font-medium text-yellow-300 transition hover:bg-yellow-400/25"
                >
                  Caption Generation
                </button>
                <button
                  onClick={() => createJob("scoring")}
                  className="rounded-lg border border-purple-400/40 bg-purple-400/15 px-3 py-2 text-sm font-medium text-purple-300 transition hover:bg-purple-400/25"
                >
                  Content Scoring
                </button>
                <button
                  onClick={() => createJob("render_job")}
                  className="rounded-lg border border-orange-400/40 bg-orange-400/15 px-3 py-2 text-sm font-medium text-orange-300 transition hover:bg-orange-400/25"
                >
                  Render Job
                </button>
                <button
                  onClick={() => createJob("export_bundle")}
                  className="rounded-lg border border-pink-400/40 bg-pink-400/15 px-3 py-2 text-sm font-medium text-pink-300 transition hover:bg-pink-400/25"
                >
                  Export Bundle
                </button>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={processAllJobs}
                disabled={isProcessing}
                className="rounded-full border border-[#C9A24A]/40 bg-[#C9A24A]/15 px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#C9A24A]/25 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Process All
              </button>
              <button
                onClick={clearCompleted}
                className="rounded-full border border-white/10 bg-white/[0.05] px-4 py-2 text-sm font-semibold text-white/70 transition hover:border-white/20 hover:bg-white/[0.1]"
              >
                Clear Completed
              </button>
            </div>
          </div>

          {/* Selected Job Details */}
          {selectedJobId && (
            <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/35 mb-3">
                Selected Job
              </p>
              {(() => {
                const job = getSelectedJob();
                if (!job) {
                  return <p className="text-sm text-white/50">No job selected</p>;
                }
                return (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-white/60">ID:</span>
                      <span className="font-mono text-white">{job.id.substring(0, 16)}...</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/60">Type:</span>
                      <span className={`font-medium ${getJobTypeColor(job.type)}`}>
                        {job.type.replace("_", " ")}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/60">Status:</span>
                      <span className={`font-medium ${getStatusColor(job.status)}`}>
                        {job.status}
                      </span>
                    </div>
                    {job.progress !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-white/60">Progress:</span>
                        <span className="font-medium text-white">{job.progress}%</span>
                      </div>
                    )}
                    {job.stage && (
                      <div className="flex justify-between">
                        <span className="text-white/60">Stage:</span>
                        <span className="font-medium text-white">{job.stage}</span>
                      </div>
                    )}
                    {job.error && (
                      <div className="text-red-400 text-xs">
                        Error: {job.error}
                      </div>
                    )}
                    {job.status === "pending" && (
                      <button
                        onClick={() => processJob(job.id)}
                        disabled={isProcessing}
                        className="mt-2 w-full rounded-lg border border-[#C9A24A]/40 bg-[#C9A24A]/15 px-3 py-2 text-sm font-medium text-[#E9C77B] transition hover:bg-[#C9A24A]/25 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Process Job
                      </button>
                    )}
                  </div>
                );
              })()}
            </div>
          )}
        </section>

        {/* Jobs List */}
        <section className="rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
            Jobs Queue
          </p>

          <div className="mt-5 max-h-96 overflow-y-auto space-y-2">
            {jobs.length === 0 ? (
              <p className="text-sm text-white/50">No jobs created yet. Click a button to start.</p>
            ) : (
              jobs.map((job) => (
                <div
                  key={job.id}
                  onClick={() => setSelectedJobId(job.id)}
                  className={`rounded-lg border p-3 text-sm cursor-pointer transition ${
                    selectedJobId === job.id
                      ? "border-[#C9A24A]/40 bg-[#C9A24A]/10"
                      : "border-white/10 bg-black/25 hover:border-white/20"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className={`font-mono ${getJobTypeColor(job.type)}`}>
                        {job.type.replace("_", " ")}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        job.status === "completed" ? "bg-emerald-400/20 text-emerald-300" :
                        job.status === "failed" ? "bg-red-400/20 text-red-300" :
                        job.status === "processing" ? "bg-yellow-400/20 text-yellow-300" :
                        "bg-blue-400/20 text-blue-300"
                      }`}>
                        {job.status}
                      </span>
                    </div>
                    <span className="text-white/40 text-xs">
                      {new Date(job.createdAt).toLocaleTimeString()}
                    </span>
                  </div>
                  {job.progress !== undefined && (
                    <div className="mt-2">
                      <div className="flex justify-between text-xs text-white/60 mb-1">
                        <span>Progress</span>
                        <span>{job.progress}%</span>
                      </div>
                      <div className="w-full bg-white/10 rounded-full h-1">
                        <div
                          className="bg-[#C9A24A] h-1 rounded-full transition-all duration-300"
                          style={{ width: `${job.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                  {job.stage && (
                    <div className="mt-1 text-xs text-white/60">
                      Stage: {job.stage}
                    </div>
                  )}
                  {job.error && (
                    <div className="mt-1 text-xs text-red-400">
                      {job.error}
                    </div>
                  )}
                  {job.result && (
                    <div className="mt-2 text-xs text-white/60">
                      {job.result.clips && `${job.result.clips.length} clips`}
                      {job.result.hooks && `${job.result.hooks.length} hooks`}
                      {job.result.captions && `${job.result.captions.length} captions`}
                      {job.result.scores && `${job.result.scores.length} scores`}
                      {job.result.renderJobs && `${job.result.renderJobs.length} renders`}
                      {job.result.exportBundle && "1 bundle"}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      {/* Job Type Breakdown */}
      <section className="mt-8 rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
          Jobs by Type
        </p>

        <div className="mt-5 grid gap-4 md:grid-cols-3">
          {Object.entries(stats.jobsByType).map(([type, count]) => (
            <div
              key={type}
              className="rounded-lg border border-white/10 bg-black/25 p-4 text-sm"
            >
              <div className="flex items-center justify-between">
                <span className={`font-medium ${getJobTypeColor(type as CreatorEngineJobType)}`}>
                  {type.replace("_", " ")}
                </span>
                <span className="text-white font-bold">{count}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </section>
  );
}
