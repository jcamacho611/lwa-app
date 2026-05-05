"use client";

import { useState } from "react";

interface PackagingExportRailProps {
  clipsCount: number;
  onExport: (format: "json" | "markdown" | "txt") => void;
  onAddWatermark?: () => void;
  onAddCTA?: () => void;
}

export default function PackagingExportRail({
  clipsCount,
  onExport,
  onAddWatermark,
  onAddCTA,
}: PackagingExportRailProps) {
  const [selectedFormat, setSelectedFormat] = useState<"json" | "markdown" | "txt">("markdown");
  const [includeHooks, setIncludeHooks] = useState(true);
  const [includeCaptions, setIncludeCaptions] = useState(true);
  const [includeCTAs, setIncludeCTAs] = useState(true);

  const formatDescriptions = {
    json: "Structured data for integrations",
    markdown: "Formatted document with all metadata",
    txt: "Plain text for quick copying",
  };

  return (
    <div className="w-full p-6 bg-[#0a0a0a] border border-[#1a1a1a] rounded-xl">
      <h3 className="text-lg font-semibold text-white mb-4">Export Package</h3>

      {/* Format Selection */}
      <div className="space-y-2 mb-4">
        <label className="block text-sm font-medium text-white/70">Export Format</label>
        <div className="grid grid-cols-3 gap-2">
          {(Object.keys(formatDescriptions) as Array<keyof typeof formatDescriptions>).map((format) => (
            <button
              key={format}
              onClick={() => setSelectedFormat(format)}
              className={`py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                selectedFormat === format
                  ? "bg-[#C9A24A] text-black"
                  : "bg-[#1a1a1a] text-white/70 hover:bg-[#2a2a2a]"
              }`}
            >
              {format.toUpperCase()}
            </button>
          ))}
        </div>
        <p className="text-xs text-white/50">{formatDescriptions[selectedFormat]}</p>
      </div>

      {/* Include Options */}
      <div className="space-y-3 mb-4">
        <label className="block text-sm font-medium text-white/70">Include in Export</label>
        
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={includeHooks}
            onChange={(e) => setIncludeHooks(e.target.checked)}
            className="w-4 h-4 rounded border-[#2a2a2a] bg-[#1a1a1a] text-[#C9A24A] focus:ring-[#C9A24A]"
          />
          <span className="text-sm text-white/80">Hooks</span>
        </label>

        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={includeCaptions}
            onChange={(e) => setIncludeCaptions(e.target.checked)}
            className="w-4 h-4 rounded border-[#2a2a2a] bg-[#1a1a1a] text-[#C9A24A] focus:ring-[#C9A24A]"
          />
          <span className="text-sm text-white/80">Captions</span>
        </label>

        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={includeCTAs}
            onChange={(e) => setIncludeCTAs(e.target.checked)}
            className="w-4 h-4 rounded border-[#2a2a2a] bg-[#1a1a1a] text-[#C9A24A] focus:ring-[#C9A24A]"
          />
          <span className="text-sm text-white/80">Call-to-Actions</span>
        </label>
      </div>

      {/* Enhancement Options */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={onAddWatermark}
          className="flex-1 py-2 px-3 bg-[#1a1a1a] hover:bg-[#2a2a2a] text-white/70 text-sm rounded-lg transition-colors"
        >
          Add Watermark
        </button>
        <button
          onClick={onAddCTA}
          className="flex-1 py-2 px-3 bg-[#1a1a1a] hover:bg-[#2a2a2a] text-white/70 text-sm rounded-lg transition-colors"
        >
          Add CTA Overlay
        </button>
      </div>

      {/* Export Preview */}
      <div className="p-3 bg-[#1a1a1a] rounded-lg mb-4">
        <div className="flex justify-between items-center text-sm">
          <span className="text-white/60">Items to export:</span>
          <span className="text-white font-medium">{clipsCount} clips</span>
        </div>
        <div className="flex justify-between items-center text-sm mt-1">
          <span className="text-white/60">Format:</span>
          <span className="text-[#C9A24A]">{selectedFormat.toUpperCase()}</span>
        </div>
      </div>

      {/* Export Button */}
      <button
        onClick={() => onExport(selectedFormat)}
        className="w-full py-3 px-4 bg-[#C9A24A] hover:bg-[#D4AF37] text-black font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        Export Package
      </button>

      <p className="text-xs text-center text-white/50 mt-3">
        Free exports include metadata only. Video rendering requires credits.
      </p>
    </div>
  );
}
