"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";

interface VideoOSEngine {
  name: string;
  status: "healthy" | "error" | "loading";
  description: string;
  endpoint: string;
  metrics?: {
    total_jobs: number;
    active_jobs: number;
    completed_jobs: number;
    failed_jobs: number;
  };
}

interface RenderJob {
  id: string;
  source_url: string;
  status: string;
  created_at: string;
  progress?: number;
}

interface SourceAsset {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
  status: string;
}

export function VideoOSPanel() {
  const [engines, setEngines] = useState<VideoOSEngine[]>([
    {
      name: "Video Service",
      status: "loading",
      description: "Core video processing and management",
      endpoint: "/api/v1/video/health"
    },
    {
      name: "Render Engine",
      status: "loading",
      description: "Video rendering and transcoding",
      endpoint: "/api/v1/render/health"
    },
    {
      name: "Caption Engine",
      status: "loading",
      description: "Automatic caption generation",
      endpoint: "/api/v1/caption/health"
    },
    {
      name: "Audio Engine",
      status: "loading",
      description: "Audio processing and enhancement",
      endpoint: "/api/v1/audio/health"
    },
    {
      name: "Safety Engine",
      status: "loading",
      description: "Content safety and compliance checking",
      endpoint: "/api/v1/safety/health"
    }
  ]);
  const [renderJobs, setRenderJobs] = useState<RenderJob[]>([]);
  const [sourceAssets, setSourceAssets] = useState<SourceAsset[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadVideoOSData = async () => {
      try {
        // Check engine health (using existing endpoints)
        const healthChecks = engines.map(async (engine) => {
          try {
            // Try different health endpoints based on engine type
            let endpoint = engine.endpoint;
            if (engine.name === "Render Engine") {
              endpoint = "/api/v1/render/jobs";
            } else if (engine.name === "Video Service") {
              endpoint = "/api/v1/video/jobs";
            }
            
            const response = await fetch(endpoint);
            const data = await response.json();
            
            return {
              ...engine,
              status: response.ok ? "healthy" : "error",
              metrics: data.metrics || data.total ? {
                total_jobs: data.total || 0,
                active_jobs: data.active || 0,
                completed_jobs: data.completed || 0,
                failed_jobs: data.failed || 0
              } : undefined
            };
          } catch (error) {
            return { ...engine, status: "error" };
          }
        });

        const updatedEngines = await Promise.all(healthChecks);
        setEngines(updatedEngines as VideoOSEngine[]);

        // Load recent render jobs
        try {
          const jobsResponse = await fetch("/api/v1/video/jobs");
          const jobsData = await jobsResponse.json();
          
          if (jobsData.jobs && Array.isArray(jobsData.jobs)) {
            setRenderJobs(jobsData.jobs.slice(0, 5)); // Show last 5 jobs
          }
        } catch (error) {
          console.error("Failed to load render jobs:", error);
        }

        // Load source assets
        try {
          const assetsResponse = await fetch("/api/v1/source-assets");
          const assetsData = await assetsResponse.json();
          
          if (assetsData.assets && Array.isArray(assetsData.assets)) {
            setSourceAssets(assetsData.assets.slice(0, 5)); // Show last 5 assets
          }
        } catch (error) {
          console.error("Failed to load source assets:", error);
        }
      } catch (error) {
        console.error("Failed to load Video OS data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadVideoOSData();
  }, [engines]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy": return "text-green-600";
      case "error": return "text-red-600";
      case "loading": return "text-yellow-600";
      default: return "text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy": return "✓";
      case "error": return "✗";
      case "loading": return "⟳";
      default: return "?";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Video OS</h3>
        <div className="text-center py-8">
          <div className="text-gray-500">Loading Video OS data...</div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Video OS Engines */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Video OS Engines</h3>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {engines.map((engine, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">{engine.name}</h4>
                <span className={`text-2xl ${getStatusColor(engine.status)}`}>
                  {getStatusIcon(engine.status)}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{engine.description}</p>
              
              {engine.metrics && (
                <div className="space-y-1 text-sm mb-3">
                  <div className="flex justify-between">
                    <span>Total Jobs:</span>
                    <span>{engine.metrics.total_jobs}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Active:</span>
                    <span className="text-blue-600">{engine.metrics.active_jobs}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Completed:</span>
                    <span className="text-green-600">{engine.metrics.completed_jobs}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Failed:</span>
                    <span className="text-red-600">{engine.metrics.failed_jobs}</span>
                  </div>
                </div>
              )}
              
              <Button
                variant="secondary"
                size="sm"
                className="w-full"
                disabled={engine.status !== "healthy"}
              >
                {engine.status === "healthy" ? "Manage" : "Unavailable"}
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Recent Render Jobs */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Recent Render Jobs</h3>
        {renderJobs.length > 0 ? (
          <div className="space-y-3">
            {renderJobs.map((job) => (
              <div key={job.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{job.id}</h4>
                  <span className={`text-sm px-2 py-1 rounded ${
                    job.status === "completed" ? "bg-green-500 text-white" :
                    job.status === "processing" ? "bg-blue-500 text-white" :
                    job.status === "failed" ? "bg-red-500 text-white" :
                    "bg-gray-400 text-white"
                  }`}>
                    {job.status}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  <p>Source: {job.source_url}</p>
                  <p>Created: {formatDate(job.created_at)}</p>
                  {job.progress !== undefined && (
                    <div className="mt-2">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Progress:</span>
                        <span>{job.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${job.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No recent render jobs found
          </div>
        )}
      </Card>

      {/* Source Assets */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Source Assets</h3>
        {sourceAssets.length > 0 ? (
          <div className="space-y-3">
            {sourceAssets.map((asset) => (
              <div key={asset.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{asset.filename}</h4>
                  <span className={`text-sm px-2 py-1 rounded ${
                    asset.status === "processed" ? "bg-green-500 text-white" :
                    asset.status === "processing" ? "bg-blue-500 text-white" :
                    asset.status === "failed" ? "bg-red-500 text-white" :
                    "bg-gray-400 text-white"
                  }`}>
                    {asset.status}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  <p>Type: {asset.file_type}</p>
                  <p>Size: {formatFileSize(asset.file_size)}</p>
                  <p>Uploaded: {formatDate(asset.uploaded_at)}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No source assets found
          </div>
        )}
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Button variant="secondary" size="sm">
            Upload Source
          </Button>
          <Button variant="secondary" size="sm">
            Create Render Job
          </Button>
          <Button variant="secondary" size="sm">
            View All Jobs
          </Button>
          <Button variant="secondary" size="sm">
            Engine Settings
          </Button>
        </div>
      </Card>
    </div>
  );
}
