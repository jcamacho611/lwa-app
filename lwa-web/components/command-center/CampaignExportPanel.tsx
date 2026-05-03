"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";

interface Campaign {
  id: string;
  name: string;
  description: string;
  platforms: string[];
  status: string;
  created_at: string;
  total_clips: number;
  exported_clips: number;
  export_settings: {
    formats: string[];
        quality: string;
        include_captions: boolean;
        include_thumbnails: boolean;
    };
}

interface ExportPackage {
  id: string;
  campaign_id: string;
  package_name: string;
  status: string;
  created_at: string;
  completed_at?: string;
  file_count: number;
  total_size: number;
  download_url?: string;
  formats: string[];
}

interface FeedbackInsight {
  id: string;
  campaign_id?: string;
  insight_type: string;
  title: string;
  description: string;
  confidence_score: number;
  impact_level: string;
  created_at: string;
  applied: boolean;
  recommendations: string[];
}

interface LearningMetric {
  metric_name: string;
  current_value: number;
  previous_value: number;
  change_percentage: number;
  trend: string;
  last_updated: string;
}

export function CampaignExportPanel() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [exportPackages, setExportPackages] = useState<ExportPackage[]>([]);
  const [insights, setInsights] = useState<FeedbackInsight[]>([]);
  const [metrics, setMetrics] = useState<LearningMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"campaigns" | "exports" | "feedback" | "metrics">("campaigns");

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load campaigns
        try {
          const campaignsResponse = await fetch("/api/v1/campaigns");
          const campaignsData = await campaignsResponse.json();
          
          if (campaignsData.campaigns && Array.isArray(campaignsData.campaigns)) {
            setCampaigns(campaignsData.campaigns.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load campaigns:", error);
        }

        // Load export packages
        try {
          const exportsResponse = await fetch("/api/v1/export/packages");
          const exportsData = await exportsResponse.json();
          
          if (exportsData.packages && Array.isArray(exportsData.packages)) {
            setExportPackages(exportsData.packages.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load export packages:", error);
        }

        // Load feedback insights
        try {
          const insightsResponse = await fetch("/api/v1/feedback/insights");
          const insightsData = await insightsResponse.json();
          
          if (insightsData.insights && Array.isArray(insightsData.insights)) {
            setInsights(insightsData.insights.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load feedback insights:", error);
        }

        // Load learning metrics
        try {
          const metricsResponse = await fetch("/api/v1/learning/metrics");
          const metricsData = await metricsResponse.json();
          
          if (metricsData.metrics && Array.isArray(metricsData.metrics)) {
            setMetrics(metricsData.metrics);
          }
        } catch (error) {
          console.error("Failed to load learning metrics:", error);
        }
      } catch (error) {
        console.error("Failed to load campaign export data:", error);
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "text-green-600";
      case "completed": return "text-blue-600";
      case "processing": return "text-yellow-600";
      case "failed": return "text-red-600";
      case "pending": return "text-gray-600";
      default: return "text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active": return "✓";
      case "completed": return "✓";
      case "processing": return "⟳";
      case "failed": return "✗";
      case "pending": return "⏳";
      default: return "?";
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "high": return "text-red-600";
      case "medium": return "text-yellow-600";
      case "low": return "text-green-600";
      default: return "text-gray-600";
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up": return "📈";
      case "down": return "📉";
      case "stable": return "➡️";
      default: return "?";
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "up": return "text-green-600";
      case "down": return "text-red-600";
      case "stable": return "text-gray-600";
      default: return "text-gray-600";
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Campaign Export & Feedback Learning</h3>
        <div className="text-center py-8">
          <div className="text-gray-500">Loading campaign and feedback data...</div>
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
            onClick={() => setActiveTab("campaigns")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "campaigns"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Campaigns ({campaigns.length})
          </button>
          <button
            onClick={() => setActiveTab("exports")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "exports"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Export Packages ({exportPackages.length})
          </button>
          <button
            onClick={() => setActiveTab("feedback")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "feedback"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Feedback Insights ({insights.length})
          </button>
          <button
            onClick={() => setActiveTab("metrics")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "metrics"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Learning Metrics ({metrics.length})
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "campaigns" && (
        <div className="space-y-4">
          {campaigns.length > 0 ? (
            campaigns.map((campaign) => (
              <Card key={campaign.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{campaign.name}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(campaign.status)} bg-gray-100`}>
                        {getStatusIcon(campaign.status)} {campaign.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{campaign.description}</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Platforms:</span> {campaign.platforms.join(", ")}
                      </div>
                      <div>
                        <span className="font-medium">Total Clips:</span> {campaign.total_clips}
                      </div>
                      <div>
                        <span className="font-medium">Exported:</span> {campaign.exported_clips}
                      </div>
                      <div>
                        <span className="font-medium">Created:</span> {formatDate(campaign.created_at)}
                      </div>
                    </div>
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Export Settings:</span> {campaign.export_settings.formats.join(", ")}, {campaign.export_settings.quality}
                      {campaign.export_settings.include_captions && ", captions"}
                      {campaign.export_settings.include_thumbnails && ", thumbnails"}
                    </div>
                  </div>
                  <div className="ml-4 space-y-2">
                    <Button variant="secondary" size="sm">
                      View Details
                    </Button>
                    <Button variant="secondary" size="sm">
                      Export Package
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No campaigns found
            </div>
          )}
        </div>
      )}

      {activeTab === "exports" && (
        <div className="space-y-4">
          {exportPackages.length > 0 ? (
            exportPackages.map((pkg) => (
              <Card key={pkg.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{pkg.package_name}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(pkg.status)} bg-gray-100`}>
                        {getStatusIcon(pkg.status)} {pkg.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Files:</span> {pkg.file_count}
                      </div>
                      <div>
                        <span className="font-medium">Size:</span> {formatFileSize(pkg.total_size)}
                      </div>
                      <div>
                        <span className="font-medium">Formats:</span> {pkg.formats.join(", ")}
                      </div>
                      <div>
                        <span className="font-medium">Created:</span> {formatDate(pkg.created_at)}
                      </div>
                    </div>
                    {pkg.completed_at && (
                      <div className="text-sm text-gray-500">
                        Completed: {formatDate(pkg.completed_at)}
                      </div>
                    )}
                  </div>
                  <div className="ml-4 space-y-2">
                    {pkg.download_url && (
                      <Button variant="secondary" size="sm">
                        Download
                      </Button>
                    )}
                    <Button variant="secondary" size="sm">
                      View Details
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No export packages found
            </div>
          )}
        </div>
      )}

      {activeTab === "feedback" && (
        <div className="space-y-4">
          {insights.length > 0 ? (
            insights.map((insight) => (
              <Card key={insight.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{insight.title}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getImpactColor(insight.impact_level)} bg-gray-100`}>
                        {insight.impact_level} impact
                      </span>
                      <span className={`text-sm px-2 py-1 rounded ${insight.applied ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                        {insight.applied ? "Applied" : "Pending"}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{insight.description}</p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Type:</span> {insight.insight_type}
                      </div>
                      <div>
                        <span className="font-medium">Confidence:</span> {Math.round(insight.confidence_score * 100)}%
                      </div>
                      <div>
                        <span className="font-medium">Created:</span> {formatDate(insight.created_at)}
                      </div>
                    </div>
                    {insight.recommendations.length > 0 && (
                      <div className="text-sm text-gray-600">
                        <span className="font-medium">Recommendations:</span> {insight.recommendations.join(", ")}
                      </div>
                    )}
                  </div>
                  <div className="ml-4 space-y-2">
                    <Button variant="secondary" size="sm">
                      View Details
                    </Button>
                    {!insight.applied && (
                      <Button variant="secondary" size="sm">
                        Apply Insight
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No feedback insights found
            </div>
          )}
        </div>
      )}

      {activeTab === "metrics" && (
        <div className="space-y-4">
          {metrics.length > 0 ? (
            metrics.map((metric, index) => (
              <Card key={index} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium mb-2">{metric.metric_name}</h4>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Current:</span> {metric.current_value}
                      </div>
                      <div>
                        <span className="font-medium">Previous:</span> {metric.previous_value}
                      </div>
                      <div>
                        <span className="font-medium">Change:</span>
                        <span className={metric.change_percentage >= 0 ? "text-green-600" : "text-red-600"}>
                          {metric.change_percentage >= 0 ? "+" : ""}{metric.change_percentage}%
                        </span>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500 mt-2">
                      Last updated: {formatDate(metric.last_updated)}
                    </div>
                  </div>
                  <div className="ml-4 text-center">
                    <div className={`text-2xl mb-1 ${getTrendColor(metric.trend)}`}>
                      {getTrendIcon(metric.trend)}
                    </div>
                    <div className="text-sm text-gray-600">
                      {metric.trend}
                    </div>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No learning metrics found
            </div>
          )}
        </div>
      )}

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Button variant="secondary" size="sm">
            Create Campaign
          </Button>
          <Button variant="secondary" size="sm">
            Export Package
          </Button>
          <Button variant="secondary" size="sm">
            Generate Insights
          </Button>
          <Button variant="secondary" size="sm">
            View Analytics
          </Button>
        </div>
      </Card>
    </div>
  );
}
