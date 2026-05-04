import Link from "next/link";
import { useState } from "react";
import { mockCampaigns, mockEarnings, mockWorldProfile } from "../../lib/worlds/mock-data";
import { formatMoney } from "../../lib/worlds/utils";
import { SafetyNotice } from "./SafetyNotice";
import { StatPill } from "./StatPill";
import { LeeWuhBrainPanel } from "../command-center/LeeWuhBrainPanel";
import DirectorBrainPanel from "../command-center/DirectorBrainPanel";
import { SafetyRightsCostPanel } from "../command-center/SafetyRightsCostPanel";
import { CaptionEnginePanel } from "../command-center/CaptionEnginePanel";
import { AudioMusicVoicePanel } from "../command-center/AudioMusicVoicePanel";
import { CharacterSystemPanel } from "../command-center/CharacterSystemPanel";
import { GameWorldPanel } from "../command-center/GameWorldPanel";
import { MarketplacePanel } from "../command-center/MarketplacePanel";
import { CampaignExportPanel } from "../command-center/CampaignExportPanel";
import { CreativeEnginesPanel } from "../command-center/CreativeEnginesPanel";
import { VideoOSPanel } from "../command-center/VideoOSPanel";
import { SourceTimelinePanel } from "../command-center/SourceTimelinePanel";
import { BatchReviewPanel } from "../command-center/BatchReviewPanel";
import { ProofVaultStyleMemoryPanel } from "../command-center/ProofVaultStyleMemoryPanel";
import { DemoModePanel } from "../command-center/DemoModePanel";
import { LeeWuhCharacterStage } from "../lee-wuh";

