"use client";

import { useState, useEffect } from "react";
import { createSourceAsset, listSourceAssets, deleteSourceAsset, getSourceAssetTypes, SourceAsset, SourceAssetCreatePayload } from "../lib/api";

interface SourceAssetsPanelProps {
  token: string;
  onAssetsSelected?: (assetIds: string[]) => void;
  selectedAssetIds?: string[];
}

const ASSET_TYPE_DESCRIPTIONS = {
  url: "URL to video, audio, or image content",
  video: "Uploaded video file",
  audio: "Uploaded audio file", 
  song: "Music file for visualizer or soundtrack",
  image: "Static image for animation or background",
  script: "Text script for video generation",
  voice_note: "Voice recording for narration",
  podcast: "Podcast episode for analysis or clipping",
  multi_asset: "Multiple assets packaged together"
};

export function SourceAssetsPanel({ token, onAssetsSelected, selectedAssetIds = [] }: SourceAssetsPanelProps) {
  const [assets, setAssets] = useState<SourceAsset[]>([]);
  const [assetTypes, setAssetTypes] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedType, setSelectedType] = useState("url");
  const [sourceUrl, setSourceUrl] = useState("");
  const [sourceContent, setSourceContent] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  // Load assets and types on mount
  useEffect(() => {
    if (token) {
      loadAssets();
      loadAssetTypes();
    }
  }, [token]);

  const loadAssets = async () => {
    try {
      setIsLoading(true);
      const response = await listSourceAssets(token);
      setAssets(response.assets || []);
    } catch (err) {
      console.error("Failed to load assets:", err);
      setError("Failed to load assets");
    } finally {
      setIsLoading(false);
    }
  };

  const loadAssetTypes = async () => {
    try {
      const response = await getSourceAssetTypes(token);
      setAssetTypes(response.asset_types || []);
    } catch (err) {
      console.error("Failed to load asset types:", err);
    }
  };

  const createAsset = async () => {
    setError("");
    setIsCreating(true);

    try {
      const payload: SourceAssetCreatePayload = {
        asset_type: selectedType,
        source_url: sourceUrl || undefined,
        source_content: sourceContent || undefined,
      };

      const newAsset = await createSourceAsset(token, payload);
      setAssets(prev => [newAsset, ...prev]);
      
      // Reset form
      setSourceUrl("");
      setSourceContent("");
    } catch (err: any) {
      setError(err.message || "Failed to create asset");
    } finally {
      setIsCreating(false);
    }
  };

  const deleteAsset = async (assetId: string) => {
    try {
      await deleteSourceAsset(token, assetId);
      setAssets(prev => prev.filter(asset => asset.asset_id !== assetId));
      
      // Update selection
      if (selectedAssetIds.includes(assetId)) {
        const newSelection = selectedAssetIds.filter(id => id !== assetId);
        onAssetsSelected?.(newSelection);
      }
    } catch (err) {
      console.error("Failed to delete asset:", err);
      setError("Failed to delete asset");
    }
  };

  const toggleAssetSelection = (assetId: string) => {
    const newSelection = selectedAssetIds.includes(assetId)
      ? selectedAssetIds.filter(id => id !== assetId)
      : [...selectedAssetIds, assetId];
    
    onAssetsSelected?.(newSelection);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ready": return "text-green-600";
      case "processing": return "text-blue-600";
      case "failed": return "text-red-600";
      case "uploaded": return "text-yellow-600";
      default: return "text-gray-600";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Source Assets</h2>
        <p className="text-gray-600">Load videos, audio, images, scripts, and more for video creation.</p>
        
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-yellow-800 text-sm">
            <strong>Storage:</strong> Metadata only (placeholder storage). No files are stored in v0.
          </p>
        </div>
      </div>

      {/* Create Asset Form */}
      <div className="mb-8 p-4 border border-gray-200 rounded">
        <h3 className="text-lg font-medium mb-4">Add Source Asset</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">Asset Type</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
            >
              {assetTypes.map((type) => (
                <option key={type} value={type}>
                  {type.replace(/_/g, " ").toUpperCase()}
                </option>
              ))}
            </select>
            {ASSET_TYPE_DESCRIPTIONS[selectedType as keyof typeof ASSET_TYPE_DESCRIPTIONS] && (
              <p className="text-xs text-gray-500 mt-1">
                {ASSET_TYPE_DESCRIPTIONS[selectedType as keyof typeof ASSET_TYPE_DESCRIPTIONS]}
              </p>
            )}
          </div>
        </div>

        <div className="space-y-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">Source URL (optional)</label>
            <input
              type="url"
              placeholder="https://example.com/video.mp4"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Text Content (for scripts, voice notes)</label>
            <textarea
              placeholder="Enter script text or voice note content..."
              value={sourceContent}
              onChange={(e) => setSourceContent(e.target.value)}
              rows={3}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded mb-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <button
          onClick={createAsset}
          disabled={isCreating || (!sourceUrl && !sourceContent)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {isCreating ? "Creating..." : "Add Asset"}
        </button>
      </div>

      {/* Assets List */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium">Your Assets ({assets.length})</h3>
          {selectedAssetIds.length > 0 && (
            <span className="text-sm text-gray-600">
              {selectedAssetIds.length} selected for Video OS
            </span>
          )}
        </div>

        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        ) : assets.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No assets yet. Add your first source asset above.
          </div>
        ) : (
          <div className="space-y-3">
            {assets.map((asset) => (
              <div key={asset.asset_id} className="p-4 border border-gray-200 rounded">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <input
                        type="checkbox"
                        checked={selectedAssetIds.includes(asset.asset_id)}
                        onChange={() => toggleAssetSelection(asset.asset_id)}
                        className="rounded"
                      />
                      <h4 className="font-medium">{asset.asset_type.replace(/_/g, " ").toUpperCase()}</h4>
                      <span className={`px-2 py-1 rounded text-xs ${getStatusColor(asset.status)}`}>
                        {asset.status}
                      </span>
                    </div>
                    
                    <div className="text-sm text-gray-600 space-y-1">
                      {asset.source_url && (
                        <div>
                          <strong>URL:</strong> {asset.source_url}
                        </div>
                      )}
                      {asset.source_content && (
                        <div>
                          <strong>Content:</strong> {asset.source_content.substring(0, 100)}
                          {asset.source_content.length > 100 && "..."}
                        </div>
                      )}
                      {asset.metadata?.filename && (
                        <div>
                          <strong>Filename:</strong> {asset.metadata.filename}
                        </div>
                      )}
                      {asset.metadata?.file_size_bytes && (
                        <div>
                          <strong>Size:</strong> {(asset.metadata.file_size_bytes / 1024 / 1024).toFixed(2)} MB
                        </div>
                      )}
                      {asset.metadata?.duration_seconds && (
                        <div>
                          <strong>Duration:</strong> {asset.metadata.duration_seconds.toFixed(1)}s
                        </div>
                      )}
                      <div>
                        <strong>Created:</strong> {formatDate(asset.created_at)}
                      </div>
                      {asset.error_message && (
                        <div className="text-red-600">
                          <strong>Error:</strong> {asset.error_message}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => deleteAsset(asset.asset_id)}
                      className="px-3 py-1 text-sm border border-red-300 text-red-600 rounded hover:bg-red-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedAssetIds.length > 0 && (
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
          <p className="text-blue-800">
            <strong>Selected for Video OS:</strong> {selectedAssetIds.length} asset(s)
          </p>
          <p className="text-blue-700 text-sm mt-1">
            These assets can be used as source_asset_ids in Video OS job creation.
          </p>
        </div>
      )}
    </div>
  );
}
