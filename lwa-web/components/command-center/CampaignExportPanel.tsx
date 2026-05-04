"use client";

import { useState, useEffect } from "react";
import { ClipResult } from "../../lib/types";
import { getCampaigns, getExportPackages, trackLwaEvent } from "../../lib/api";

type Campaign = {
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
};

type ExportPackage = {
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
  quality: string;
};

type RenderedClip = {
  id: string;
  clip: ClipResult;
  hasRenderProof: boolean;
  downloadUrl: string | null;
  isRendered: boolean;
};

interface CampaignExportPanelProps {
  clips?: ClipResult[];
  leadClip?: ClipResult | null;
  sourceId?: string | null;
}

export function CampaignExportPanel({ clips = [], leadClip, sourceId }: CampaignExportPanelProps) {
  const [activeTab, setActiveTab] = useState<"packages" | "clips" | "bundle">("packages");
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [packages, setPackages] = useState<ExportPackage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  // Separate rendered from strategy-only clips
  const renderedClips: RenderedClip[] = clips.map(clip => {
    const hasRenderProof = Boolean(
      clip.download_url || 
      clip.edited_clip_url || 
      clip.clip_url || 
      clip.preview_url
    );
    const downloadUrl = clip.download_url || clip.edited_clip_url || clip.clip_url || null;
    const isRendered = hasRenderProof && !clip.is_strategy_only && !clip.strategy_only;
    
    return {
      id: clip.clip_id || clip.id || `clip_${Math.random().toString(36).slice(2)}`,
      clip,
      hasRenderProof,
      downloadUrl,
      isRendered
    };
  });

  const readyClips = renderedClips.filter(rc => rc.isRendered);
  const strategyOnlyClips = renderedClips.filter(rc => !rc.isRendered);

  useEffect(() => {
    loadCampaignData();
  }, []);

  async function loadCampaignData() {
    setLoading(true);
    try {
      const [campaignsRes, packagesRes] = await Promise.all([
        getCampaigns(50, 0),
        getExportPackages(50, 0)
      ]);
      
      if (campaignsRes.success) {
        setCampaigns(campaignsRes.campaigns);
      }
      if (packagesRes.success) {
        setPackages(packagesRes.packages);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load campaign data");
    } finally {
      setLoading(false);
    }
  }

  function buildCampaignBundle(): string {
    const lines: string[] = [];
    lines.push("# Campaign Export Bundle");
    lines.push(`Generated: ${new Date().toISOString()}`);
    if (sourceId) lines.push(`Source: ${sourceId}`);
    lines.push("");
    
    if (leadClip) {
      lines.push("## Lead Clip");
      lines.push(`Hook: ${leadClip.hook || "N/A"}`);
      lines.push(`Caption: ${leadClip.caption || "N/A"}`);
      lines.push(`CTA: ${leadClip.suggested_cta || leadClip.cta || "N/A"}`);
      lines.push(`Platform: ${leadClip.suggested_platform || leadClip.target_platform || "N/A"}`);
      lines.push(`Score: ${Math.round((leadClip.score || 0) * 100)}%`);
      lines.push("");
    }
    
    if (readyClips.length > 0) {
      lines.push(`## Ready Clips (${readyClips.length})`);
      readyClips.forEach((rc, i) => {
        lines.push(`\n### Clip ${i + 1}: ${rc.clip.title || "Untitled"}`);
        lines.push(`Hook: ${rc.clip.hook || "N/A"}`);
        lines.push(`Caption: ${rc.clip.caption || "N/A"}`);
        if (rc.clip.thumbnail_text) lines.push(`Thumbnail: ${rc.clip.thumbnail_text}`);
        if (rc.clip.suggested_cta || rc.clip.cta) lines.push(`CTA: ${rc.clip.suggested_cta || rc.clip.cta}`);
        if (rc.clip.why_this_matters) lines.push(`Why: ${rc.clip.why_this_matters}`);
        lines.push(`Platform: ${rc.clip.suggested_platform || rc.clip.target_platform || "N/A"}`);
        lines.push(`Score: ${Math.round((rc.clip.score || 0) * 100)}%`);
        if (rc.clip.campaign_role) lines.push(`Role: ${rc.clip.campaign_role}`);
        if (rc.downloadUrl) lines.push(`Download: ${rc.downloadUrl}`);
      });
      lines.push("");
    }
    
    if (strategyOnlyClips.length > 0) {
      lines.push(`## Strategy-Only Clips (${strategyOnlyClips.length}) - Not Yet Rendered`);
      strategyOnlyClips.forEach((rc, i) => {
        lines.push(`\n### Strategy ${i + 1}: ${rc.clip.title || "Untitled"}`);
        lines.push(`Hook: ${rc.clip.hook || "N/A"}`);
        lines.push(`Caption: ${rc.clip.caption || "N/A"}`);
        if (rc.clip.suggested_cta || rc.clip.cta) lines.push(`CTA: ${rc.clip.suggested_cta || rc.clip.cta}`);
        if (rc.clip.why_this_matters) lines.push(`Why: ${rc.clip.why_this_matters}`);
        lines.push(`Timestamps: ${rc.clip.timestamp_start || "N/A"} - ${rc.clip.timestamp_end || "N/A"}`);
        if (rc.clip.reason_not_rendered) lines.push(`Status: ${rc.clip.reason_not_rendered}`);
      });
      lines.push("");
    }
    
    return lines.join("\n");
  }

  async function handleCopyBundle() {
    const bundle = buildCampaignBundle();
    try {
      await navigator.clipboard.writeText(bundle);
      setCopiedText("bundle");
      setTimeout(() => setCopiedText(null), 2000);
      
      void trackLwaEvent({
        event_type: "clip_export",
        source_id: sourceId || null,
        metadata: { 
          action: "copy_bundle", 
          clips_count: clips.length,
          ready_count: readyClips.length,
          strategy_count: strategyOnlyClips.length
        }
      });
    } catch (err) {
      setError("Failed to copy to clipboard");
    }
  }

  const canExport = readyClips.length > 0;

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#FF6B35]/20 text-3xl">
            📤
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white">Campaign Export</h3>
            <p className="text-sm text-white/50">
              {clips.length > 0 
                ? `${readyClips.length} ready, ${strategyOnlyClips.length} strategy-only`
                : "Bundle clips, hooks, captions for delivery"
              }
            </p>
          </div>
          <div className="flex gap-4 text-right">
            <div>
              <div className="text-sm text-white/50">Ready</div>
              <div className="text-xl font-bold text-green-400">{readyClips.length}</div>
            </div>
            <div>
              <div className="text-sm text-white/50">Strategy</div>
              <div className="text-xl font-bold text-yellow-400">{strategyOnlyClips.length}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="rounded-xl border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-300">
          {error}
          <button 
            onClick={() => setError(null)}
            className="ml-2 text-red-300 hover:text-red-200"
          >
            ✕
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: "packages", label: "Packages", icon: "📦", count: packages.length },
          { id: "clips", label: "Current Clips", icon: "🎬", count: clips.length },
          { id: "bundle", label: "Export Bundle", icon: "📋" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all ${
              activeTab === tab.id
                ? "bg-[#C9A24A] text-black"
                : "border border-white/10 bg-white/[0.04] text-white/70 hover:bg-white/[0.08]"
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
            {tab.count !== undefined && tab.count > 0 && (
              <span className="rounded-full bg-black/30 px-2 py-0.5 text-xs">{tab.count}</span>
            )}
          </button>
        ))}
      </div>

      {/* Packages Tab */}
      {activeTab === "packages" && (
        <div className="space-y-4">
          {loading ? (
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-8 text-center">
              <div className="text-white/50">Loading packages...</div>
            </div>
          ) : packages.length === 0 ? (
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-8 text-center">
              <div className="mb-2 text-4xl">📦</div>
              <div className="text-white/70">No export packages yet</div>
              <div className="mt-2 text-sm text-white/50">
                Generate clips and create your first campaign export
              </div>
            </div>
          ) : (
            packages.map((pkg) => (
              <div
                key={pkg.id}
                onClick={() => setSelectedPackage(selectedPackage === pkg.id ? null : pkg.id)}
                className={`cursor-pointer rounded-2xl border p-5 transition ${
                  selectedPackage === pkg.id
                    ? "border-[#C9A24A] bg-[#C9A24A]/5"
                    : "border-white/10 bg-white/[0.04] hover:border-white/20"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="mb-2 flex items-center gap-2">
                      <span
                        className={`rounded-full px-2 py-1 text-xs ${
                          pkg.status === "ready"
                            ? "bg-green-400/20 text-green-400"
                            : pkg.status === "processing"
                            ? "bg-yellow-400/20 text-yellow-400"
                            : "bg-white/10 text-white/50"
                        }`}
                      >
                        {pkg.status}
                      </span>
                      <span className="text-xs text-white/30">{pkg.id.slice(0, 8)}</span>
                    </div>
                    <h4 className="font-medium text-white">{pkg.package_name}</h4>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-white">{pkg.file_count}</div>
                    <div className="text-xs text-white/30">files</div>
                  </div>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {pkg.formats.map((fmt) => (
                    <span
                      key={fmt}
                      className="rounded-full border border-white/10 bg-white/[0.04] px-2 py-1 text-xs uppercase text-white/50"
                    >
                      {fmt}
                    </span>
                  ))}
                </div>

                <div className="mt-4 flex items-center justify-between text-sm">
                  <div className="text-white/50">
                    Created: {new Date(pkg.created_at).toLocaleDateString()}
                  </div>
                  <div className="text-white/50">{(pkg.total_size / 1024 / 1024).toFixed(1)} MB</div>
                </div>

                {selectedPackage === pkg.id && pkg.status === "ready" && pkg.download_url && (
                  <div className="mt-4 flex gap-2 border-t border-white/10 pt-4">
                    <a
                      href={pkg.download_url}
                      download
                      className="flex-1 rounded-lg bg-[#C9A24A] px-4 py-2 text-center text-sm font-medium text-black transition hover:bg-[#E9C77B]"
                    >
                      Download
                    </a>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        void trackLwaEvent({
                          event_type: "clip_share",
                          metadata: { package_id: pkg.id, action: "share_link" }
                        });
                      }}
                      className="flex-1 rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white transition hover:bg-white/[0.08]"
                    >
                      Share Link
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Clips Tab */}
      {activeTab === "clips" && (
        <div className="space-y-6">
          {/* Ready Clips Section */}
          <div>
            <h4 className="mb-3 text-sm font-medium text-green-400">
              ✅ Ready for Export ({readyClips.length})
            </h4>
            {readyClips.length === 0 ? (
              <div className="rounded-xl border border-white/10 bg-white/[0.04] p-4 text-center">
                <p className="text-sm text-white/50">
                  No rendered clips available. Render clips first to export.
                </p>
              </div>
            ) : (
              <div className="grid gap-3">
                {readyClips.map((rc) => (
                  <div
                    key={rc.id}
                    className="rounded-xl border border-green-400/20 bg-green-400/5 p-4"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white">{rc.clip.hook || "Untitled"}</p>
                        <p className="mt-1 text-xs text-white/50 line-clamp-2">{rc.clip.caption}</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {rc.clip.campaign_role && (
                            <span className="rounded-full bg-[#C9A24A]/20 px-2 py-0.5 text-xs text-[#E9C77B]">
                              {rc.clip.campaign_role}
                            </span>
                          )}
                          <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs text-white/50">
                            {Math.round((rc.clip.score || 0) * 100)}%
                          </span>
                          {rc.clip.suggested_platform && (
                            <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs text-white/50 capitalize">
                              {rc.clip.suggested_platform}
                            </span>
                          )}
                        </div>
                      </div>
                      {rc.downloadUrl && (
                        <a
                          href={rc.downloadUrl}
                          download
                          className="rounded-lg bg-[#C9A24A] px-3 py-1.5 text-xs font-medium text-black transition hover:bg-[#E9C77B]"
                        >
                          Download
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Strategy-Only Clips Section */}
          <div>
            <h4 className="mb-3 text-sm font-medium text-yellow-400">
              📝 Strategy Only — Not Rendered ({strategyOnlyClips.length})
            </h4>
            {strategyOnlyClips.length === 0 ? (
              <div className="rounded-xl border border-white/10 bg-white/[0.04] p-4 text-center">
                <p className="text-sm text-white/50">No strategy-only clips.</p>
              </div>
            ) : (
              <div className="grid gap-3">
                {strategyOnlyClips.map((rc) => (
                  <div
                    key={rc.id}
                    className="rounded-xl border border-yellow-400/20 bg-yellow-400/5 p-4 opacity-75"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white/70">{rc.clip.hook || "Untitled"}</p>
                        <p className="mt-1 text-xs text-white/40 line-clamp-2">{rc.clip.caption}</p>
                        <div className="mt-2 flex items-center gap-2">
                          <span className="text-xs text-yellow-400/80">
                            {rc.clip.reason_not_rendered || "Not rendered yet"}
                          </span>
                          {rc.clip.timestamp_start && (
                            <span className="text-xs text-white/30">
                              {rc.clip.timestamp_start}s - {rc.clip.timestamp_end}s
                            </span>
                          )}
                        </div>
                      </div>
                      <span className="rounded-lg border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs text-white/30">
                        Strategy Only
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Bundle Tab */}
      {activeTab === "bundle" && (
        <div className="space-y-4">
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
            <h4 className="mb-4 font-medium text-white">Campaign Bundle</h4>
            
            {/* Export Stats */}
            <div className="mb-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-xl bg-white/[0.02] p-4 text-center">
                <div className="text-2xl font-bold text-green-400">{readyClips.length}</div>
                <div className="text-sm text-white/50">Ready Clips</div>
              </div>
              <div className="rounded-xl bg-white/[0.02] p-4 text-center">
                <div className="text-2xl font-bold text-yellow-400">{strategyOnlyClips.length}</div>
                <div className="text-sm text-white/50">Strategy Only</div>
              </div>
              <div className="rounded-xl bg-white/[0.02] p-4 text-center">
                <div className="text-2xl font-bold text-white">{clips.length}</div>
                <div className="text-sm text-white/50">Total Clips</div>
              </div>
            </div>

            {/* Export Action */}
            <div className="flex flex-col gap-3">
              <button
                onClick={handleCopyBundle}
                disabled={!canExport}
                className={`w-full rounded-xl px-4 py-3 text-sm font-semibold transition ${
                  canExport
                    ? "bg-[#C9A24A] text-black hover:bg-[#E9C77B]"
                    : "cursor-not-allowed border border-white/10 bg-white/[0.04] text-white/30"
                }`}
              >
                {copiedText === "bundle" 
                  ? "✓ Copied!" 
                  : canExport 
                    ? "Copy Bundle to Clipboard" 
                    : "No Rendered Clips to Export"
                }
              </button>
              
              {!canExport && strategyOnlyClips.length > 0 && (
                <p className="text-center text-xs text-yellow-400/80">
                  {strategyOnlyClips.length} clips need rendering before export.
                  Go to Clips tab to view strategy details.
                </p>
              )}
            </div>
          </div>

          {/* Lead Clip Preview */}
          {leadClip && (
            <div className="rounded-2xl border border-[#C9A24A]/30 bg-[#C9A24A]/5 p-5">
              <div className="mb-3 flex items-center gap-2">
                <span className="rounded-full bg-[#C9A24A] px-2 py-1 text-xs font-bold text-black">
                  LEAD
                </span>
                <span className="text-sm text-white/70">Best Clip</span>
              </div>
              <p className="text-sm font-medium text-white">{leadClip.hook}</p>
              <p className="mt-2 text-xs text-white/50">{leadClip.caption}</p>
              <div className="mt-3 flex gap-2">
                <span className="rounded-full bg-white/10 px-2 py-1 text-xs text-white/50">
                  Score: {Math.round((leadClip.score || 0) * 100)}%
                </span>
                {leadClip.campaign_role && (
                  <span className="rounded-full bg-[#C9A24A]/20 px-2 py-1 text-xs text-[#E9C77B]">
                    {leadClip.campaign_role}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Bundle Preview */}
          {clips.length > 0 && (
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
              <h4 className="mb-3 text-sm font-medium text-white/70">Bundle Preview</h4>
              <pre className="max-h-64 overflow-auto rounded-xl bg-black/40 p-4 text-xs text-white/50">
                {buildCampaignBundle().slice(0, 2000)}
                {buildCampaignBundle().length > 2000 && "\n... (truncated)"}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
