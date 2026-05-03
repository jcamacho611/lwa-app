"use client";

import { useState } from "react";
import { LeeWuhCharacter, LeeWuhAvatar } from "../lee-wuh";

interface ProofAsset {
  id: string;
  asset_type: string;
  status: "winning" | "rejected" | "pending";
  hook_text?: string;
  caption_text?: string;
  platform?: string;
  ai_score?: number;
  style_tags: string[];
}

interface StyleProfile {
  niche?: string;
  brand_voice?: string;
  tone_keywords: string[];
  preferred_hook_styles: string[];
  signature_ctas: string[];
}

interface LeeWuhRecommendation {
  recommendation_type: string;
  title: string;
  description: string;
  confidence: number;
  action: string;
}

const mockProofAssets: ProofAsset[] = [
  {
    id: "proof_001",
    asset_type: "clip",
    status: "winning",
    hook_text: "You won't believe what happens at 3:42...",
    caption_text: "The moment that changed everything",
    platform: "tiktok",
    ai_score: 0.94,
    style_tags: ["viral_hook", "suspense", "short_form"],
  },
  {
    id: "proof_002",
    asset_type: "clip",
    status: "rejected",
    hook_text: "Check this out...",
    ai_score: 0.62,
    style_tags: ["weak_hook", "low_energy"],
  },
  {
    id: "proof_003",
    asset_type: "clip",
    status: "winning",
    hook_text: "Stop making this mistake...",
    platform: "youtube_shorts",
    ai_score: 0.91,
    style_tags: ["educational", "problem_solution"],
  },
];

const mockStyleProfile: StyleProfile = {
  niche: "podcast_editing",
  brand_voice: "confident_educational",
  tone_keywords: ["confident", "insightful", "direct", "premium"],
  preferred_hook_styles: ["question", "curiosity", "controversy"],
  signature_ctas: ["Follow for more insights", "Save for later"],
};

const mockRecommendations: LeeWuhRecommendation[] = [
  {
    recommendation_type: "hook_pattern",
    title: "Use Curiosity Gaps",
    description: "Your top 3 winning clips all use curiosity-gap hooks. Try 'You won't believe...' or 'The truth about...'",
    confidence: 0.92,
    action: "Apply to next clip generation",
  },
  {
    recommendation_type: "caption_style",
    title: "Bold Minimal Captions",
    description: "Bold text with minimal words performs 34% better for your audience",
    confidence: 0.88,
    action: "Set as default caption style",
  },
  {
    recommendation_type: "platform_strategy",
    title: "TikTok: 15s Sweet Spot",
    description: "Your TikTok clips under 18s get 2x more views",
    confidence: 0.85,
    action: "Trim TikTok clips to 15s",
  },
];

