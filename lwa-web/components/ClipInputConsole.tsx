"use client";

import { useState, useCallback } from "react";

interface ClipInputConsoleProps {
  onSubmit: (_data: { sourceUrl: string; description: string }) => void;
  isLoading?: boolean;
}

export default function ClipInputConsole({ onSubmit, isLoading = false }: ClipInputConsoleProps) {
  const [sourceUrl, setSourceUrl] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  const isValidUrl = (url: string): boolean => {
    if (!url) return false;
    try {
      new URL(url);
      return true;
    } catch {
      return url.includes("youtube.com") || 
             url.includes("youtu.be") || 
             url.includes("tiktok.com") ||
             url.includes("instagram.com");
    }
  };

  const handleSubmit = useCallback(() => {
    if (!sourceUrl.trim()) {
      setError("Please enter a video URL");
      return;
    }
    if (!isValidUrl(sourceUrl)) {
      setError("Please enter a valid video URL (YouTube, TikTok, Instagram)");
      return;
    }
    setError(null);
    onSubmit({ sourceUrl: sourceUrl.trim(), description: description.trim() });
  }, [sourceUrl, description, onSubmit]);

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-[#0a0a0a] border border-[#1a1a1a] rounded-xl">
      <h2 className="text-xl font-semibold text-white mb-4">Create Clip Pack</h2>
      
      <div className="space-y-4">
        {/* URL Input */}
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">
            Video URL
          </label>
          <input
            type="url"
            placeholder="Paste YouTube, TikTok, or Instagram URL..."
            value={sourceUrl}
            onChange={(e) => setSourceUrl(e.target.value)}
            className="w-full px-4 py-3 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:border-[#C9A24A] focus:ring-1 focus:ring-[#C9A24A]"
            disabled={isLoading}
          />
          <p className="mt-1 text-xs text-white/50">
            Supports: YouTube, TikTok, Instagram, or direct video links
          </p>
        </div>

        {/* Description Input */}
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">
            Description (Optional)
          </label>
          <textarea
            placeholder="Describe what you want to extract (e.g., 'best moments', 'funny parts', 'key insights')..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full px-4 py-3 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:border-[#C9A24A] focus:ring-1 focus:ring-[#C9A24A] resize-none"
            disabled={isLoading}
          />
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={isLoading || !sourceUrl.trim()}
          className="w-full py-3 px-6 bg-[#C9A24A] hover:bg-[#D4AF37] disabled:bg-[#2a2a2a] disabled:text-white/40 text-black font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Processing...
            </>
          ) : (
            <>
              Generate Clips
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </>
          )}
        </button>

        {/* Free Tier Note */}
        <p className="text-xs text-center text-white/50">
          Free tier: Offline processing only. AI features require credits.
        </p>
      </div>
    </div>
  );
}
