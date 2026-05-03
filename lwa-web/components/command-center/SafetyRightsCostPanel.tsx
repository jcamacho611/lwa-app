"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";
import { runSafetyCheck } from "../../lib/api";

interface SafetyCheck {
  overall_safe: boolean;
  safety_score: number;
  issues: any[];
  warnings: any[];
  recommendations: string[];
}

interface RightsCheck {
  rights_clear: boolean;
  rights_score: number;
  issues: any[];
  warnings: any[];
  clearance_status: string;
  attribution_required: boolean;
}

interface CostEstimate {
  estimated_cost: number;
  cost_breakdown: {
    rendering: number;
    storage: number;
    bandwidth: number;
    platform_fees: number;
  };
  cost_factors: string[];
}

interface CheckHistory {
  id: string;
  content_type: string;
  platform: string;
  safety_score: number;
  rights_score: number;
  estimated_cost: number;
  checked_at: string;
  status: string;
}

export function SafetyRightsCostPanel() {
  const [checkHistory, setCheckHistory] = useState<CheckHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"check" | "history" | "guidelines">("check");
  const [currentCheck, setCurrentCheck] = useState<{
    safety?: SafetyCheck;
    rights?: RightsCheck;
    cost?: CostEstimate;
  } | null>(null);
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        // Mock check history data
        const history: CheckHistory[] = [
          {
            id: "check_1",
            content_type: "video",
            platform: "tiktok",
            safety_score: 0.92,
            rights_score: 0.88,
            estimated_cost: 0.00,
            checked_at: "2026-05-03T12:00:00Z",
            status: "safe"
          },
          {
            id: "check_2",
            content_type: "video",
            platform: "youtube",
            safety_score: 0.89,
            rights_score: 0.91,
            estimated_cost: 2.50,
            checked_at: "2026-05-03T10:30:00Z",
            status: "safe"
          },
          {
            id: "check_3",
            content_type: "image",
            platform: "instagram",
            safety_score: 0.95,
            rights_score: 0.93,
            estimated_cost: 0.00,
            checked_at: "2026-05-03T08:15:00Z",
            status: "safe"
          }
        ];
        
        setCheckHistory(history);
      } catch (error) {
        console.error("Failed to load check history:", error);
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return "text-green-600";
    if (score >= 0.8) return "text-yellow-600";
    if (score >= 0.7) return "text-orange-600";
    return "text-red-600";
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "safe": return "text-green-600";
      case "caution": return "text-yellow-600";
      case "risky": return "text-orange-600";
      case "blocked": return "text-red-600";
      default: return "text-gray-600";
    }
  };

  const handleSafetyCheck = async (contentType: string, platform: string) => {
    setChecking(true);
    try {
      const result = await runSafetyCheck(contentType, {}, platform);
      setCurrentCheck(result);
    } catch (error) {
      console.error("Safety check failed:", error);
    } finally {
      setChecking(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Safety, Rights & Cost</h3>
        <div className="text-center py-8">
          <div className="text-gray-500">Loading safety and rights data...</div>
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
            onClick={() => setActiveTab("check")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "check"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Run Check
          </button>
          <button
            onClick={() => setActiveTab("history")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "history"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            History ({checkHistory.length})
          </button>
          <button
            onClick={() => setActiveTab("guidelines")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "guidelines"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Guidelines
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "check" && (
        <div className="space-y-4">
          <Card className="p-4">
            <h4 className="font-medium mb-4">Run Safety, Rights & Cost Check</h4>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Content Type
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="video">Video</option>
                  <option value="image">Image</option>
                  <option value="audio">Audio</option>
                  <option value="text">Text</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Platform
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="tiktok">TikTok</option>
                  <option value="youtube">YouTube</option>
                  <option value="instagram">Instagram</option>
                  <option value="twitter">Twitter</option>
                </select>
              </div>
            </div>
            <div className="mt-4">
              <Button 
                variant="secondary" 
                onClick={() => handleSafetyCheck("video", "tiktok")}
                disabled={checking}
              >
                {checking ? "Checking..." : "Run Safety Check"}
              </Button>
            </div>
          </Card>

          {currentCheck && (
            <div className="space-y-4">
              {currentCheck.safety && (
                <Card className="p-4">
                  <h4 className="font-medium mb-3">Safety Analysis</h4>
                  <div className="grid grid-cols-2 gap-4 mb-3">
                    <div>
                      <span className="text-sm text-gray-600">Overall Safe:</span>
                      <span className={`ml-2 font-medium ${currentCheck.safety.overall_safe ? "text-green-600" : "text-red-600"}`}>
                        {currentCheck.safety.overall_safe ? "Yes" : "No"}
                      </span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Safety Score:</span>
                      <span className={`ml-2 font-medium ${getScoreColor(currentCheck.safety.safety_score)}`}>
                        {Math.round(currentCheck.safety.safety_score * 100)}%
                      </span>
                    </div>
                  </div>
                  {currentCheck.safety.warnings.length > 0 && (
                    <div className="mb-3">
                      <h5 className="text-sm font-medium mb-2">Warnings:</h5>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {currentCheck.safety.warnings.map((warning, index) => (
                          <li key={index} className="flex items-center gap-2">
                            <span className="text-yellow-500">⚠️</span>
                            {warning.message || warning}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {currentCheck.safety.recommendations.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium mb-2">Recommendations:</h5>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {currentCheck.safety.recommendations.map((rec, index) => (
                          <li key={index} className="flex items-center gap-2">
                            <span className="text-blue-500">→</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </Card>
              )}

              {currentCheck.rights && (
                <Card className="p-4">
                  <h4 className="font-medium mb-3">Rights Clearance</h4>
                  <div className="grid grid-cols-2 gap-4 mb-3">
                    <div>
                      <span className="text-sm text-gray-600">Rights Clear:</span>
                      <span className={`ml-2 font-medium ${currentCheck.rights.rights_clear ? "text-green-600" : "text-red-600"}`}>
                        {currentCheck.rights.rights_clear ? "Yes" : "No"}
                      </span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Rights Score:</span>
                      <span className={`ml-2 font-medium ${getScoreColor(currentCheck.rights.rights_score)}`}>
                        {Math.round(currentCheck.rights.rights_score * 100)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Clearance Status:</span>
                      <span className={`ml-2 font-medium ${getStatusColor(currentCheck.rights.clearance_status)}`}>
                        {currentCheck.rights.clearance_status.replace("_", " ")}
                      </span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Attribution Required:</span>
                      <span className={`ml-2 font-medium ${currentCheck.rights.attribution_required ? "text-orange-600" : "text-green-600"}`}>
                        {currentCheck.rights.attribution_required ? "Yes" : "No"}
                      </span>
                    </div>
                  </div>
                </Card>
              )}

              {currentCheck.cost && (
                <Card className="p-4">
                  <h4 className="font-medium mb-3">Cost Estimation</h4>
                  <div className="grid grid-cols-2 gap-4 mb-3">
                    <div>
                      <span className="text-sm text-gray-600">Estimated Cost:</span>
                      <span className={`ml-2 font-medium ${currentCheck.cost.estimated_cost > 0 ? "text-orange-600" : "text-green-600"}`}>
                        {formatCurrency(currentCheck.cost.estimated_cost)}
                      </span>
                    </div>
                  </div>
                  <div className="space-y-2 mb-3">
                    <h5 className="text-sm font-medium">Cost Breakdown:</h5>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="flex justify-between">
                        <span>Rendering:</span>
                        <span>{formatCurrency(currentCheck.cost.cost_breakdown.rendering)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Storage:</span>
                        <span>{formatCurrency(currentCheck.cost.cost_breakdown.storage)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Bandwidth:</span>
                        <span>{formatCurrency(currentCheck.cost.cost_breakdown.bandwidth)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Platform Fees:</span>
                        <span>{formatCurrency(currentCheck.cost.cost_breakdown.platform_fees)}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h5 className="text-sm font-medium mb-2">Cost Factors:</h5>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {currentCheck.cost.cost_factors.map((factor, index) => (
                        <li key={index} className="flex items-center gap-2">
                          <span className="text-green-500">✓</span>
                          {factor}
                        </li>
                      ))}
                    </ul>
                  </div>
                </Card>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === "history" && (
        <div className="space-y-4">
          {checkHistory.length > 0 ? (
            checkHistory.map((check) => (
              <Card key={check.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{check.content_type} - {check.platform}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(check.status)} bg-gray-100`}>
                        {check.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Safety Score:</span>
                        <span className={`ml-2 font-medium ${getScoreColor(check.safety_score)}`}>
                          {Math.round(check.safety_score * 100)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Rights Score:</span>
                        <span className={`ml-2 font-medium ${getScoreColor(check.rights_score)}`}>
                          {Math.round(check.rights_score * 100)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Cost:</span>
                        <span className={`ml-2 font-medium ${check.estimated_cost > 0 ? "text-orange-600" : "text-green-600"}`}>
                          {formatCurrency(check.estimated_cost)}
                        </span>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500 mt-2">
                      Checked: {formatDate(check.checked_at)}
                    </div>
                  </div>
                  <div className="ml-4">
                    <Button variant="secondary" size="sm">
                      View Details
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No check history found
            </div>
          )}
        </div>
      )}

      {activeTab === "guidelines" && (
        <div className="space-y-4">
          <Card className="p-4">
            <h4 className="font-medium mb-3">Platform Guidelines</h4>
            <div className="space-y-4">
              <div>
                <h5 className="text-sm font-medium mb-2">TikTok</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Max duration: 60 seconds</li>
                  <li>• Aspect ratios: 9:16, 1:1</li>
                  <li>• No copyrighted music without license</li>
                  <li>• Community guidelines strictly enforced</li>
                </ul>
              </div>
              <div>
                <h5 className="text-sm font-medium mb-2">YouTube</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Max duration: 15 minutes (standard)</li>
                  <li>• Aspect ratios: 16:9, 9:16</li>
                  <li>• Content ID system for copyright detection</li>
                  <li>• Monetization requirements apply</li>
                </ul>
              </div>
              <div>
                <h5 className="text-sm font-medium mb-2">Instagram</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Max duration: 90 seconds (Reels)</li>
                  <li>• Aspect ratios: 9:16, 4:5, 1:1</li>
                  <li>• Music licensing through library</li>
                  <li>• Brand partnership disclosures required</li>
                </ul>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <h4 className="font-medium mb-3">Content Safety Best Practices</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h5 className="text-sm font-medium mb-2">Pre-Upload Checklist</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Check for copyrighted material</li>
                  <li>• Verify age-appropriate content</li>
                  <li>• Ensure proper attribution</li>
                  <li>• Review platform guidelines</li>
                  <li>• Check technical specifications</li>
                </ul>
              </div>
              <div>
                <h5 className="text-sm font-medium mb-2">Rights Management</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Use royalty-free music when possible</li>
                  <li>• Document content sources</li>
                  <li>• Keep permission records</li>
                  <li>• Monitor for DMCA claims</li>
                  <li>• Understand fair use limitations</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Button variant="secondary" size="sm">
            Batch Check
          </Button>
          <Button variant="secondary" size="sm">
            Export Report
          </Button>
          <Button variant="secondary" size="sm">
            Update Guidelines
          </Button>
          <Button variant="secondary" size="sm">
            Cost Calculator
          </Button>
        </div>
      </Card>
    </div>
  );
}
