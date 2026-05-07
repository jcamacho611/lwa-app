import Link from "next/link";
import { useState } from "react";
import {
  CompanyOsShell,
  SectionHeader,
  StatusBadge,
} from "../../components/company-os/CompanyOsShell";
import { LeeWuhCharacter } from "../../components/lee-wuh";
import { ClipResultsPanel } from "../../components/command-center/ClipResultsPanel";
import LwaEventBridgePanel from "../../components/command-center/LwaEventBridgePanel";

const phases = [
  { name: "Source ingest", status: "complete" },
  { name: "Moment finding", status: "complete" },
  { name: "Ranking / packaging", status: "complete" },
  { name: "Render / export", status: "complete" },
  { name: "Delivery", status: "complete" },
];

export default function CommandCenterPage() {
  return (
    <CompanyOsShell
      activeHref="/command-center"
      eyebrow="LWA Command Center"
      title="The main operational surface for creators and operators."
      description="This v0 keeps the existing generation flow alive while giving LWA a central dashboard for source intake, rendered review, strategy lanes, packaging, campaigns, and revenue actions."
    >
      <div className="space-y-12">
        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
            <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#C9A24A]">
              Source intake
            </p>
            <h2 className="mt-3 text-3xl font-semibold text-white">
              Feed Lee-Wuh one source. Let LWA find moments worth posting.
            </h2>
            <p className="mt-3 text-sm leading-6 text-white/55">
              This route is Company OS command surface. The existing
              generation flow stays preserved and reachable.
            </p>

            <div className="mt-6 rounded-2xl border border-white/10 bg-black/20 p-4">
              <input
                placeholder="Paste public video URL..."
                className="h-12 w-full rounded-xl border border-white/10 bg-black/40 px-4 text-sm text-white outline-none placeholder:text-white/30"
              />
              <div className="mt-4 flex flex-wrap gap-3">
                <Link
                  href="/generate"
                  className="rounded-full bg-[#C9A24A] px-5 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]"
                >
                  Open Generate Flow
                </Link>
                <Link
                  href="/campaigns"
                  className="rounded-full border border-white/15 px-5 py-3 text-sm text-white/75 transition hover:bg-white/5"
                >
                  Campaigns
                </Link>
                <Link
                  href="/revenue"
                  className="rounded-full border border-white/15 px-5 py-3 text-sm text-white/75 transition hover:bg-white/5"
                >
                  Revenue OS
                </Link>
              </div>
            </div>
          </div>

          <div className="rounded-[28px] border-2 border-[#C9A24A]/50 bg-gradient-to-b from-[#C9A24A]/20 to-transparent p-8">
            <p className="font-mono text-xs uppercase tracking-[0.2em] text-[#E9C77B]">
              Recommendation rail
            </p>
            <div className="mt-5 space-y-4">
              <RailItem label="Destination" value="Auto recommended" />
              <RailItem label="Content type" value="Short-form clip pack" />
              <RailItem label="Output style" value="Rendered proof first" />
              <RailItem label="Mascot state" value="Lee-Wuh supports loading/empty/result states" />
            </div>
          </div>
        </section>

        {/* SOURCE INPUT - THE KILLER DEMO STARTS HERE */}
        <section className="rounded-[28px] border-2 border-[#C9A24A]/50 bg-gradient-to-b from-[#C9A24A]/20 to-transparent p-8">
          <div className="mb-6 flex items-center gap-4">
            <LeeWuhCharacter mood="idle" size="md" showMessage={false} />
            <div>
              <h2 className="text-2xl font-bold text-white">Drop one source. Get the best clips first.</h2>
              <p className="text-white/60">Paste a YouTube, TikTok, Twitch, or podcast URL. Lee-Wuh finds moments worth posting.</p>
            </div>
          </div>

          <div className="flex flex-col gap-4 sm:flex-row">
            <input
              type="text"
              placeholder="Paste video URL here... (YouTube, TikTok, Twitch, podcast)"
              className="flex-1 rounded-2xl border border-white/20 bg-black/40 px-6 py-4 text-white outline-none placeholder:text-white/30 focus:border-[#C9A24A]"
            />
            <button className="rounded-2xl bg-[#C9A24A] px-8 py-4 text-base font-bold text-black transition hover:bg-[#E9C77B]">
              🎬 Generate Clip Pack
            </button>
          </div>

          <div className="mt-6 flex flex-wrap items-center gap-6 text-sm text-white/40">
            <span>✓ YouTube</span>
            <span>✓ TikTok</span>
            <span>✓ Twitch</span>
            <span>✓ Podcasts</span>
            <span>✓ MP4 Upload (coming)</span>
          </div>
        </section>

        {/* CLIP RESULTS - BEST CLIP FIRST */}
        <section>
          <ClipResultsPanel />
        </section>

        {/* PROCESSING PHASES */}
        <section>
          <SectionHeader
            eyebrow="Processing"
            title="How LWA creates your clip pack"
          />
          <div className="grid gap-3 md:grid-cols-5">
            {phases.map((phase, index) => (
              <div
                key={phase.name}
                className={`rounded-[20px] border p-4 ${
                  phase.status === "complete"
                    ? "border-green-400/30 bg-green-400/10"
                    : "border-white/10 bg-white/[0.04]"
                }`}
              >
                <div className="flex items-center gap-2">
                  {phase.status === "complete" ? (
                    <span className="text-green-400">✓</span>
                  ) : (
                    <span className="text-white/30">○</span>
                  )}
                  <p className="text-sm font-semibold text-white">{phase.name}</p>
                </div>
                <p className="mt-2 text-xs text-white/45">
                  Step {index + 1}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* NEXT ACTIONS - KILLER DEMO PATH CONTINUATION */}
        <section className="rounded-[28px] border-2 border-[#C9A24A]/50 bg-gradient-to-r from-[#C9A24A]/10 to-transparent p-6">
          <div className="mb-4 flex items-center gap-3">
            <span className="text-2xl">🎯</span>
            <h3 className="text-lg font-semibold text-white">Next Best Action</h3>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <button className="rounded-2xl border border-green-400/30 bg-green-400/10 p-4 text-left transition hover:border-green-400/50">
              <p className="text-xs text-green-400">STEP 1</p>
              <p className="mt-1 font-medium text-white">Play Best Clip</p>
              <p className="mt-1 text-xs text-white/50">Verify it's one</p>
            </button>
            <button className="rounded-2xl border-[#C9A24A]/30 bg-[#C9A24A]/10 p-4 text-left transition hover:border-[#C9A24A]/50">
              <p className="text-xs text-[#E9C77B]">STEP 2</p>
              <p className="mt-1 font-medium text-white">Save to Proof Vault</p>
              <p className="mt-1 text-xs text-white/50">Train Lee-Wuh</p>
            </button>
            <button className="rounded-2xl border-[#6D3BFF]/30 bg-[#6D3BFF]/10 p-4 text-left transition hover:border-[#6D3BFF]/50">
              <p className="text-xs text-[#6D3BFF]">STEP 3</p>
              <p className="mt-1 font-medium text-white">Package &amp; Export</p>
              <p className="mt-1 text-xs text-white/50">Ready to post</p>
            </button>
          </div>
        </section>

        {/* LWA EVENT BRIDGE */}
        <section>
          <LwaEventBridgePanel />
        </section>
      </div>
    </CompanyOsShell>
  );
}

function RailItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-white/40">
        {label}
      </p>
      <p className="mt-2 text-sm font-semibold text-white">{value}</p>
    </div>
  );
}
