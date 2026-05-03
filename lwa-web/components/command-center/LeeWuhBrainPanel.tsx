"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";

interface GuidanceMessage {
  id: string;
  type: string;
  message: string;
  context: string;
  priority: string;
  created_at: string;
  action_suggestions: string[];
}

interface CouncilMember {
  id: string;
  name: string;
  role: string;
  expertise: string[];
  status: string;
  avatar_url?: string;
}

interface BrainState {
  consciousness_level: number;
  processing_power: number;
  knowledge_domains: string[];
  active_council_members: number;
  total_guidance_given: number;
  last_updated: string;
}

export function LeeWuhBrainPanel() {
  const [guidanceMessages, setGuidanceMessages] = useState<GuidanceMessage[]>([]);
  const [councilMembers, setCouncilMembers] = useState<CouncilMember[]>([]);
  const [brainState, setBrainState] = useState<BrainState | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"guidance" | "council" | "brain">("guidance");

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load guidance messages
        try {
          const guidanceResponse = await fetch("/api/v1/lee-wuh/guidance");
          const guidanceData = await guidanceResponse.json();
          
          if (guidanceData.messages && Array.isArray(guidanceData.messages)) {
            setGuidanceMessages(guidanceData.messages.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load guidance messages:", error);
        }

        // Load council members
        try {
          const councilResponse = await fetch("/api/v1/lee-wuh/council");
          const councilData = await councilResponse.json();
          
          if (councilData.members && Array.isArray(councilData.members)) {
            setCouncilMembers(councilData.members);
          }
        } catch (error) {
          console.error("Failed to load council members:", error);
        }

        // Load brain state
        try {
          const brainResponse = await fetch("/api/v1/lee-wuh/brain-state");
          const brainData = await brainResponse.json();
          
          if (brainData.state) {
            setBrainState(brainData.state);
          }
        } catch (error) {
          console.error("Failed to load brain state:", error);
        }
      } catch (error) {
        console.error("Failed to load Lee-Wuh brain data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical": return "text-red-600";
      case "high": return "text-orange-600";
      case "medium": return "text-yellow-600";
      case "low": return "text-green-600";
      default: return "text-gray-600";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "text-green-600";
      case "processing": return "text-blue-600";
      case "idle": return "text-gray-600";
      case "offline": return "text-red-600";
      default: return "text-gray-600";
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "strategy": return "🧠";
      case "creative": return "🎨";
      case "technical": return "⚙️";
      case "safety": return "🛡️";
      case "optimization": return "📈";
      case "warning": return "⚠️";
      default: return "💡";
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Lee-Wuh Brain & Council</h3>
        <div className="text-center py-8">
          <div className="text-gray-500">Loading Lee-Wuh brain data...</div>
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
            onClick={() => setActiveTab("guidance")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "guidance"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Guidance ({guidanceMessages.length})
          </button>
          <button
            onClick={() => setActiveTab("council")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "council"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Council ({councilMembers.length})
          </button>
          <button
            onClick={() => setActiveTab("brain")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "brain"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Brain State
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "guidance" && (
        <div className="space-y-4">
          {guidanceMessages.length > 0 ? (
            guidanceMessages.map((message) => (
              <Card key={message.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">{getTypeIcon(message.type)}</span>
                      <h4 className="font-medium">{message.context}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getPriorityColor(message.priority)} bg-gray-100`}>
                        {message.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-3">{message.message}</p>
                    {message.action_suggestions.length > 0 && (
                      <div className="mb-3">
                        <h5 className="text-sm font-medium mb-2">Suggested Actions:</h5>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {message.action_suggestions.map((suggestion, index) => (
                            <li key={index} className="flex items-center gap-2">
                              <span className="text-purple-500">→</span>
                              {suggestion}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <div className="text-sm text-gray-500">
                      {formatDate(message.created_at)}
                    </div>
                  </div>
                  <div className="ml-4 space-y-2">
                    <Button variant="secondary" size="sm">
                      Apply Guidance
                    </Button>
                    <Button variant="secondary" size="sm">
                      View Details
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No guidance messages available
            </div>
          )}
        </div>
      )}

      {activeTab === "council" && (
        <div className="space-y-4">
          {councilMembers.length > 0 ? (
            councilMembers.map((member) => (
              <Card key={member.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                      {member.avatar_url ? (
                        <img
                          src={member.avatar_url}
                          alt={member.name}
                          className="w-10 h-10 rounded-full"
                        />
                      ) : (
                        <span className="text-purple-600 font-bold">
                          {member.name.charAt(0)}
                        </span>
                      )}
                    </div>
                    <div>
                      <h4 className="font-medium">{member.name}</h4>
                      <p className="text-sm text-gray-600">{member.role}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-sm px-2 py-1 rounded ${getStatusColor(member.status)} bg-gray-100`}>
                          {member.status}
                        </span>
                        <span className="text-sm text-gray-500">
                          Expertise: {member.expertise.join(", ")}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Button variant="secondary" size="sm">
                      Consult
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No council members available
            </div>
          )}
        </div>
      )}

      {activeTab === "brain" && brainState && (
        <div className="space-y-4">
          <Card className="p-6">
            <h4 className="font-medium mb-4">Brain State Overview</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round(brainState.consciousness_level * 100)}%
                </div>
                <div className="text-sm text-gray-600">Consciousness Level</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {Math.round(brainState.processing_power * 100)}%
                </div>
                <div className="text-sm text-gray-600">Processing Power</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {brainState.active_council_members}
                </div>
                <div className="text-sm text-gray-600">Active Council Members</div>
              </div>
            </div>
            <div className="mt-4">
              <div className="text-sm text-gray-600 mb-2">Knowledge Domains:</div>
              <div className="flex flex-wrap gap-2">
                {brainState.knowledge_domains.map((domain, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-sm"
                  >
                    {domain}
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-4 text-sm text-gray-500">
              Total Guidance Given: {brainState.total_guidance_given} | 
              Last Updated: {formatDate(brainState.last_updated)}
            </div>
          </Card>

          <Card className="p-6">
            <h4 className="font-medium mb-4">Brain Capabilities</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h5 className="text-sm font-medium text-gray-700">Core Functions</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Strategic content analysis</li>
                  <li>• Creative direction guidance</li>
                  <li>• Technical optimization</li>
                  <li>• Safety and compliance checking</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h5 className="text-sm font-medium text-gray-700">Learning Systems</h5>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Pattern recognition</li>
                  <li>• Performance optimization</li>
                  <li>• Trend analysis</li>
                  <li>• User preference learning</li>
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
            Request Guidance
          </Button>
          <Button variant="secondary" size="sm">
            Consult Council
          </Button>
          <Button variant="secondary" size="sm">
            Brain Training
          </Button>
          <Button variant="secondary" size="sm">
            Update Knowledge
          </Button>
        </div>
      </Card>
    </div>
  );
}
