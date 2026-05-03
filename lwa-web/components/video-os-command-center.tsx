"use client";

import { useState, useEffect } from "react";
import { 
  createSourceAsset, 
  listSourceAssets, 
  deleteSourceAsset,
  createVideoJob,
  listVideoJobs,
  getVideoJob,
  composeTimeline,
  sendTimelineToRender,
  listTimelines,
  createCampaignExport,
  createFeedback,
  SourceAsset,
  VideoJob,
  Timeline,
  SourceAssetCreatePayload,
  VideoJobRequest,
  TimelineComposerRequest
} from "../lib/api";

interface VideoOSCommandCenterProps {
  token: string;
}

export function VideoOSCommandCenter({ token }: VideoOSCommandCenterProps) {
  const [activeTab, setActiveTab] = useState("sources");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // Source assets state
  const [sourceAssets, setSourceAssets] = useState<SourceAsset[]>([]);
  const [selectedSourceAssets, setSelectedSourceAssets] = useState<string[]>([]);

  // Video jobs state
  const [videoJobs, setVideoJobs] = useState<VideoJob[]>([]);

  // Timeline state
  const [timelines, setTimelines] = useState<Timeline[]>([]);
  const [selectedTimeline, setSelectedTimeline] = useState<Timeline | null>(null);

  // Form states
  const [sourceUrl, setSourceUrl] = useState("");
  const [sourceContent, setSourceContent] = useState("");
  const [sourceType, setSourceType] = useState("url");
  const [prompt, setPrompt] = useState("");
  const [goal, setGoal] = useState("attention");
  const [platform, setPlatform] = useState("tiktok");
  const [stylePreset, setStylePreset] = useState("clean_minimal");

  // Load data on mount
  useEffect(() => {
    if (token) {
      const loadSourceAssets = async () => {
        try {
          const response = await listSourceAssets(token);
          setSourceAssets(response.assets || []);
        } catch (err) {
          console.error("Failed to load source assets:", err);
        }
      };

      const loadVideoJobs = async () => {
        try {
          const response = await listVideoJobs(token);
          setVideoJobs(response.jobs || []);
        } catch (err) {
          console.error("Failed to load video jobs:", err);
        }
      };

      const loadTimelines = async () => {
        try {
          const response = await listTimelines(token);
          setTimelines(response.timelines || []);
        } catch (err) {
          console.error("Failed to load timelines:", err);
        }
      };

      loadSourceAssets();
      loadVideoJobs();
      loadTimelines();
    }
  }, [token]);

  
  const addSourceAsset = async () => {
    setError("");
    setIsLoading(true);

    try {
      const payload: SourceAssetCreatePayload = {
        asset_type: sourceType,
        source_url: sourceUrl || undefined,
        source_content: sourceContent || undefined,
      };

      const newAsset = await createSourceAsset(token, payload);
      setSourceAssets(prev => [newAsset, ...prev]);
      
      // Reset form
      setSourceUrl("");
      setSourceContent("");
    } catch (err: any) {
      setError(err.message || "Failed to create source asset");
    } finally {
      setIsLoading(false);
    }
  };

  const createVideoJobFromAssets = async () => {
    if (selectedSourceAssets.length === 0) {
      setError("Please select source assets first");
      return;
    }

    setError("");
    setIsLoading(true);

    try {
      const payload: VideoJobRequest = {
        job_type: "multi_asset_masterpiece",
        prompt: prompt || undefined,
        source_asset_ids: selectedSourceAssets,
        aspect_ratio: platform === "youtube" ? "16:9" : "9:16",
        style_preset: stylePreset,
      };

      const job = await createVideoJob(token, payload);
      setVideoJobs(prev => [job, ...prev]);
      
      // Reset selection
      setSelectedSourceAssets([]);
    } catch (err: any) {
      setError(err.message || "Failed to create video job");
    } finally {
      setIsLoading(false);
    }
  };

  const composeTimelineFromAssets = async () => {
    if (selectedSourceAssets.length === 0) {
      setError("Please select source assets first");
      return;
    }

    setError("");
    setIsLoading(true);

    try {
      const payload: TimelineComposerRequest = {
        source_asset_ids: selectedSourceAssets,
        prompt: prompt || undefined,
        goal: goal,
        platform: platform,
        style_preset: stylePreset,
        include_hook: true,
        include_cta: goal === "sales",
        include_captions: true,
        include_broll: stylePreset === "cinematic_broll",
      };

      const timeline = await composeTimeline(token, payload);
      setTimelines(prev => [timeline, ...prev]);
      setSelectedTimeline(timeline);
      
      // Switch to timeline tab
      setActiveTab("timeline");
    } catch (err: any) {
      setError(err.message || "Failed to compose timeline");
    } finally {
      setIsLoading(false);
    }
  };

  const sendTimelineToRenderEngine = async () => {
    if (!selectedTimeline) {
      setError("Please select a timeline first");
      return;
    }

    setError("");
    setIsLoading(true);

    try {
      const result = await sendTimelineToRender(token, selectedTimeline.timeline_id);
      
      if (result.success) {
        // Reload video jobs to see the new render job
        const videoJobsResponse = await listVideoJobs(token);
        setVideoJobs(videoJobsResponse.jobs || []);
        setActiveTab("render");
      } else {
        setError(result.error || "Failed to send to render");
      }
    } catch (err: any) {
      setError(err.message || "Failed to send to render");
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSourceAssetSelection = (assetId: string) => {
    setSelectedSourceAssets(prev => 
      prev.includes(assetId) 
        ? prev.filter(id => id !== assetId)
        : [...prev, assetId]
    );
  };

  const deleteSourceAssetById = async (assetId: string) => {
    try {
      await deleteSourceAsset(token, assetId);
      setSourceAssets(prev => prev.filter(asset => asset.asset_id !== assetId));
      setSelectedSourceAssets(prev => prev.filter(id => id !== assetId));
    } catch (err) {
      console.error("Failed to delete source asset:", err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ready": case "completed": return "text-green-600";
      case "processing": case "in_progress": case "composing": return "text-blue-600";
      case "failed": return "text-red-600";
      case "queued": return "text-yellow-600";
      default: return "text-gray-600";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 bg-black text-white min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-yellow-400 to-yellow-600 bg-clip-text text-transparent">
          Video OS Command Center
        </h1>
        <p className="text-gray-400">Load anything. Create finished video packages.</p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-900/50 border border-red-600 rounded-lg">
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-8 border-b border-gray-800">
        {[
          { id: "sources", label: "Sources" },
          { id: "assets", label: "Asset Vault" },
          { id: "strategy", label: "Strategy" },
          { id: "timeline", label: "Timeline" },
          { id: "render", label: "Render Jobs" },
          { id: "export", label: "Export" },
          { id: "next", label: "Next Action" }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === tab.id
                ? "text-yellow-400 border-b-2 border-yellow-400"
                : "text-gray-400 hover:text-white"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Sources Tab */}
        {activeTab === "sources" && (
          <div className="space-y-6">
            <div className="bg-gray-900 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Add Source</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Source Type</label>
                  <select
                    value={sourceType}
                    onChange={(e) => setSourceType(e.target.value)}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg text-white"
                  >
                    <option value="url">URL</option>
                    <option value="script">Script</option>
                    <option value="voice_note">Voice Note</option>
                    <option value="video">Video</option>
                    <option value="audio">Audio</option>
                    <option value="image">Image</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Source URL</label>
                  <input
                    type="url"
                    placeholder="https://example.com/video.mp4"
                    value={sourceUrl}
                    onChange={(e) => setSourceUrl(e.target.value)}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Text Content</label>
                  <textarea
                    placeholder="Enter script or voice note content..."
                    value={sourceContent}
                    onChange={(e) => setSourceContent(e.target.value)}
                    rows={4}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400"
                  />
                </div>

                <button
                  onClick={addSourceAsset}
                  disabled={isLoading || (!sourceUrl && !sourceContent)}
                  className="w-full py-3 bg-yellow-500 text-black font-semibold rounded-lg hover:bg-yellow-400 disabled:bg-gray-700 disabled:text-gray-500 transition-colors"
                >
                  {isLoading ? "Adding..." : "Add Source"}
                </button>
              </div>
            </div>

            <div className="bg-gray-900 rounded-lg p-4">
              <p className="text-sm text-yellow-400">
                ⚠️ Metadata-only storage (v0 limitation) - no actual files stored yet
              </p>
            </div>
          </div>
        )}

        {/* Asset Vault Tab */}
        {activeTab === "assets" && (
          <div className="space-y-6">
            <div className="bg-gray-900 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Asset Vault</h2>
              
              {sourceAssets.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No assets yet. Add your first source asset.
                </div>
              ) : (
                <div className="space-y-3">
                  {sourceAssets.map((asset) => (
                    <div key={asset.asset_id} className="bg-gray-800 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <input
                              type="checkbox"
                              checked={selectedSourceAssets.includes(asset.asset_id)}
                              onChange={() => toggleSourceAssetSelection(asset.asset_id)}
                              className="rounded"
                            />
                            <span className="font-medium">{asset.asset_type.toUpperCase()}</span>
                            <span className={`px-2 py-1 rounded text-xs ${getStatusColor(asset.status)}`}>
                              {asset.status}
                            </span>
                          </div>
                          
                          <div className="text-sm text-gray-400 space-y-1">
                            {asset.source_url && (
                              <div>URL: {asset.source_url}</div>
                            )}
                            {asset.source_content && (
                              <div>Content: {asset.source_content.substring(0, 100)}...</div>
                            )}
                            {asset.metadata?.filename && (
                              <div>File: {asset.metadata.filename}</div>
                            )}
                            <div>Created: {formatDate(asset.created_at)}</div>
                          </div>
                        </div>

                        <button
                          onClick={() => deleteSourceAssetById(asset.asset_id)}
                          className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {selectedSourceAssets.length > 0 && (
              <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4">
                <p className="text-yellow-200">
                  {selectedSourceAssets.length} asset(s) selected for timeline and video job creation
                </p>
              </div>
            )}
          </div>
        )}

        {/* Strategy Tab */}
        {activeTab === "strategy" && (
          <div className="space-y-6">
            <div className="bg-gray-900 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Strategy & Style</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Prompt (optional)</label>
                  <textarea
                    placeholder="Describe your video concept..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={3}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Goal</label>
                  <select
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg text-white"
                  >
                    <option value="attention">Attention</option>
                    <option value="trust">Trust</option>
                    <option value="sales">Sales</option>
                    <option value="proof">Proof</option>
                    <option value="authority">Authority</option>
                    <option value="community">Community</option>
                    <option value="launch">Launch</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Platform</label>
                  <select
                    value={platform}
                    onChange={(e) => setPlatform(e.target.value)}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg text-white"
                  >
                    <option value="tiktok">TikTok</option>
                    <option value="instagram">Instagram Reels</option>
                    <option value="youtube_shorts">YouTube Shorts</option>
                    <option value="youtube">YouTube</option>
                    <option value="whop">Whop</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="ads">Ads</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Style Preset</label>
                  <select
                    value={stylePreset}
                    onChange={(e) => setStylePreset(e.target.value)}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg text-white"
                  >
                    <option value="clean_minimal">Clean Minimal</option>
                    <option value="viral_aggressive">Viral Aggressive</option>
                    <option value="luxury_editorial">Luxury Editorial</option>
                    <option value="gaming_neon">Gaming Neon</option>
                    <option value="podcast_clean">Podcast Clean</option>
                    <option value="cinematic_broll">Cinematic B-roll</option>
                  </select>
                </div>

                <div className="flex gap-4">
                  <button
                    onClick={composeTimelineFromAssets}
                    disabled={isLoading || selectedSourceAssets.length === 0}
                    className="flex-1 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 transition-colors"
                  >
                    {isLoading ? "Composing..." : "Compose Timeline"}
                  </button>
                  
                  <button
                    onClick={createVideoJobFromAssets}
                    disabled={isLoading || selectedSourceAssets.length === 0}
                    className="flex-1 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:bg-gray-700 disabled:text-gray-500 transition-colors"
                  >
                    {isLoading ? "Creating..." : "Create Video Job"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Timeline Tab */}
        {activeTab === "timeline" && (
          <div className="space-y-6">
            <div className="bg-gray-900 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Timeline Plans</h2>
              
              {timelines.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No timelines yet. Create your first timeline from the Strategy tab.
                </div>
              ) : (
                <div className="space-y-4">
                  {timelines.map((timeline) => (
                    <div 
                      key={timeline.timeline_id} 
                      className={`bg-gray-800 rounded-lg p-4 cursor-pointer border ${
                        selectedTimeline?.timeline_id === timeline.timeline_id 
                          ? 'border-yellow-400' 
                          : 'border-gray-700'
                      }`}
                      onClick={() => setSelectedTimeline(timeline)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="font-medium">{timeline.title}</h3>
                          <p className="text-sm text-gray-400">{timeline.strategy_summary}</p>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs ${getStatusColor(timeline.status)}`}>
                          {timeline.status}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-400 space-y-1">
                        <div>Duration: {timeline.total_duration_seconds}s</div>
                        <div>Aspect Ratio: {timeline.aspect_ratio}</div>
                        <div>Tracks: {timeline.tracks.length}</div>
                        <div>Created: {formatDate(timeline.created_at)}</div>
                      </div>

                      {timeline.warnings.length > 0 && (
                        <div className="mt-3 p-2 bg-yellow-900/30 border border-yellow-600 rounded">
                          <p className="text-yellow-200 text-sm">
                            Warnings: {timeline.warnings.join(", ")}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {selectedTimeline && (
              <div className="bg-gray-900 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Selected Timeline</h3>
                
                <div className="mb-4">
                  <h4 className="font-medium mb-2">Tracks</h4>
                  <div className="space-y-2">
                    {selectedTimeline.tracks.map((track: any) => (
                      <div key={track.track_id} className="bg-gray-800 rounded p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{track.track_type.toUpperCase()}</span>
                          <span className="text-sm text-gray-400">{track.segments.length} segments</span>
                        </div>
                        <div className="text-sm text-gray-400">
                          Duration: {track.segments.reduce((sum: number, seg: any) => sum + seg.duration, 0).toFixed(1)}s
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex gap-4">
                  <button
                    onClick={sendTimelineToRenderEngine}
                    disabled={isLoading}
                    className="flex-1 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:bg-gray-700 disabled:text-gray-500 transition-colors"
                  >
                    {isLoading ? "Sending..." : "Send to Render"}
                  </button>
                </div>

                <div className="mt-4 p-3 bg-blue-900/30 border border-blue-600 rounded">
                  <p className="text-blue-200 text-sm">
                    Timeline plan only - no MP4 rendered yet. Send to render to create video job.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Render Jobs Tab */}
        {activeTab === "render" && (
          <div className="space-y-6">
            <div className="bg-gray-900 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Render Jobs</h2>
              
              {videoJobs.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No render jobs yet. Create a video job or send a timeline to render.
                </div>
              ) : (
                <div className="space-y-4">
                  {videoJobs.map((job) => (
                    <div key={job.job_id} className="bg-gray-800 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="font-medium">{job.job_type.replace(/_/g, " ").toUpperCase()}</h3>
                          <p className="text-sm text-gray-400">Provider: {job.provider}</p>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs ${getStatusColor(job.status)}`}>
                          {job.status}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-400 space-y-1">
                        {job.prompt && <div>Prompt: {job.prompt}</div>}
                        {job.aspect_ratio && <div>Aspect: {job.aspect_ratio}</div>}
                        {job.duration_seconds && <div>Duration: {job.duration_seconds}s</div>}
                        {job.cost_estimate_usd && <div>Cost: ${job.cost_estimate_usd.toFixed(2)}</div>}
                        {job.progress !== undefined && <div>Progress: {Math.round(job.progress * 100)}%</div>}
                        <div>Created: {formatDate(job.created_at)}</div>
                      </div>

                      {job.error_message && (
                        <div className="mt-3 p-2 bg-red-900/30 border border-red-600 rounded">
                          <p className="text-red-200 text-sm">{job.error_message}</p>
                        </div>
                      )}

                      {job.output_url && (
                        <div className="mt-3">
                          <a 
                            href={job.output_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 underline"
                          >
                            View Output
                          </a>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="bg-gray-900 rounded-lg p-4">
              <p className="text-sm text-yellow-400">
                ⚠️ Mock/Provider Disabled - No actual video generation in v0
              </p>
            </div>
          </div>
        )}

        {/* Export Tab */}
        {activeTab === "export" && (
          <div className="space-y-6">
            <div className="bg-gray-900 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Package Export</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Platform Package</label>
                  <select
                    value={platform}
                    onChange={(e) => setPlatform(e.target.value)}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg text-white"
                  >
                    <option value="tiktok">TikTok Package</option>
                    <option value="instagram">Instagram Reels Package</option>
                    <option value="youtube_shorts">YouTube Shorts Package</option>
                    <option value="youtube">YouTube Package</option>
                    <option value="whop">Whop Package</option>
                    <option value="linkedin">LinkedIn Package</option>
                  </select>
                </div>

                <div className="p-4 bg-gray-800 rounded-lg">
                  <h4 className="font-medium mb-3">Package Contents</h4>
                  <div className="space-y-2 text-sm text-gray-400">
                    <div>• Platform-optimized title</div>
                    <div>• Caption copy with hashtags</div>
                    <div>• Call-to-action text</div>
                    <div>• Posting instructions</div>
                    <div>• Asset references</div>
                  </div>
                </div>

                <button
                  onClick={() => {
                    // Placeholder for campaign export
                    setError("Campaign export not available yet - future feature");
                  }}
                  className="w-full py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Generate Package
                </button>
              </div>
            </div>

            <div className="bg-gray-900 rounded-lg p-4">
              <p className="text-sm text-yellow-400">
                ⚠️ Metadata/Text package only - Future storage/export integration needed
              </p>
            </div>
          </div>
        )}

        {/* Next Action Tab */}
        {activeTab === "next" && (
          <div className="space-y-6">
            <div className="bg-gray-900 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Next Action</h2>
              
              <div className="space-y-4">
                <div className="p-4 bg-gray-800 rounded-lg">
                  <h4 className="font-medium mb-2">Recommended Next Move</h4>
                  <p className="text-gray-300 mb-3">
                    {selectedSourceAssets.length > 0 
                      ? "You have source assets ready. Create a timeline or video job."
                      : "Start by adding source assets to build your video foundation."
                    }
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => setActiveTab("sources")}
                    className="py-3 bg-gray-800 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    Add Sources
                  </button>
                  
                  <button
                    onClick={() => setActiveTab("strategy")}
                    disabled={selectedSourceAssets.length === 0}
                    className="py-3 bg-gray-800 text-white font-medium rounded-lg hover:bg-gray-700 disabled:bg-gray-900 disabled:text-gray-600 transition-colors"
                  >
                    Set Strategy
                  </button>
                  
                  <button
                    onClick={() => setActiveTab("timeline")}
                    disabled={timelines.length === 0}
                    className="py-3 bg-gray-800 text-white font-medium rounded-lg hover:bg-gray-700 disabled:bg-gray-900 disabled:text-gray-600 transition-colors"
                  >
                    View Timeline
                  </button>
                  
                  <button
                    onClick={() => setActiveTab("render")}
                    disabled={videoJobs.length === 0}
                    className="py-3 bg-gray-800 text-white font-medium rounded-lg hover:bg-gray-700 disabled:bg-gray-900 disabled:text-gray-600 transition-colors"
                  >
                    Check Renders
                  </button>
                </div>

                <div className="p-4 bg-yellow-900/30 border border-yellow-600 rounded">
                  <h4 className="font-medium mb-2 text-yellow-200">Quick Actions</h4>
                  <div className="space-y-2">
                    <button className="w-full py-2 bg-yellow-600/20 text-yellow-200 rounded hover:bg-yellow-600/30 transition-colors">
                      Post First (when ready)
                    </button>
                    <button className="w-full py-2 bg-yellow-600/20 text-yellow-200 rounded hover:bg-yellow-600/30 transition-colors">
                      Render Next
                    </button>
                    <button className="w-full py-2 bg-yellow-600/20 text-yellow-200 rounded hover:bg-yellow-600/30 transition-colors">
                      Add Captions
                    </button>
                    <button className="w-full py-2 bg-yellow-600/20 text-yellow-200 rounded hover:bg-yellow-600/30 transition-colors">
                      Package for Whop
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
