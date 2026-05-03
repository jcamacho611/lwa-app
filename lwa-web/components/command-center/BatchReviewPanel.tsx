"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";

interface BatchJob {
  id: string;
  name: string;
  status: string;
  total_clips: number;
  completed_clips: number;
  failed_clips: number;
  created_at: string;
  completed_at?: string;
  source_assets: string[];
  settings: {
    clip_duration: number;
    output_format: string;
    quality: string;
  };
}

interface RenderJob {
  id: string;
  batch_job_id?: string;
  source_asset_id: string;
  clip_title: string;
  status: string;
  progress?: number;
  output_url?: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
  render_settings: {
    resolution: string;
    format: string;
    quality: string;
  };
}

interface ProofItem {
  id: string;
  render_job_id: string;
  clip_title: string;
  thumbnail_url?: string;
  video_url?: string;
  status: string;
  review_status: string;
  created_at: string;
  metadata: {
    duration: number;
    file_size: number;
    tags: string[];
  };
}

export function BatchReviewPanel() {
  const [batchJobs, setBatchJobs] = useState<BatchJob[]>([]);
  const [renderJobs, setRenderJobs] = useState<RenderJob[]>([]);
  const [proofItems, setProofItems] = useState<ProofItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"batch" | "render" | "proof">("batch");

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load batch jobs
        try {
          const batchResponse = await fetch("/api/v1/batch/jobs");
          const batchData = await batchResponse.json();
          
          if (batchData.jobs && Array.isArray(batchData.jobs)) {
            setBatchJobs(batchData.jobs.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load batch jobs:", error);
        }

        // Load render jobs
        try {
          const renderResponse = await fetch("/api/v1/render/jobs");
          const renderData = await renderResponse.json();
          
          if (renderData.jobs && Array.isArray(renderData.jobs)) {
            setRenderJobs(renderData.jobs.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load render jobs:", error);
        }

        // Load proof items
        try {
          const proofResponse = await fetch("/api/v1/proof/items");
          const proofData = await proofResponse.json();
          
          if (proofData.items && Array.isArray(proofData.items)) {
            setProofItems(proofData.items.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load proof items:", error);
        }
      } catch (error) {
        console.error("Failed to load data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

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

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "text-green-600";
      case "processing": return "text-blue-600";
      case "failed": return "text-red-600";
      case "pending": return "text-yellow-600";
      case "review": return "text-purple-600";
      default: return "text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed": return "✓";
      case "processing": return "⟳";
      case "failed": return "✗";
      case "pending": return "⏳";
      case "review": return "👁";
      default: return "?";
    }
  };

  const getReviewStatusColor = (status: string) => {
    switch (status) {
      case "approved": return "text-green-600";
      case "rejected": return "text-red-600";
      case "pending": return "text-yellow-600";
      default: return "text-gray-600";
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Batch Review & Render Jobs</h3>
        <div className="text-center py-8">
          <div className="text-gray-500">Loading batch and render data...</div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab("batch")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "batch"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Batch Jobs ({batchJobs.length})
          </button>
          <button
            onClick={() => setActiveTab("render")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "render"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Render Jobs ({renderJobs.length})
          </button>
          <button
            onClick={() => setActiveTab("proof")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "proof"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Proof Items ({proofItems.length})
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "batch" && (
        <div className="space-y-4">
          {batchJobs.length > 0 ? (
            batchJobs.map((job) => (
              <Card key={job.id} className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{job.name}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(job.status)} bg-gray-100`}>
                        {getStatusIcon(job.status)} {job.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Total Clips:</span> {job.total_clips}
                      </div>
                      <div>
                        <span className="font-medium">Completed:</span> {job.completed_clips}
                      </div>
                      <div>
                        <span className="font-medium">Failed:</span> {job.failed_clips}
                      </div>
                      <div>
                        <span className="font-medium">Duration:</span> {job.settings.clip_duration}s
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Created: {formatDate(job.created_at)}
                      {job.completed_at && (
                        <span className="ml-4">Completed: {formatDate(job.completed_at)}</span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      <span className="font-medium">Source Assets:</span> {job.source_assets.join(", ")}
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${job.total_clips > 0 ? (job.completed_clips / job.total_clips) * 100 : 0}%`
                        }}
                      />
                    </div>
                    <div className="space-y-2">
                      <Button variant="secondary" size="sm" className="w-full">
                        View Details
                      </Button>
                      {job.status === "completed" && (
                        <Button variant="secondary" size="sm" className="w-full">
                          Export Results
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No batch jobs found
            </div>
          )}
        </div>
      )}

      {activeTab === "render" && (
        <div className="space-y-4">
          {renderJobs.length > 0 ? (
            renderJobs.map((job) => (
              <Card key={job.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{job.clip_title}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(job.status)} bg-gray-100`}>
                        {getStatusIcon(job.status)} {job.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Resolution:</span> {job.render_settings.resolution}
                      </div>
                      <div>
                        <span className="font-medium">Format:</span> {job.render_settings.format}
                      </div>
                      <div>
                        <span className="font-medium">Quality:</span> {job.render_settings.quality}
                      </div>
                      {job.batch_job_id && (
                        <div>
                          <span className="font-medium">Batch Job:</span> {job.batch_job_id}
                        </div>
                      )}
                    </div>
                    <div className="text-sm text-gray-500 mb-2">
                      Created: {formatDate(job.created_at)}
                      {job.completed_at && (
                        <span className="ml-4">Completed: {formatDate(job.completed_at)}</span>
                      )}
                    </div>
                    {job.error_message && (
                      <div className="text-sm text-red-600 mb-2">
                        <span className="font-medium">Error:</span> {job.error_message}
                      </div>
                    )}
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
                  <div className="ml-4 space-y-2">
                    {job.output_url && (
                      <Button variant="secondary" size="sm">
                        Download
                      </Button>
                    )}
                    <Button variant="secondary" size="sm" disabled={job.status === "processing"}>
                      {job.status === "processing" ? "Rendering..." : "Retry"}
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No render jobs found
            </div>
          )}
        </div>
      )}

      {activeTab === "proof" && (
        <div className="space-y-4">
          {proofItems.length > 0 ? (
            proofItems.map((item) => (
              <Card key={item.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{item.clip_title}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(item.status)} bg-gray-100`}>
                        {getStatusIcon(item.status)} {item.status}
                      </span>
                      <span className={`text-sm px-2 py-1 rounded ${getReviewStatusColor(item.review_status)} bg-gray-100`}>
                        {item.review_status}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Duration:</span> {formatDuration(item.metadata.duration)}
                      </div>
                      <div>
                        <span className="font-medium">Size:</span> {formatFileSize(item.metadata.file_size)}
                      </div>
                      <div>
                        <span className="font-medium">Tags:</span> {item.metadata.tags.join(", ")}
                      </div>
                      <div>
                        <span className="font-medium">Created:</span> {formatDate(item.created_at)}
                      </div>
                    </div>
                    {item.thumbnail_url && (
                      <div className="mt-2">
                        <img
                          src={item.thumbnail_url}
                          alt={item.clip_title}
                          className="w-32 h-20 object-cover rounded"
                        />
                      </div>
                    )}
                  </div>
                  <div className="ml-4 space-y-2">
                    {item.video_url && (
                      <Button variant="secondary" size="sm">
                        Preview
                      </Button>
                    )}
                    <Button variant="secondary" size="sm">
                      {item.review_status === "pending" ? "Review" : "View Details"}
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No proof items found
            </div>
          )}
        </div>
      )}

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Button variant="secondary" size="sm">
            Create Batch Job
          </Button>
          <Button variant="secondary" size="sm">
            Queue Renders
          </Button>
          <Button variant="secondary" size="sm">
            Review Queue
          </Button>
          <Button variant="secondary" size="sm">
            Export Package
          </Button>
        </div>
      </Card>
    </div>
  );
}
