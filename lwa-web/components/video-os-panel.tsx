"use client";

import { useState, useEffect } from "react";

interface VideoJob {
  job_id: string;
  user_id: string;
  job_type: string;
  provider: string;
  status: string;
  prompt?: string;
  input_urls: string[];
  source_asset_ids: string[];
  aspect_ratio: string;
  duration_seconds: number;
  resolution: string;
  style_preset?: string;
  cost_estimate_usd: number;
  progress: number;
  preview_url?: string;
  output_url?: string;
  thumbnail_url?: string;
  error_message?: string;
  timeline_plan?: {
    id: string;
    title: string;
    aspect_ratio: string;
    duration_seconds: number;
    track_count: number;
  };
  created_at: string;
  updated_at: string;
}

interface VideoOSCapabilities {
  enabled: boolean;
  provider: string;
  job_types: string[];
  statuses: string[];
  allowed_aspect_ratios: string[];
  allowed_resolutions: string[];
  max_duration_seconds: number;
  max_inputs: number;
  max_resolution: string;
  allow_live_providers: boolean;
  storage_provider: string;
  mock_mode: boolean;
}

const JOB_TYPES = [
  { value: "text_to_video", label: "Text to Video", description: "Generate video from text prompt" },
  { value: "image_to_video", label: "Image to Video", description: "Animate static images" },
  { value: "video_to_video", label: "Video to Video", description: "Remix or enhance existing video" },
  { value: "clip_to_video", label: "Clip to Video", description: "Convert clips to finished videos" },
  { value: "audio_to_video", label: "Audio to Video", description: "Create visual from audio" },
  { value: "song_visualizer", label: "Song Visualizer", description: "Generate music videos" },
  { value: "timeline_render", label: "Timeline Render", description: "Render timeline composition" },
  { value: "multi_asset_masterpiece", label: "Multi-Asset Masterpiece", description: "Create video from multiple sources" },
];

const ASPECT_RATIOS = [
  { value: "9:16", label: "Vertical (9:16)", description: "TikTok, Reels, Shorts" },
  { value: "16:9", label: "Horizontal (16:9)", description: "YouTube, standard video" },
  { value: "1:1", label: "Square (1:1)", description: "Instagram posts" },
  { value: "4:5", label: "Portrait (4:5)", description: "Instagram stories" },
];

const RESOLUTIONS = [
  { value: "480p", label: "480p (SD)", description: "Standard definition" },
  { value: "720p", label: "720p (HD)", description: "High definition" },
  { value: "1080p", label: "1080p (Full HD)", description: "Full high definition" },
];

