"use client";

import { useState, useEffect } from "react";
import { 
  listWorkflowItems,
  executeWorkflowAction,
  executeBulkWorkflowAction,
  getWorkflowSummary,
  getWorkflowCapabilities,
  WorkflowItem,
  WorkflowFilterRequest,
  WorkflowSummary,
  BulkActionRequest
} from "../../lib/api";

interface BatchReviewConsoleProps {
  token: string;
}

export function BatchReviewConsole({ token }: BatchReviewConsoleProps) {
  const [items, setItems] = useState<WorkflowItem[]>([]);
  const [summary, setSummary] = useState<WorkflowSummary | null>(null);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState<WorkflowFilterRequest>({});
  const [capabilities, setCapabilities] = useState<any>(null);

  // Load data on mount
  useEffect(() => {
    if (token) {
      const loadItems = async () => {
        try {
          setIsLoading(true);
          const response = await listWorkflowItems(token, filters);
          setItems(response.items || []);
        } catch (err) {
          console.error("Failed to load workflow items:", err);
          setError("Failed to load workflow items");
        } finally {
          setIsLoading(false);
        }
      };

      const loadSummary = async () => {
        try {
          const response = await getWorkflowSummary(token);
          setSummary(response);
        } catch (err) {
          console.error("Failed to load workflow summary:", err);
        }
      };

      const loadCapabilities = async () => {
        try {
          const response = await getWorkflowCapabilities(token);
          setCapabilities(response);
        } catch (err) {
          console.error("Failed to load capabilities:", err);
        }
      };

      loadItems();
      loadSummary();
      loadCapabilities();
    }
  }, [token, filters]);

  const executeAction = async (itemId: string, actionType: string, notes?: string) => {
    try {
      setIsLoading(true);
      await executeWorkflowAction(token, itemId, { action_type: actionType, notes });
      
      // Reload data
      const itemsResponse = await listWorkflowItems(token, filters);
      setItems(itemsResponse.items || []);
      
      const summaryResponse = await getWorkflowSummary(token);
      setSummary(summaryResponse);
    } catch (err: any) {
      setError(err.message || "Failed to execute action");
    } finally {
      setIsLoading(false);
    }
  };

  const executeBulkAction = async (actionType: string, notes?: string) => {
    if (selectedItems.length === 0) {
      setError("Please select items first");
      return;
    }

    try {
      setIsLoading(true);
      await executeBulkWorkflowAction(token, { item_ids: selectedItems, action_type: actionType, notes });
      setSelectedItems([]);
      
      // Reload data
      const itemsResponse = await listWorkflowItems(token, filters);
      setItems(itemsResponse.items || []);
      
      const summaryResponse = await getWorkflowSummary(token);
      setSummary(summaryResponse);
    } catch (err: any) {
      setError(err.message || "Failed to execute bulk action");
    } finally {
      setIsLoading(false);
    }
  };

  const toggleItemSelection = (itemId: string) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const updateFilter = (newFilters: Partial<WorkflowFilterRequest>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "approved": case "rendered": case "packaged": case "saved_as_proof": return "text-green-400";
      case "new": case "reviewed": case "queued_for_render": case "rendering": return "text-blue-400";
      case "rejected": case "failed": return "text-red-400";
      case "needs_changes": return "text-yellow-400";
      case "archived": return "text-gray-400";
      default: return "text-gray-400";
    }
  };

  const getActionColor = (actionType: string) => {
    switch (actionType) {
      case "approve": return "bg-green-600 hover:bg-green-700";
      case "reject": return "bg-red-600 hover:bg-red-700";
      case "mark_needs_changes": return "bg-yellow-600 hover:bg-yellow-700";
      case "queue_render": return "bg-blue-600 hover:bg-blue-700";
      case "package": return "bg-purple-600 hover:bg-purple-700";
      case "save_as_proof": return "bg-indigo-600 hover:bg-indigo-700";
      case "archive": return "bg-gray-600 hover:bg-gray-700";
      default: return "bg-gray-600 hover:bg-gray-700";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getActionLabel = (actionType: string) => {
    return actionType.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 bg-black text-white min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-yellow-400 to-yellow-600 bg-clip-text text-transparent">
          Batch Workflow Review Console
        </h1>
        <p className="text-gray-400">Approve, reject, and manage your video assets at scale.</p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-900/50 border border-red-600 rounded-lg">
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="text-2xl font-bold text-yellow-400">{summary.total_items}</div>
            <div className="text-sm text-gray-400">Total Items</div>
          </div>
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-400">{summary.needs_review}</div>
            <div className="text-sm text-gray-400">Needs Review</div>
          </div>
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-400">{summary.ready_to_render}</div>
            <div className="text-sm text-gray-400">Ready to Render</div>
          </div>
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="text-2xl font-bold text-purple-400">{summary.approved_items}</div>
            <div className="text-sm text-gray-400">Approved</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-gray-900 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Filters</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Item Type</label>
            <select
              value={filters.item_types?.[0] || ""}
              onChange={(e) => updateFilter({ item_types: e.target.value ? [e.target.value] : undefined })}
              className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
            >
              <option value="">All Types</option>
              {capabilities?.item_types?.map((type: string) => (
                <option key={type} value={type}>{type.replace(/_/g, ' ').toUpperCase()}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Status</label>
            <select
              value={filters.statuses?.[0] || ""}
              onChange={(e) => updateFilter({ statuses: e.target.value ? [e.target.value] : undefined })}
              className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
            >
              <option value="">All Statuses</option>
              {capabilities?.statuses?.map((status: string) => (
                <option key={status} value={status}>{status.replace(/_/g, ' ').toUpperCase()}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Platform</label>
            <select
              value={filters.platforms?.[0] || ""}
              onChange={(e) => updateFilter({ platforms: e.target.value ? [e.target.value] : undefined })}
              className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
            >
              <option value="">All Platforms</option>
              {capabilities?.platforms?.map((platform: string) => (
                <option key={platform} value={platform}>{platform.toUpperCase()}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Quick Filters</label>
            <select
              onChange={(e) => {
                const value = e.target.value;
                if (value === "needs_review") {
                  updateFilter({ needs_review: true });
                } else if (value === "ready_to_render") {
                  updateFilter({ ready_to_render: true });
                } else {
                  updateFilter({ needs_review: undefined, ready_to_render: undefined });
                }
              }}
              className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
            >
              <option value="">All Items</option>
              <option value="needs_review">Needs Review</option>
              <option value="ready_to_render">Ready to Render</option>
            </select>
          </div>
        </div>

        <div className="flex gap-4 mt-4">
          <button
            onClick={async () => {
              setIsLoading(true);
              try {
                const response = await listWorkflowItems(token, filters);
                setItems(response.items || []);
              } catch (err) {
                console.error("Failed to load workflow items:", err);
                setError("Failed to load workflow items");
              } finally {
                setIsLoading(false);
              }
            }}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-700"
          >
            Apply Filters
          </button>
          <button
            onClick={() => setFilters({})}
            disabled={isLoading}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-700"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedItems.length > 0 && (
        <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-200 font-medium">{selectedItems.length} items selected</p>
            </div>
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => executeBulkAction("approve")}
                disabled={isLoading}
                className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-700 text-sm"
              >
                Approve All
              </button>
              <button
                onClick={() => executeBulkAction("reject")}
                disabled={isLoading}
                className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-gray-700 text-sm"
              >
                Reject All
              </button>
              <button
                onClick={() => executeBulkAction("queue_render")}
                disabled={isLoading}
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-700 text-sm"
              >
                Queue Render
              </button>
              <button
                onClick={() => executeBulkAction("archive")}
                disabled={isLoading}
                className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:bg-gray-700 text-sm"
              >
                Archive All
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Items Grid */}
      <div className="space-y-6">
        {isLoading ? (
          <div className="text-center py-8 text-gray-500">
            Loading workflow items...
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No workflow items found. Create some items to get started.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((item) => (
              <div key={item.item_id} className="bg-gray-900 rounded-lg p-6 border border-gray-800">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <input
                        type="checkbox"
                        checked={selectedItems.includes(item.item_id)}
                        onChange={() => toggleItemSelection(item.item_id)}
                        className="rounded"
                      />
                      <span className="text-xs px-2 py-1 bg-gray-800 rounded text-gray-400">
                        {item.item_type.replace(/_/g, ' ').toUpperCase()}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${getStatusColor(item.status)}`}>
                        {item.status.replace(/_/g, ' ').toUpperCase()}
                      </span>
                    </div>
                    <h3 className="font-semibold text-white mb-1">{item.title}</h3>
                    {item.description && (
                      <p className="text-sm text-gray-400 mb-2">{item.description}</p>
                    )}
                  </div>
                </div>

                {/* Metadata */}
                <div className="space-y-2 mb-4 text-sm">
                  {item.platform && (
                    <div>
                      <span className="text-gray-500">Platform:</span>
                      <span className="ml-2 text-gray-300">{item.platform.toUpperCase()}</span>
                    </div>
                  )}
                  {item.goal && (
                    <div>
                      <span className="text-gray-500">Goal:</span>
                      <span className="ml-2 text-gray-300">{item.goal}</span>
                    </div>
                  )}
                  {item.best_use_case && (
                    <div>
                      <span className="text-gray-500">Best Use:</span>
                      <span className="ml-2 text-gray-300">{item.best_use_case}</span>
                    </div>
                  )}
                  {item.score_confidence && (
                    <div>
                      <span className="text-gray-500">Confidence:</span>
                      <span className="ml-2 text-gray-300">{Math.round(item.score_confidence * 100)}%</span>
                    </div>
                  )}
                  <div>
                    <span className="text-gray-500">Created:</span>
                    <span className="ml-2 text-gray-300">{formatDate(item.created_at)}</span>
                  </div>
                </div>

                {/* Available Actions */}
                <div className="space-y-2">
                  <p className="text-xs text-gray-500 mb-2">Available Actions:</p>
                  <div className="flex flex-wrap gap-2">
                    {item.available_actions.slice(0, 4).map((actionType) => (
                      <button
                        key={actionType}
                        onClick={() => executeAction(item.item_id, actionType)}
                        disabled={isLoading}
                        className={`px-3 py-1 text-xs rounded text-white ${getActionColor(actionType)} disabled:bg-gray-700`}
                      >
                        {getActionLabel(actionType)}
                      </button>
                    ))}
                    {item.available_actions.length > 4 && (
                      <span className="text-xs text-gray-500">+{item.available_actions.length - 4} more</span>
                    )}
                  </div>
                </div>

                {/* External Reference */}
                {item.external_ref && (
                  <div className="mt-4 pt-4 border-t border-gray-800">
                    <div className="text-xs text-gray-500">
                      Ref: {item.external_type} - {item.external_ref}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Metadata Warning */}
      <div className="mt-8 p-4 bg-yellow-900/30 border border-yellow-600 rounded-lg">
        <p className="text-yellow-200 text-sm">
          ⚠️ Metadata workflow only - No actual media processing in v0
        </p>
      </div>
    </div>
  );
}
