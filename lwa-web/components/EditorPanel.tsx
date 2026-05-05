"use client";

import { useState } from "react";
import ClipEditorOverlay from "./ClipEditorOverlay";

interface Segment {
  start: number;
  end: number;
  type: "kept" | "removed" | "suggested";
}

interface Clip {
  clip_id: string;
  preview_url?: string;
  segments: Segment[];
  hook: string;
  caption: string;
  cta: string;
  virality_score: number;
  thumbnail_text: string;
  platform_tags: string[];
  render_status: "strategy_only" | "rendered";
}

interface EditorPanelProps {
  clip: Clip;
  onSave?: (clip: Clip) => void;
  onExport?: (clip: Clip) => void;
}

export default function EditorPanel({ clip, onSave, onExport }: EditorPanelProps) {
  const [editedHook, setEditedHook] = useState(clip.hook);
  const [editedCaption, setEditedCaption] = useState(clip.caption);
  const [editedCta, setEditedCta] = useState(clip.cta);
  const [isStrategyOnly] = useState(clip.render_status === "strategy_only");

  const handleSave = () => {
    onSave?.({
      ...clip,
      hook: editedHook,
      caption: editedCaption,
      cta: editedCta,
    });
  };

  return (
    <div className="w-full bg-[#0a0a0a] border border-[#1a1a1a] rounded-xl overflow-hidden">
      {/* Strategy-Only Banner */}
      {isStrategyOnly && (
        <div className="p-3 bg-[#C9A24A]/10 border-b border-[#C9A24A]/20">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-[#C9A24A]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm font-medium text-[#C9A24A]">Strategy Only</span>
          </div>
          <p className="text-xs text-white/60 mt-1">
            This clip has not been rendered yet. Hook, caption, and CTA are ready to use.
          </p>
        </div>
      )}

      {/* Video Preview (or Placeholder) */}
      <div className="relative aspect-video bg-[#1a1a1a]">
        {clip.preview_url ? (
          <video
            src={clip.preview_url}
            controls
            className="w-full h-full"
            poster={`/api/thumbnail?clip_id=${clip.clip_id}`}
          />
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="w-16 h-16 bg-[#2a2a2a] rounded-full flex items-center justify-center mb-3">
              <svg className="w-8 h-8 text-white/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-sm text-white/50">Preview not available (strategy-only)</p>
            <p className="text-xs text-white/40 mt-1">Render with credits to generate video</p>
          </div>
        )}

        {/* Virality Score Badge */}
        <div className="absolute top-3 right-3 px-3 py-1 bg-[#0a0a0a]/80 backdrop-blur rounded-full border border-[#1a1a1a]">
          <span className="text-xs font-medium text-[#C9A24A]">Score: {Math.round(clip.virality_score)}/100</span>
        </div>
      </div>

      {/* Timeline Editor */}
      <div className="p-4 border-b border-[#1a1a1a]">
        <ClipEditorOverlay
          segments={clip.segments}
          duration={30} // Mock duration
        />
      </div>

      {/* Editable Fields */}
      <div className="p-4 space-y-4">
        {/* Hook */}
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">
            Hook (First 3 seconds)
          </label>
          <input
            type="text"
            value={editedHook}
            onChange={(e) => setEditedHook(e.target.value)}
            className="w-full px-3 py-2 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg text-white text-sm focus:outline-none focus:border-[#C9A24A]"
            placeholder="Enter hook text..."
          />
          <p className="text-xs text-white/50 mt-1">Grabs attention in the first 3 seconds</p>
        </div>

        {/* Caption */}
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">
            Caption/Description
          </label>
          <textarea
            value={editedCaption}
            onChange={(e) => setEditedCaption(e.target.value)}
            rows={2}
            className="w-full px-3 py-2 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg text-white text-sm resize-none focus:outline-none focus:border-[#C9A24A]"
            placeholder="Enter caption..."
          />
        </div>

        {/* CTA */}
        <div>
          <label className="block text-sm font-medium text-white/70 mb-2">
            Call to Action
          </label>
          <input
            type="text"
            value={editedCta}
            onChange={(e) => setEditedCta(e.target.value)}
            className="w-full px-3 py-2 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg text-white text-sm focus:outline-none focus:border-[#C9A24A]"
            placeholder="Enter CTA..."
          />
        </div>

        {/* Platform Tags */}
        <div className="flex flex-wrap gap-2">
          {clip.platform_tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 text-xs bg-[#1a1a1a] text-white/70 rounded border border-[#2a2a2a]"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-2">
          <button
            onClick={handleSave}
            className="flex-1 py-2 px-4 bg-[#1a1a1a] hover:bg-[#2a2a2a] text-white font-medium rounded-lg transition-colors text-sm"
          >
            Save Changes
          </button>
          <button
            onClick={() => onExport?.(clip)}
            className="flex-1 py-2 px-4 bg-[#C9A24A] hover:bg-[#D4AF37] text-black font-medium rounded-lg transition-colors text-sm"
          >
            Export Package
          </button>
        </div>
      </div>
    </div>
  );
}
