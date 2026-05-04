"use client";

import { useState } from "react";
import { Check, Copy, Star, TrendingUp, Shield, Zap } from "lucide-react";

export interface HeroClipProps {
  clip: {
    clip_id: string;
    hook: string;
    caption: string;
    text: string;
    cta: string;
    thumbnail_text: string;
    score: number;
    why: string;
    rank: number;
  };
  onCopyHook: () => void;
  onCopyCaption: () => void;
}

function getConfidenceLabel(score: number): {
  label: string;
  color: string;
  icon: React.ReactNode;
  description: string;
} {
  if (score >= 0.8) {
    return {
      label: "High Potential",
      color: "text-emerald-400",
      icon: <Zap className="h-4 w-4" />,
      description: "Strong hook + emotional trigger",
    };
  } else if (score >= 0.6) {
    return {
      label: "Safe Post",
      color: "text-blue-400",
      icon: <Shield className="h-4 w-4" />,
      description: "Proven engagement pattern",
    };
  } else {
    return {
      label: "Experimental",
      color: "text-amber-400",
      icon: <TrendingUp className="h-4 w-4" />,
      description: "Test this angle",
    };
  }
}

export function HeroClip({ clip, onCopyHook, onCopyCaption }: HeroClipProps) {
  const [copiedHook, setCopiedHook] = useState(false);
  const [copiedCaption, setCopiedCaption] = useState(false);
  
  const confidence = getConfidenceLabel(clip.score);
  
  const handleCopyHook = () => {
    navigator.clipboard.writeText(clip.hook);
    setCopiedHook(true);
    onCopyHook();
    setTimeout(() => setCopiedHook(false), 2000);
  };
  
  const handleCopyCaption = () => {
    navigator.clipboard.writeText(clip.caption);
    setCopiedCaption(true);
    onCopyCaption();
    setTimeout(() => setCopiedCaption(false), 2000);
  };
  
  return (
    <div className="relative overflow-hidden rounded-2xl border-2 border-[#C9A24A] bg-gradient-to-br from-[#C9A24A]/20 via-[#E9C77B]/10 to-transparent p-6">
      {/* Crown indicator */}
      <div className="absolute -right-1 -top-1 flex items-center gap-1 rounded-bl-xl rounded-tr-xl bg-[#C9A24A] px-3 py-1 text-sm font-bold text-black">
        <Star className="h-4 w-4 fill-black" />
        POST THIS FIRST
      </div>
      
      {/* Score badge */}
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-[#C9A24A] to-[#E9C77B] text-2xl font-bold text-black">
          {Math.round(clip.score * 100)}
        </div>
        <div>
          <div className={`flex items-center gap-1 font-semibold ${confidence.color}`}>
            {confidence.icon}
            {confidence.label}
          </div>
          <p className="text-sm text-white/60">{confidence.description}</p>
        </div>
      </div>
      
      {/* Why this works */}
      <div className="mb-4 rounded-lg bg-white/5 p-3">
        <p className="text-sm text-white/80">
          <span className="text-[#C9A24A]">Why this works:</span> {clip.why}
        </p>
      </div>
      
      {/* Hook */}
      <div className="mb-4">
        <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-white/50">
          Hook (Copy this)
        </label>
        <div className="flex items-start gap-2">
          <div className="flex-1 rounded-lg bg-white/10 p-3 text-lg font-semibold text-white">
            {clip.hook}
          </div>
          <button
            onClick={handleCopyHook}
            className="flex items-center gap-1 rounded-lg bg-[#C9A24A] px-3 py-3 text-sm font-medium text-black transition hover:bg-[#E9C77B]"
          >
            {copiedHook ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            {copiedHook ? "Copied" : "Copy"}
          </button>
        </div>
      </div>
      
      {/* Caption */}
      <div className="mb-4">
        <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-white/50">
          Caption (Copy this)
        </label>
        <div className="flex items-start gap-2">
          <div className="flex-1 rounded-lg bg-white/10 p-3 text-white/90">
            {clip.caption}
          </div>
          <button
            onClick={handleCopyCaption}
            className="flex items-center gap-1 rounded-lg bg-white/20 px-3 py-3 text-sm font-medium text-white transition hover:bg-white/30"
          >
            {copiedCaption ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
          </button>
        </div>
      </div>
      
      {/* CTA */}
      <div className="flex items-center gap-2 rounded-lg bg-[#C9A24A]/10 px-4 py-2">
        <span className="text-sm text-white/60">CTA:</span>
        <span className="font-medium text-[#C9A24A]">{clip.cta}</span>
      </div>
    </div>
  );
}