export function CommandCenter() {
  const [activeTab, setActiveTab] = useState("overview");

  const tabs = [
    { id: "overview", label: "Overview", icon: "🏠" },
    { id: "demo", label: "Try Demo", icon: "✨" },
    { id: "leewuh", label: "Lee-Wuh Brain", icon: "🧠" },
    { id: "director", label: "Director Brain", icon: "🎯" },
    { id: "character", label: "Character System", icon: "👤" },
    { id: "gameworld", label: "Game World", icon: "🌍" },
    { id: "marketplace", label: "Marketplace", icon: "🛒" },
    { id: "export", label: "Campaign Export", icon: "📤" },
    { id: "creative", label: "Creative Engines", icon: "🎨" },
    { id: "video", label: "Video OS", icon: "🎬" },
    { id: "timeline", label: "Source Timeline", icon: "📁" },
    { id: "batch", label: "Batch Review", icon: "📋" },
    { id: "proofvault", label: "Proof Vault", icon: "🏆" },
    { id: "safety", label: "Safety & Rights", icon: "🛡️" },
    { id: "captions", label: "Captions", icon: "💬" },
    { id: "audio", label: "Audio & Music", icon: "🎵" }
  ];

  const renderActiveTab = () => {
    switch (activeTab) {
      case "demo":
        return <DemoModePanel />;
      case "leewuh":
        return <LeeWuhBrainPanel />;
      case "director":
        return <DirectorBrainPanel />;
      case "character":
        return <CharacterSystemPanel />;
      case "gameworld":
        return <GameWorldPanel />;
      case "marketplace":
        return <MarketplacePanel />;
      case "export":
        return <CampaignExportPanel />;
      case "creative":
        return <CreativeEnginesPanel />;
      case "video":
        return <VideoOSPanel />;
      case "timeline":
        return <SourceTimelinePanel />;
      case "batch":
        return <BatchReviewPanel />;
      case "proofvault":
        return <ProofVaultStyleMemoryPanel />;
      case "safety":
        return <SafetyRightsCostPanel />;
      case "captions":
        return <CaptionEnginePanel />;
      case "audio":
        return <AudioMusicVoicePanel />;
      default:
        return (
          <div className="space-y-6">
            <section className="grid gap-5 lg:grid-cols-[1.25fr_0.75fr]">
              <div className="hero-card rounded-[32px] p-6 sm:p-8">
                <p className="section-kicker">AI Clip Engine</p>
                <h2 className="page-title mt-3 text-3xl font-semibold leading-tight sm:text-[2.4rem]">
                  Drop one source. Build clips, campaigns, XP, and value.
                </h2>
                <p className="mt-3 max-w-2xl text-sm leading-7 text-ink/62">
                  The Command Center links clipping, marketplace jobs, UGC creation, world progression, and the internal
                  economy ledger without replacing the existing generation flow.
                </p>

                <div className="mt-6 grid gap-3 sm:grid-cols-[1fr_auto]">
                  <input
                    placeholder="Paste YouTube, TikTok, Twitch, podcast, or source URL..."
                    className="source-command-input input-surface input-command min-h-[56px] w-full rounded-[24px] px-5 text-base"
                  />
                  <Link
                    href="/generate"
                    className="primary-button inline-flex min-h-[56px] items-center justify-center rounded-full px-6 text-sm font-semibold"
                  >
                    Generate Clip Pack
                  </Link>
                </div>

                <div className="mt-5 flex flex-wrap gap-3">
                  <Link href="/marketplace/post-job" className="secondary-button rounded-full px-4 py-2 text-sm font-semibold">
                    Create campaign
                  </Link>
                  <Link href="/ugc/create" className="secondary-button rounded-full px-4 py-2 text-sm font-semibold">
                    Create UGC asset
                  </Link>
                  <Link href="/worlds/quests" className="ghost-button rounded-full px-4 py-2 text-sm font-semibold">
                    View quests
                  </Link>
                </div>
              </div>

              <div className="glass-panel rounded-[28px] p-6">
                <LeeWuhCharacterStage
                  mood="confident"
                  variant="card"
                  title="Lee-Wuh Command Guide"
                  message="I sit across clipping, campaigns, proof, style memory, and creator missions."
                  posterPath="/brand/lee-wuh/lee-wuh-hero-16x9.png"
                  className="mb-6"
                />

                <p className="section-kicker">World Identity</p>
                <h3 className="mt-3 text-2xl font-semibold text-ink">{mockWorldProfile.displayName}</h3>
                <p className="mt-2 text-sm leading-7 text-ink/62">
                  {mockWorldProfile.className} of {mockWorldProfile.faction}
                </p>

                <div className="mt-5 flex flex-wrap gap-2">
                  <StatPill label="Level" value={mockWorldProfile.level} accent />
                  <StatPill label="XP" value={`${mockWorldProfile.xp}/${mockWorldProfile.nextLevelXp}`} />
                  <StatPill label="Badges" value={mockWorldProfile.badges.length} />
                  <StatPill label="Relics" value={mockWorldProfile.relics.length} />
                </div>

                <Link href="/worlds/profile" className="primary-button mt-6 inline-flex rounded-full px-4 py-2 text-sm font-semibold">
                  Open World Profile
                </Link>
              </div>
            </section>

            <section className="grid gap-5 md:grid-cols-3">
              <div className="metric-tile rounded-[24px] p-5">
                <p className="text-sm text-ink/46">Marketplace campaigns</p>
                <p className="mt-2 text-3xl font-semibold text-ink">{mockCampaigns.length}</p>
                <p className="mt-2 text-sm text-ink/62">Open and review-ready jobs.</p>
              </div>
              <div className="metric-tile rounded-[24px] p-5">
                <p className="text-sm text-ink/46">Approved earnings</p>
                <p className="mt-2 text-3xl font-semibold text-ink">{formatMoney(mockEarnings.approved.amount)}</p>
                <p className="mt-2 text-sm text-ink/62">Not guaranteed until payout clears.</p>
              </div>
              <div className="metric-tile rounded-[24px] p-5">
                <p className="text-sm text-ink/46">Pending review</p>
                <p className="mt-2 text-3xl font-semibold text-ink">{formatMoney(mockEarnings.pendingReview.amount)}</p>
                <p className="mt-2 text-sm text-ink/62">Admin or buyer approval required.</p>
              </div>
            </section>

            <SafetyNotice>
              Earnings are estimates until work is reviewed and approved. Wallet, chain, and collectible features remain
              future-facing placeholders.
            </SafetyNotice>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-[28px] p-3">
        <div className="flex gap-2 overflow-x-auto pb-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-semibold transition ${
                activeTab === tab.id
                  ? "bg-ink text-white shadow-lg"
                  : "bg-white/50 text-ink/70 hover:bg-white/80 hover:text-ink"
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {renderActiveTab()}
    </div>
  );
}