export function VideoOSPanel() {
  const [capabilities, setCapabilities] = useState<VideoOSCapabilities | null>(null);
  const [jobs, setJobs] = useState<VideoJob[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedJobType, setSelectedJobType] = useState("");
  const [prompt, setPrompt] = useState("");
  const [inputUrls, setInputUrls] = useState("");
  const [aspectRatio, setAspectRatio] = useState("9:16");
  const [duration, setDuration] = useState(15);
  const [resolution, setResolution] = useState("720p");
  const [stylePreset, setStylePreset] = useState("");
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("create");

  // Fetch capabilities and jobs on mount
  useEffect(() => {
    fetchCapabilities();
    fetchJobs();
  }, []);

  const fetchCapabilities = async () => {
    try {
      const response = await fetch("/api/video-jobs/capabilities");
      if (response.ok) {
        const data = await response.json();
        setCapabilities(data);
      }
    } catch (err) {
      console.error("Failed to fetch capabilities:", err);
    }
  };

  const fetchJobs = async () => {
    try {
      const response = await fetch("/api/video-jobs");
      if (response.ok) {
        const data = await response.json();
        setJobs(data.jobs || []);
      }
    } catch (err) {
      console.error("Failed to fetch jobs:", err);
    }
  };

  const createVideoJob = async () => {
    setError("");
    setIsCreating(true);

    try {
      const urls = inputUrls.split("\n").filter(url => url.trim()).map(url => url.trim());

      const response = await fetch("/api/video-jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_type: selectedJobType,
          prompt: prompt || undefined,
          input_urls: urls,
          aspect_ratio: aspectRatio,
          duration_seconds: duration,
          resolution: resolution,
          style_preset: stylePreset || undefined,
        }),
      });

      if (response.ok) {
        const job = await response.json();
        setJobs(prev => [job, ...prev]);
        // Reset form
        setPrompt("");
        setInputUrls("");
        setStylePreset("");
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to create video job");
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setIsCreating(false);
    }
  };

  const cancelJob = async (jobId: string) => {
    try {
      const response = await fetch(`/api/video-jobs/${jobId}/cancel`, {
        method: "POST",
      });

      if (response.ok) {
        fetchJobs(); // Refresh jobs list
      }
    } catch (err) {
      console.error("Failed to cancel job:", err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-500";
      case "in_progress": case "queued": return "bg-blue-500";
      case "failed": return "bg-red-500";
      case "provider_not_configured": return "bg-yellow-500";
      case "canceled": return "bg-gray-500";
      default: return "bg-gray-500";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "queued": return "Queued";
      case "in_progress": return "Processing";
      case "completed": return "Completed";
      case "failed": return "Failed";
      case "provider_not_configured": return "Not Configured";
      case "canceled": return "Canceled";
      default: return status;
    }
  };

  if (!capabilities) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Video OS</h2>
          <p className="text-gray-600 mb-4">Loading capabilities...</p>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <h1 className="text-3xl font-bold">Video OS</h1>
          {capabilities.mock_mode && (
            <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-sm">Mock Mode</span>
          )}
          {!capabilities.enabled && (
            <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-sm">Disabled</span>
          )}
        </div>
        <p className="text-gray-600">Load anything. Generate finished videos.</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b mb-6">
        <button
          className={`px-4 py-2 font-medium ${activeTab === "create" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-500"}`}
          onClick={() => setActiveTab("create")}
        >
          Create Video
        </button>
        <button
          className={`px-4 py-2 font-medium ${activeTab === "jobs" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-500"}`}
          onClick={() => setActiveTab("jobs")}
        >
          Recent Jobs
        </button>
        <button
          className={`px-4 py-2 font-medium ${activeTab === "info" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-500"}`}
          onClick={() => setActiveTab("info")}
        >
          Info
        </button>
      </div>

      {/* Create Video Tab */}
      {activeTab === "create" && (
        <div className="space-y-4">
          {!capabilities.enabled && (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-yellow-800">
                Video OS is currently disabled. Set LWA_VIDEO_OS_ENABLED=true to enable mock jobs.
              </p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Video Type</label>
              <select
                value={selectedJobType}
                onChange={(e) => setSelectedJobType(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
              >
                <option value="">Select video type</option>
                {JOB_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label} - {type.description}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Aspect Ratio</label>
              <select
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
              >
                {ASPECT_RATIOS.map((ratio) => (
                  <option key={ratio.value} value={ratio.value}>
                    {ratio.label} - {ratio.description}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Duration (seconds)</label>
              <input
                type="number"
                min="1"
                max={capabilities.max_duration_seconds}
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Resolution</label>
              <select
                value={resolution}
                onChange={(e) => setResolution(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
              >
                {RESOLUTIONS.map((res) => (
                  <option key={res.value} value={res.value}>
                    {res.label} - {res.description}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Prompt (optional)</label>
            <textarea
              placeholder="Describe the video you want to create..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Input URLs (one per line, optional)</label>
            <textarea
              placeholder="https://example.com/video1.mp4&#10;https://example.com/image1.jpg"
              value={inputUrls}
              onChange={(e) => setInputUrls(e.target.value)}
              rows={4}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Style Preset (optional)</label>
            <input
              type="text"
              placeholder="cinematic, anime, realistic, etc."
              value={stylePreset}
              onChange={(e) => setStylePreset(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          <button
            onClick={createVideoJob}
            disabled={!selectedJobType || isCreating || !capabilities.enabled}
            className="w-full p-3 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {isCreating ? "Creating..." : "Generate Video"}
          </button>
        </div>
      )}

      {/* Recent Jobs Tab */}
      {activeTab === "jobs" && (
        <div className="space-y-4">
          {jobs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No video jobs yet. Create your first video above.
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.map((job) => (
                <div key={job.job_id} className="p-4 border border-gray-200 rounded">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-medium">{job.job_type.replace(/_/g, " ").toUpperCase()}</h3>
                        <span className={`px-2 py-1 rounded text-xs text-white ${getStatusColor(job.status)}`}>
                          {getStatusText(job.status)}
                        </span>
                        {job.provider === "mock" && (
                          <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-xs">Mock</span>
                        )}
                      </div>
                      
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>Duration: {job.duration_seconds}s</div>
                        <div>Resolution: {job.resolution}</div>
                        <div>Aspect Ratio: {job.aspect_ratio}</div>
                        {job.prompt && <div>Prompt: {job.prompt}</div>}
                        {job.error_message && (
                          <div className="text-red-600">Error: {job.error_message}</div>
                        )}
                      </div>

                      {job.progress > 0 && job.status === "in_progress" && (
                        <div className="mt-2">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${job.progress}%` }}
                            ></div>
                          </div>
                          <div className="text-sm text-gray-500 mt-1">{job.progress}% complete</div>
                        </div>
                      )}

                      {job.output_url && (
                        <div className="mt-2">
                          <a
                            href={job.output_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            View Output →
                          </a>
                        </div>
                      )}

                      {job.timeline_plan && (
                        <div className="mt-2 text-sm text-gray-500">
                          Timeline: {job.timeline_plan.track_count} tracks, {job.timeline_plan.duration_seconds}s
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col gap-2 ml-4">
                      <div className="text-sm text-gray-500">
                        ${job.cost_estimate_usd.toFixed(4)}
                      </div>
                      {(job.status === "queued" || job.status === "in_progress") && (
                        <button
                          className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50"
                          onClick={() => cancelJob(job.job_id)}
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Info Tab */}
      {activeTab === "info" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border border-gray-200 rounded">
              <h3 className="text-lg font-medium mb-3">Configuration</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Enabled:</span>
                  <span className={capabilities.enabled ? "text-green-600" : "text-red-600"}>
                    {capabilities.enabled ? "Yes" : "No"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Provider:</span>
                  <span>{capabilities.provider}</span>
                </div>
                <div className="flex justify-between">
                  <span>Mock Mode:</span>
                  <span className={capabilities.mock_mode ? "text-yellow-600" : "text-green-600"}>
                    {capabilities.mock_mode ? "Yes" : "No"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Storage:</span>
                  <span>{capabilities.storage_provider}</span>
                </div>
              </div>
            </div>

            <div className="p-4 border border-gray-200 rounded">
              <h3 className="text-lg font-medium mb-3">Limits</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Max Duration:</span>
                  <span>{capabilities.max_duration_seconds}s</span>
                </div>
                <div className="flex justify-between">
                  <span>Max Inputs:</span>
                  <span>{capabilities.max_inputs}</span>
                </div>
                <div className="flex justify-between">
                  <span>Max Resolution:</span>
                  <span>{capabilities.max_resolution}</span>
                </div>
                <div className="flex justify-between">
                  <span>Live Providers:</span>
                  <span className={capabilities.allow_live_providers ? "text-green-600" : "text-red-600"}>
                    {capabilities.allow_live_providers ? "Allowed" : "Disabled"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="p-4 border border-gray-200 rounded">
            <h3 className="text-lg font-medium mb-3">Supported Job Types</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {capabilities.job_types.map((type) => (
                <span key={type} className="px-2 py-1 bg-gray-100 rounded text-sm">
                  {type.replace(/_/g, " ").toUpperCase()}
                </span>
              ))}
            </div>
          </div>

          {capabilities.mock_mode && (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-yellow-800">
                <strong>Mock Mode Active:</strong> Video OS is running in mock mode. Jobs will complete instantly 
                with placeholder outputs. Enable live providers by setting LWA_VIDEO_OS_ENABLED=true and configuring 
                provider credentials.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
