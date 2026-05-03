"use client";

import Link from "next/link";
import { LeeWuhCharacter } from "../../components/lee-wuh";

const opportunities = [
  {
    id: "opp_001",
    title: "Podcast Clip Campaign",
    payout: "$500",
    difficulty: "Medium",
    platform: "TikTok",
    description: "Create 10 viral clips from 3 podcast episodes",
    requirements: ["2+ years editing experience", "TikTok native"],
  },
  {
    id: "opp_002",
    title: "YouTube Shorts Series",
    payout: "$800",
    difficulty: "Hard",
    platform: "YouTube",
    description: "Turn long tutorials into engaging Shorts",
    requirements: ["YouTube experience", "Storytelling skills"],
  },
  {
    id: "opp_003",
    title: "Brand Launch Package",
    payout: "$1,200",
    difficulty: "Expert",
    platform: "Multi-platform",
    description: "Full campaign: 20 clips + strategy",
    requirements: ["Portfolio required", "Fast turnaround"],
  },
];

export default function OpportunitiesPage() {
  return (
    <main className="min-h-screen bg-[#0A0A0B] text-[#F5F1E8] p-6">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <LeeWuhCharacter
            mood="victory"
            size="md"
            showMessage={true}
            customMessage="Found 3 paid opportunities that match your skills!"
          />
        </div>

        {/* Stats */}
        <div className="mb-8 grid grid-cols-3 gap-4">
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-center">
            <div className="text-2xl font-bold text-green-400">$2,500</div>
            <div className="text-xs text-white/50">Total Available</div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-center">
            <div className="text-2xl font-bold text-[#C9A24A]">3</div>
            <div className="text-xs text-white/50">Open Jobs</div>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-center">
            <div className="text-2xl font-bold text-[#6D3BFF]">12h</div>
            <div className="text-xs text-white/50">Avg Response</div>
          </div>
        </div>

        {/* Opportunities List */}
        <h2 className="mb-4 text-xl font-bold text-white">Available Work</h2>
        <div className="space-y-4">
          {opportunities.map((opp) => (
            <div
              key={opp.id}
              className="rounded-2xl border border-white/10 bg-white/[0.04] p-6 transition hover:border-[#C9A24A]/50"
            >
              <div className="mb-3 flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-bold text-white">{opp.title}</h3>
                  <p className="mt-1 text-sm text-white/60">{opp.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-green-400">{opp.payout}</div>
                  <div className="text-xs text-white/50">{opp.difficulty}</div>
                </div>
              </div>

              <div className="mb-4 flex flex-wrap gap-2">
                <span className="rounded-full bg-white/[0.04] px-3 py-1 text-sm text-white/60">
                  {opp.platform}
                </span>
                {opp.requirements.map((req, idx) => (
                  <span
                    key={idx}
                    className="rounded-full bg-[#C9A24A]/10 px-3 py-1 text-sm text-[#E9C77B]"
                  >
                    {req}
                  </span>
                ))}
              </div>

              <Link
                href={`/opportunities/${opp.id}/apply`}
                className="block w-full rounded-xl bg-[#C9A24A] py-3 text-center font-bold text-black transition hover:bg-[#E9C77B]"
              >
                Apply Now →
              </Link>
            </div>
          ))}
        </div>

        {/* Upgrade CTA */}
        <div className="mt-8 rounded-2xl border border-[#C9A24A]/30 bg-[#C9A24A]/10 p-6 text-center">
          <p className="text-lg font-medium text-white">
            Get priority access to high-payout jobs
          </p>
          <p className="mt-2 text-sm text-white/60">
            Pro creators see opportunities 24h before everyone else
          </p>
          <Link
            href="https://whop.com/lwa/"
            className="mt-4 inline-block rounded-xl bg-[#C9A24A] px-6 py-3 font-bold text-black hover:bg-[#E9C77B]"
          >
            Upgrade to Pro — $29/mo
          </Link>
        </div>
      </div>
    </main>
  );
}
