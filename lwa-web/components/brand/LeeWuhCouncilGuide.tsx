"use client";

import React, { useState, useEffect } from "react";
import Card from "../ui/Card";

interface CouncilInput {
  app_state: string;
  current_screen: string;
  source_asset_ids: string[];
  timeline_id?: string;
  render_job_id?: string;
  clip_id?: string;
  user_goal?: string;
  platform?: string;
  warnings: string[];
  engine_statuses: Record<string, string>;
  user_id?: string;
  has_credits: boolean;
  has_sources: boolean;
  has_clips: boolean;
  has_timeline: boolean;
}

interface CouncilOutput {
  mascot_message: string;
  council_summary: string;
  next_best_action: string;
  recommended_engine?: string;
  warnings: string[];
  confidence: number;
  visual_state: string;
  metadata: Record<string, any>;
}

export default function LeeWuhCouncilGuide({
  currentScreen = "homepage",
  hasSources = false,
  hasClips = false,
  hasTimeline = false,
  hasCredits = true,
  warnings = [],
  engineStatuses = {},
}: {
  currentScreen?: string;
  hasSources?: boolean;
  hasClips?: boolean;
  hasTimeline?: boolean;
  hasCredits?: boolean;
  warnings?: string[];
  engineStatuses?: Record<string, string>;
}) {
  const [guidance, setGuidance] = useState<CouncilOutput | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGuidance();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentScreen, hasSources, hasClips, hasTimeline, hasCredits]);

  const fetchGuidance = async () => {
    setLoading(true);
    setError(null);

    try {
      const input: CouncilInput = {
        app_state: "idle",
        current_screen: currentScreen,
        source_asset_ids: [],
        warnings,
        engine_statuses: engineStatuses,
        has_credits: hasCredits,
        has_sources: hasSources,
        has_clips: hasClips,
        has_timeline: hasTimeline,
      };

      const response = await fetch("/v1/lee-wuh/guidance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch council guidance");
      }

      const data: CouncilOutput = await response.json();
      setGuidance(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="bg-gradient-to-br from-purple-900/20 to-black border-purple-500/30 p-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-purple-500/20 animate-pulse flex items-center justify-center">
            <span className="text-2xl">🤖</span>
          </div>
          <div>
            <p className="text-white font-medium">Lee-Wuh is thinking...</p>
            <p className="text-purple-300 text-sm">Consulting the council</p>
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="bg-gradient-to-br from-red-900/20 to-black border-red-500/30 p-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
            <span className="text-2xl">⚠️</span>
          </div>
          <div>
            <p className="text-white font-medium">Council temporarily unavailable</p>
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        </div>
      </Card>
    );
  }

  if (!guidance) {
    return null;
  }

  const visualStateIcon = {
    idle: "🤖",
    thinking: "🧠",
    success: "✨",
    warning: "⚠️",
    error: "❌",
    rendering: "🔥",
    analyzing: "🔍",
    excited: "🎯",
    overlord: "👑",
  }[guidance.visual_state] || "🤖";

  return (
    <Card className="bg-gradient-to-br from-purple-900/20 to-black border-purple-500/30 p-4">
      <div className="space-y-4">
        {/* Lee-Wuh Message */}
        <div className="flex items-start gap-3">
          <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
            <span className="text-2xl">{visualStateIcon}</span>
          </div>
          <div className="flex-1">
            <p className="text-white font-medium text-lg">{guidance.mascot_message}</p>
            {guidance.confidence < 70 && (
              <p className="text-purple-300 text-sm mt-1">
                Confidence: {guidance.confidence}%
              </p>
            )}
          </div>
        </div>

        {/* Council Summary */}
        {guidance.council_summary && (
          <div className="bg-black/30 rounded-lg p-3 border border-purple-500/20">
            <p className="text-purple-200 text-sm">
              <span className="text-purple-400 font-medium">Council:</span>{" "}
              {guidance.council_summary}
            </p>
          </div>
        )}

        {/* Next Best Action */}
        {guidance.next_best_action && (
          <div className="bg-gradient-to-r from-purple-500/10 to-transparent rounded-lg p-3 border-l-4 border-purple-500">
            <p className="text-white text-sm font-medium">
              Next Action: {guidance.next_best_action}
            </p>
          </div>
        )}

        {/* Warnings */}
        {guidance.warnings.length > 0 && (
          <div className="space-y-2">
            {guidance.warnings.map((warning, index) => (
              <div
                key={index}
                className="bg-yellow-500/10 rounded-lg p-2 border border-yellow-500/30"
              >
                <p className="text-yellow-200 text-sm">⚠️ {warning}</p>
              </div>
            ))}
          </div>
        )}

        {/* Recommended Engine */}
        {guidance.recommended_engine && (
          <div className="flex items-center gap-2 text-purple-300 text-sm">
            <span>🔧</span>
            <span>Recommended: {guidance.recommended_engine}</span>
          </div>
        )}
      </div>
    </Card>
  );
}
