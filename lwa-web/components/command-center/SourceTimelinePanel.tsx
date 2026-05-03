"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";

interface SourceAsset {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  duration?: number;
  resolution?: string;
  uploaded_at: string;
  status: string;
  thumbnail_url?: string;
}

interface TimelinePlan {
  id: string;
  source_asset_id: string;
  title: string;
  description: string;
  total_duration: number;
  segments: TimelineSegment[];
  created_at: string;
  status: string;
}

interface TimelineSegment {
  id: string;
  start_time: number;
  end_time: number;
  segment_type: string;
  content_description: string;
  priority: string;
}

interface IngestJob {
  id: string;
  source_url: string;
  status: string;
  progress?: number;
  created_at: string;
  error_message?: string;
}

export function SourceTimelinePanel() {
  const [sourceAssets, setSourceAssets] = useState<SourceAsset[]>([]);
  const [timelinePlans, setTimelinePlans] = useState<TimelinePlan[]>([]);
  const [ingestJobs, setIngestJobs] = useState<IngestJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"assets" | "timeline" | "ingest">("assets");

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load source assets
        try {
          const assetsResponse = await fetch("/api/v1/source-assets");
          const assetsData = await assetsResponse.json();
          
          if (assetsData.assets && Array.isArray(assetsData.assets)) {
            setSourceAssets(assetsData.assets.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load source assets:", error);
        }

        // Load timeline plans
        try {
          const timelineResponse = await fetch("/api/v1/timeline/plans");
          const timelineData = await timelineResponse.json();
          
          if (timelineData.plans && Array.isArray(timelineData.plans)) {
            setTimelinePlans(timelineData.plans.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load timeline plans:", error);
        }

        // Load ingest jobs
        try {
          const ingestResponse = await fetch("/api/v1/ingest/jobs");
          const ingestData = await ingestResponse.json();
          
          if (ingestData.jobs && Array.isArray(ingestData.jobs)) {
            setIngestJobs(ingestData.jobs.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load ingest jobs:", error);
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
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "text-green-600";
      case "processing": return "text-blue-600";
      case "failed": return "text-red-600";
      case "pending": return "text-yellow-600";
      default: return "text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed": return "✓";
      case "processing": return "⟳";
      case "failed": return "✗";
      case "pending": return "⏳";
      default: return "?";
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Source Assets & Timeline</h3>
        <div className="text-center py-8">
          <div className="text-gray-500">Loading source and timeline data...</div>
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
            onClick={() => setActiveTab("assets")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "assets"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Source Assets ({sourceAssets.length})
          </button>
          <button
            onClick={() => setActiveTab("timeline")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "timeline"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Timeline Plans ({timelinePlans.length})
          </button>
          <button
            onClick={() => setActiveTab("ingest")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "ingest"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Ingest Jobs ({ingestJobs.length})
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "assets" && (
        <div className="space-y-4">
          {sourceAssets.length > 0 ? (
            sourceAssets.map((asset) => (
              <Card key={asset.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{asset.filename}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(asset.status)} bg-gray-100`}>
                        {getStatusIcon(asset.status)} {asset.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">Type:</span> {asset.file_type}
                      </div>
                      <div>
                        <span className="font-medium">Size:</span> {formatFileSize(asset.file_size)}
                      </div>
                      {asset.duration && (
                        <div>
                          <span className="font-medium">Duration:</span> {formatDuration(asset.duration)}
                        </div>
                      )}
                      {asset.resolution && (
                        <div>
                          <span className="font-medium">Resolution:</span> {asset.resolution}
                        </div>
                      )}
                    </div>
                    <div className="mt-2 text-sm text-gray-500">
                      Uploaded: {formatDate(asset.uploaded_at)}
                    </div>
                  </div>
                  <div className="ml-4 space-y-2">
                    <Button variant="secondary" size="sm">
                      Create Timeline
                    </Button>
                    <Button variant="secondary" size="sm">
                      Generate Clips
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No source assets found
            </div>
          )}
        </div>
      )}

      {activeTab === "timeline" && (
        <div className="space-y-4">
          {timelinePlans.length > 0 ? (
            timelinePlans.map((plan) => (
              <Card key={plan.id} className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-medium">{plan.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{plan.description}</p>
                  </div>
                  <span className={`text-sm px-2 py-1 rounded ${getStatusColor(plan.status)} bg-gray-100`}>
                    {getStatusIcon(plan.status)} {plan.status}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-3">
                  <div>
                    <span className="font-medium">Total Duration:</span> {formatDuration(plan.total_duration)}
                  </div>
                  <div>
                    <span className="font-medium">Segments:</span> {plan.segments.length}
                  </div>
                  <div>
                    <span className="font-medium">Created:</span> {formatDate(plan.created_at)}
                  </div>
                </div>

                {plan.segments.length > 0 && (
                  <div className="border-t pt-3">
                    <h5 className="font-medium text-sm mb-2">Timeline Segments</h5>
                    <div className="space-y-2">
                      {plan.segments.slice(0, 3).map((segment) => (
                        <div key={segment.id} className="flex items-center justify-between text-sm bg-gray-50 p-2 rounded">
                          <div>
                            <span className="font-medium">{formatDuration(segment.start_time)} - {formatDuration(segment.end_time)}</span>
                            <span className="ml-2 text-gray-600">{segment.segment_type}</span>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs ${
                            segment.priority === "high" ? "bg-red-100 text-red-700" :
                            segment.priority === "medium" ? "bg-yellow-100 text-yellow-700" :
                            "bg-green-100 text-green-700"
                          }`}>
                            {segment.priority}
                          </span>
                        </div>
                      ))}
                      {plan.segments.length > 3 && (
                        <div className="text-sm text-gray-500 text-center">
                          +{plan.segments.length - 3} more segments
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="mt-3 flex gap-2">
                  <Button variant="secondary" size="sm">
                    Edit Timeline
                  </Button>
                  <Button variant="secondary" size="sm">
                    Render Video
                  </Button>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No timeline plans found
            </div>
          )}
        </div>
      )}

      {activeTab === "ingest" && (
        <div className="space-y-4">
          {ingestJobs.length > 0 ? (
            ingestJobs.map((job) => (
              <Card key={job.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{job.id}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(job.status)} bg-gray-100`}>
                        {getStatusIcon(job.status)} {job.status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 mb-2">
                      <p><span className="font-medium">Source:</span> {job.source_url}</p>
                      <p><span className="font-medium">Created:</span> {formatDate(job.created_at)}</p>
                      {job.error_message && (
                        <p className="text-red-600 mt-1"><span className="font-medium">Error:</span> {job.error_message}</p>
                      )}
                    </div>
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
                  <div className="ml-4">
                    <Button variant="secondary" size="sm" disabled={job.status === "processing"}>
                      {job.status === "processing" ? "Processing..." : "Retry"}
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No ingest jobs found
            </div>
          )}
        </div>
      )}

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Button variant="secondary" size="sm">
            Upload Source
          </Button>
          <Button variant="secondary" size="sm">
            Create Timeline
          </Button>
          <Button variant="secondary" size="sm">
            Batch Ingest
          </Button>
          <Button variant="secondary" size="sm">
            View All Assets
          </Button>
        </div>
      </Card>
    </div>
  );
}