export function ProofVaultStyleMemoryPanel() {
  const [activeTab, setActiveTab] = useState<"vault" | "style" | "recommendations">("vault");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  const filteredProofs =
    filterStatus === "all"
      ? mockProofAssets
      : mockProofAssets.filter((p) => p.status === filterStatus);

  const winningCount = mockProofAssets.filter((p) => p.status === "winning").length;
  const rejectedCount = mockProofAssets.filter((p) => p.status === "rejected").length;

  return (
    <div className="space-y-6">
      {/* Header with Lee-Wuh */}
      <div className="rounded-2xl border border-[#C9A24A]/30 bg-[#C9A24A]/10 p-6">
        <div className="flex items-center gap-4">
          <LeeWuhCharacter mood="helping" size="lg" showMessage={false} />
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white">Proof Vault + Style Memory</h3>
            <p className="text-sm text-white/70">
              What works. What looks good. What Lee-Wuh recommends next.
            </p>
          </div>
          <div className="flex gap-4 text-right">
            <div className="rounded-lg bg-green-400/20 px-3 py-2">
              <div className="text-xl font-bold text-green-400">{winningCount}</div>
              <div className="text-xs text-white/50">Winning</div>
            </div>
            <div className="rounded-lg bg-red-400/20 px-3 py-2">
              <div className="text-xl font-bold text-red-400">{rejectedCount}</div>
              <div className="text-xs text-white/50">Rejected</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: "vault", label: "Proof Vault", icon: "🏆" },
          { id: "style", label: "Style Profile", icon: "🎨" },
          { id: "recommendations", label: "Lee-Wuh Says", icon: "💡" },
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
          </button>
        ))}
      </div>

      {/* Proof Vault Tab */}
      {activeTab === "vault" && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex flex-wrap gap-2">
            {["all", "winning", "rejected"].map((f) => (
              <button
                key={f}
                onClick={() => setFilterStatus(f)}
                className={`rounded-full px-3 py-1 text-sm capitalize transition ${
                  filterStatus === f
                    ? "bg-[#C9A24A] text-black"
                    : "border border-white/10 bg-white/[0.04] text-white/50 hover:bg-white/[0.08]"
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          {/* Proof Cards */}
          <div className="space-y-3">
            {filteredProofs.map((proof) => (
              <div
                key={proof.id}
                className={`rounded-2xl border p-4 ${
                  proof.status === "winning"
                    ? "border-green-400/30 bg-green-400/10"
                    : proof.status === "rejected"
                    ? "border-red-400/30 bg-red-400/10"
                    : "border-white/10 bg-white/[0.04]"
                }`}
              >
                <div className="mb-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs ${
                        proof.status === "winning"
                          ? "bg-green-400/20 text-green-400"
                          : proof.status === "rejected"
                          ? "bg-red-400/20 text-red-400"
                          : "bg-white/10 text-white/50"
                      }`}
                    >
                      {proof.status}
                    </span>
                    <span className="text-xs text-white/30">{proof.platform}</span>
                  </div>
                  {proof.ai_score && (
                    <span className="text-sm text-[#E9C77B]">{(proof.ai_score * 100).toFixed(0)}% AI</span>
                  )}
                </div>

                {proof.hook_text && (
                  <p className="mb-1 text-sm font-medium text-white">&ldquo;{proof.hook_text}&rdquo;</p>
                )}
                {proof.caption_text && (
                  <p className="mb-3 text-sm text-white/50">{proof.caption_text}</p>
                )}

                <div className="flex flex-wrap gap-1">
                  {proof.style_tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-white/[0.04] px-2 py-0.5 text-xs capitalize text-white/40"
                    >
                      {tag.replace("_", " ")}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {filteredProofs.length === 0 && (
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-8 text-center">
              <p className="text-white/50">No proofs match this filter</p>
            </div>
          )}
        </div>
      )}

      {/* Style Profile Tab */}
      {activeTab === "style" && (
        <div className="space-y-4">
          {/* Brand Voice */}
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <div className="mb-4 flex items-center gap-3">
              <LeeWuhAvatar mood="victory" size="md" />
              <div>
                <h4 className="font-semibold text-white">Brand Voice</h4>
                <p className="text-sm text-white/50">How your content sounds</p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs text-white/50">Niche</label>
                <p className="text-sm text-white">{mockStyleProfile.niche?.replace("_", " ")}</p>
              </div>
              <div>
                <label className="text-xs text-white/50">Brand Voice</label>
                <p className="text-sm text-white">{mockStyleProfile.brand_voice?.replace("_", " ")}</p>
              </div>
            </div>

            <div className="mt-4">
              <label className="text-xs text-white/50">Tone Keywords</label>
              <div className="mt-2 flex flex-wrap gap-2">
                {mockStyleProfile.tone_keywords.map((kw) => (
                  <span
                    key={kw}
                    className="rounded-full bg-[#C9A24A]/20 px-3 py-1 text-sm text-[#E9C77B]"
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Hook Preferences */}
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-3 font-medium text-white">Preferred Hook Styles</h4>
            <div className="flex flex-wrap gap-2">
              {mockStyleProfile.preferred_hook_styles.map((style) => (
                <span
                  key={style}
                  className="rounded-full bg-[#6D3BFF]/20 px-3 py-1 text-sm capitalize text-[#6D3BFF]"
                >
                  {style.replace("_", " ")}
                </span>
              ))}
            </div>
          </div>

          {/* CTAs */}
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-3 font-medium text-white">Signature CTAs</h4>
            <ul className="space-y-2">
              {mockStyleProfile.signature_ctas.map((cta, idx) => (
                <li key={idx} className="flex items-center gap-2 text-sm text-white/70">
                  <span className="text-[#E9C77B]">→</span>
                  {cta}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Lee-Wuh Recommendations Tab */}
      {activeTab === "recommendations" && (
        <div className="space-y-4">
          <div className="rounded-2xl border border-[#C9A24A]/30 bg-[#C9A24A]/10 p-5">
            <div className="mb-4 flex items-center gap-3">
              <LeeWuhCharacter mood="helping" size="md" showMessage={false} />
              <div>
                <h4 className="font-semibold text-white">Lee-Wuh Recommendations</h4>
                <p className="text-sm text-white/50">Based on your proof vault and style memory</p>
              </div>
            </div>
          </div>

          {mockRecommendations.map((rec, idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 transition hover:border-[#C9A24A]/50"
            >
              <div className="mb-2 flex items-center justify-between">
                <span className="rounded-full bg-white/[0.04] px-2 py-1 text-xs capitalize text-white/50">
                  {rec.recommendation_type.replace("_", " ")}
                </span>
                <span className="text-sm text-[#E9C77B]">{(rec.confidence * 100).toFixed(0)}% confidence</span>
              </div>

              <h4 className="mb-2 font-medium text-white">{rec.title}</h4>
              <p className="mb-4 text-sm text-white/70">{rec.description}</p>

              <button className="rounded-lg bg-[#C9A24A]/20 px-3 py-2 text-sm text-[#E9C77B] transition hover:bg-[#C9A24A]/30">
                {rec.action}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-3">
        <button className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
          Save Current Clip to Vault
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Update Style Profile
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Export Memory
        </button>
      </div>
    </div>
  );
}
