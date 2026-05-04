"use client";

import { useState, useEffect } from "react";
import {
  getDemoStatus,
  getDemoSource,
  getDemoClips,
  getDemoCampaign,
  saveDemoProof,
  DemoClip,
} from "../../lib/api";

type Tab = "overview" | "clips" | "campaign" | "proof";

export function DemoModePanel() {
  const [activeTab, setActiveTab] = useState<Tab>("overview");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [demoEnabled, setDemoEnabled] = useState(false);
  const [clips, setClips] = useState<DemoClip[]>([]);
  const [campaign, setCampaign] = useState<any>(null);
  const [savedProof, setSavedProof] = useState<any>(null);
  const [expandedClip, setExpandedClip] = useState<string | null>(null);

  useEffect(() => {
    checkDemoStatus();
  }, []);

  async function checkDemoStatus() {
    try {
      const status = await getDemoStatus();
      setDemoEnabled(status.demo_mode_enabled);
    } catch (err) {
      setError("Failed to check demo status");
    }
  }

  async function loadDemoClips() {
    setLoading(true);
    setError(null);
    try {
      const result = await getDemoClips();
      setClips(result.clips);
      setActiveTab("clips");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load demo clips");
    } finally {
      setLoading(false);
    }
  }

  async function loadDemoCampaign() {
    setLoading(true);
    setError(null);
    try {
      const result = await getDemoCampaign();
      setCampaign(result.campaign);
      setActiveTab("campaign");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load campaign");
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveProof() {
    setLoading(true);
    setError(null);
    try {
      const result = await saveDemoProof();
      setSavedProof(result);
      setActiveTab("proof");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save proof");
    } finally {
      setLoading(false);
    }
  }

  if (!demoEnabled) {
    return (
      <div className="rounded-[28px] border border-[var(--divider)] bg-[var(--surface-soft)] p-6">
        <h3 className="text-lg font-semibold text-ink">Demo Mode</h3>
        <p className="mt-2 text-sm text-ink/62">Demo mode is currently unavailable.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {[
          { id: "overview", label: "Overview", icon: "🎯" },
          { id: "clips", label: "Sample Clips", icon: "🎬" },
          { id: "campaign", label: "Campaign", icon: "📦" },
          { id: "proof", label: "Proof Vault", icon: "🏆" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as Tab)}
            className={[
              "inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition",
              activeTab === tab.id
                ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]"
                : "border border-[var(--divider)] bg-[var(--surface-veil)] text-ink/76 hover:bg-[var(--surface-soft)]",
            ].join(" ")}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {error && (
        <div className="rounded-[18px] border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {activeTab === "overview" && (
        <div className="rounded-[28px] border border-[var(--divider)] bg-[var(--surface-soft)] p-6">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1">
            <span className="text-sm font-medium text-[var(--gold)]">✨ Try LWA Without Uploading</span>
          </div>
          <h3 className="text-xl font-semibold text-ink">Demo Mode</h3>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-ink/62">
            Experience the full LWA workflow with sample content. See how clips are generated, 
            scored, and organized into campaigns — no video upload required.
          </p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <button
              onClick={loadDemoClips}
              disabled={loading}
              className="flex flex-col items-center gap-3 rounded-[24px] border border-[var(--divider)] bg-[var(--surface-veil)] p-5 text-center transition hover:border-[var(--gold-border)] hover:bg-[var(--gold-dim)]"
            >
              <span className="text-3xl">🎬</span>
              <span className="text-sm font-medium text-ink">View Sample Clips</span>
              <span className="text-xs text-ink/58">4 AI-scored clips</span>
            </button>

            <button
              onClick={loadDemoCampaign}
              disabled={loading}
              className="flex flex-col items-center gap-3 rounded-[24px] border border-[var(--divider)] bg-[var(--surface-veil)] p-5 text-center transition hover:border-[var(--gold-border)] hover:bg-[var(--gold-dim)]"
            >
              <span className="text-3xl">📦</span>
              <span className="text-sm font-medium text-ink">Export Campaign</span>
              <span className="text-xs text-ink/58">Posting schedule + bundle</span>
            </button>

            <button
              onClick={handleSaveProof}
              disabled={loading}
              className="flex flex-col items-center gap-3 rounded-[24px] border border-[var(--divider)] bg-[var(--surface-veil)] p-5 text-center transition hover:border-[var(--gold-border)] hover:bg-[var(--gold-dim)]"
            >
              <span className="text-3xl">🏆</span>
              <span className="text-sm font-medium text-ink">Save to Proof Vault</span>
              <span className="text-xs text-ink/58">Store winning hooks</span>
            </button>

            <div className="flex flex-col items-center gap-3 rounded-[24px] border border-dashed border-[var(--divider)] bg-[var(--surface-veil-strong)] p-5 text-center">
              <span className="text-3xl opacity-50">🚀</span>
              <span className="text-sm font-medium text-ink/58">Next: Upload Your Source</span>
              <span className="text-xs text-ink/42">Try with your own video</span>
            </div>
          </div>

          <div className="mt-6 rounded-[18px] border border-[var(--divider)] bg-[var(--surface-veil)] p-4">
            <h4 className="text-sm font-semibold text-ink">Sample Source</h4>
            <p className="mt-1 text-sm text-ink/62">Creator Interview — Building in Public (5 min)</p>
            <p className="mt-2 text-xs text-ink/42">
              Text-only preview for demonstration. No actual video required.
            </p>
          </div>
        </div>
      )}

      {activeTab === "clips" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-ink">Sample Clips</h3>
            <button
              onClick={() => setActiveTab("overview")}
              className="text-sm text-ink/62 hover:text-ink"
            >
              ← Back
            </button>
          </div>

          {clips.length === 0 ? (
            <p className="text-sm text-ink/62">No clips loaded. Click &quot;View Sample Clips&quot; to load.</p>
          ) : (
            <div className="grid gap-4">
              {clips.map((clip, index) => (
                <div
                  key={clip.clip_id}
                  className="rounded-[24px] border border-[var(--divider)] bg-[var(--surface-soft)] p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--gold-dim)] text-sm font-bold text-[var(--gold)]">
                        {index + 1}
                      </span>
                      <div>
                        <p className="text-sm font-medium text-ink">{clip.title}</p>
                        <p className="text-xs text-ink/58">
                          {clip.campaign_role} • {Math.round(clip.score * 100)}% score
                        </p>
                      </div>
                    </div>
                    <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1 text-xs font-medium text-[var(--gold)]">
                      {clip.funnel_stage}
                    </span>
                  </div>

                  <div className="mt-4 space-y-3">
                    <div className="rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] p-3">
                      <p className="text-xs uppercase tracking-[0.2em] text-muted">Hook</p>
                      <p className="mt-1 text-sm leading-6 text-ink/78">{clip.hook}</p>
                    </div>

                    {expandedClip === clip.clip_id && (
                      <>
                        <div className="rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] p-3">
                          <p className="text-xs uppercase tracking-[0.2em] text-muted">Caption</p>
                          <p className="mt-1 text-sm leading-6 text-ink/78">{clip.caption}</p>
                        </div>
                        <div className="rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] p-3">
                          <p className="text-xs uppercase tracking-[0.2em] text-muted">CTA</p>
                          <p className="mt-1 text-sm leading-6 text-ink/78">{clip.suggested_cta}</p>
                        </div>
                        <div className="rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] p-3">
                          <p className="text-xs uppercase tracking-[0.2em] text-muted">Why This Matters</p>
                          <p className="mt-1 text-sm leading-6 text-ink/78">{clip.why_this_matters}</p>
                        </div>
                        <div className="flex gap-2 text-xs text-ink/58">
                          <span>Start: {clip.timestamp_start}s</span>
                          <span>End: {clip.timestamp_end}s</span>
                          <span>Duration: {(clip.timestamp_end - clip.timestamp_start).toFixed(1)}s</span>
                        </div>
                      </>
                    )}
                  </div>

                  <button
                    onClick={() => setExpandedClip(expandedClip === clip.clip_id ? null : clip.clip_id)}
                    className="mt-3 text-xs font-medium text-[var(--gold)] hover:underline"
                  >
                    {expandedClip === clip.clip_id ? "Show less" : "Show more"}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "campaign" && campaign && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-ink">Campaign Pack</h3>
            <button
              onClick={() => setActiveTab("overview")}
              className="text-sm text-ink/62 hover:text-ink"
            >
              ← Back
            </button>
          </div>

          <div className="rounded-[24px] border border-[var(--divider)] bg-[var(--surface-soft)] p-5">
            <h4 className="text-sm font-semibold text-ink">{campaign.name}</h4>
            <p className="text-xs text-ink/58">{campaign.clips.length} clips • Created {new Date(campaign.created_at).toLocaleDateString()}</p>
          </div>

          <div className="rounded-[24px] border border-[var(--divider)] bg-[var(--surface-soft)] p-5">
            <h4 className="mb-4 text-sm font-semibold text-ink">Posting Schedule</h4>
            <div className="space-y-2">
              {campaign.posting_schedule.map((item: any) => (
                <div
                  key={`${item.day}-${item.clip_id}`}
                  className="flex items-center gap-4 rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] p-3"
                >
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--gold-dim)] text-xs font-bold text-[var(--gold)]">
                    D{item.day}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm text-ink capitalize">{item.platform.replace("_", " ")}</p>
                    <p className="text-xs text-ink/58">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[24px] border border-[var(--divider)] bg-[var(--surface-soft)] p-5">
            <h4 className="mb-4 text-sm font-semibold text-ink">Bundle Contents</h4>
            <div className="grid gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-ink/62">Hooks</span>
                <span className="font-medium text-ink">{campaign.bundle_contents.hooks.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-ink/62">Captions</span>
                <span className="font-medium text-ink">{campaign.bundle_contents.captions.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-ink/62">CTAs</span>
                <span className="font-medium text-ink">{campaign.bundle_contents.ctas.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-ink/62">Timestamps</span>
                <span className="font-medium text-ink">{campaign.bundle_contents.timestamps.length}</span>
              </div>
            </div>
          </div>

          <div className="rounded-[18px] border border-dashed border-[var(--divider)] bg-[var(--surface-veil-strong)] p-4 text-center">
            <p className="text-xs text-ink/42">
              Demo export shows structure. Real exports include rendered MP4s.
            </p>
          </div>
        </div>
      )}

      {activeTab === "proof" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-ink">Proof Vault</h3>
            <button
              onClick={() => setActiveTab("overview")}
              className="text-sm text-ink/62 hover:text-ink"
            >
              ← Back
            </button>
          </div>

          {savedProof ? (
            <div className="rounded-[24px] border border-[var(--gold-border)] bg-[var(--gold-dim)] p-5">
              <div className="flex items-center gap-2">
                <span className="text-xl">✅</span>
                <div>
                  <p className="text-sm font-medium text-[var(--gold)]">Demo clips saved!</p>
                  <p className="text-xs text-[var(--gold)]/80">
                    {savedProof.count} assets stored in Proof Vault
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded-[24px] border border-[var(--divider)] bg-[var(--surface-soft)] p-5 text-center">
              <p className="text-sm text-ink/62">
                No demo assets saved yet. Click &quot;Save to Proof Vault&quot; to store sample clips.
              </p>
            </div>
          )}

          <div className="rounded-[18px] border border-[var(--divider)] bg-[var(--surface-veil)] p-4">
            <h4 className="text-sm font-semibold text-ink">About Proof Vault</h4>
            <p className="mt-2 text-xs leading-6 text-ink/62">
              The Proof Vault stores your winning hooks, captions, and clip metadata. 
              Use it to build a library of proven content patterns and train your Style Memory.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
