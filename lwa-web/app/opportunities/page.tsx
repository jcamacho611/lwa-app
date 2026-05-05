"use client";

import Link from "next/link";
import { LeeWuhCharacter } from "../../components/lee-wuh";

const opportunityLanes = [
  {
    id: "lane_clip_campaign",
    title: "Clip campaign lane",
    status: "metadata shell",
    paymentState: "prepaid or partial-upfront placeholder",
    description: "Turn approved source material into ranked clip packages, captions, hooks, and campaign-ready review bundles.",
    requirements: ["Public or uploaded source", "Manual review", "No automatic payout"],
  },
  {
    id: "lane_caption_pack",
    title: "Caption and hook lane",
    status: "draft workflow",
    paymentState: "subscription or task-credit placeholder",
    description: "Prepare caption variants, hook options, and post text for generated clips without claiming direct platform posting.",
    requirements: ["Score transparency", "Platform fit check", "Operator approval"],
  },
  {
    id: "lane_campaign_review",
    title: "Campaign review lane",
    status: "readiness foundation",
    paymentState: "milestone/dispute placeholder",
    description: "Review creator submissions, mark payout readiness, and keep refund/dispute metadata before real rails are connected.",
    requirements: ["Audit trail", "Rights check", "Manual payout readiness"],
  },
];

export default function OpportunitiesPage() {
  return (
    <main className="min-h-screen bg-[#0A0A0B] p-6 text-[#F5F1E8]">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8">
          <LeeWuhCharacter
            mood="confident"
            size="md"
            showMessage={true}
            customMessage="This board shows marketplace-ready lanes. Live applications and payout automation stay disabled until rails are verified."
          />
        </div>

        <section className="mb-8 rounded-2xl border border-[#C9A24A]/25 bg-[#C9A24A]/10 p-5">
          <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#E9C77B]">
            Opportunity readiness
          </p>
          <h1 className="mt-3 text-3xl font-black uppercase text-white">
            Marketplace lanes, not fake job claims.
          </h1>
          <p className="mt-3 text-sm leading-7 text-white/65">
            These lanes describe the work LWA is preparing to support. They do not represent active paid jobs,
            guaranteed earnings, automatic campaign approval, or live payout automation.
          </p>
        </section>

        <div className="mb-8 grid grid-cols-3 gap-4">
          <Metric label="Live payouts" value="Off" />
          <Metric label="Applications" value="Manual" />
          <Metric label="Rail state" value="V0" />
        </div>

        <h2 className="mb-4 text-xl font-bold text-white">Work lanes</h2>
        <div className="space-y-4">
          {opportunityLanes.map((lane) => (
            <article
              key={lane.id}
              className="rounded-2xl border border-white/10 bg-white/[0.04] p-6 transition hover:border-[#C9A24A]/50"
            >
              <div className="mb-3 flex items-start justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold text-white">{lane.title}</h3>
                  <p className="mt-1 text-sm leading-6 text-white/60">{lane.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-xs uppercase tracking-[0.18em] text-[#E9C77B]">{lane.status}</div>
                  <div className="mt-1 text-xs text-white/45">{lane.paymentState}</div>
                </div>
              </div>

              <div className="mb-4 flex flex-wrap gap-2">
                {lane.requirements.map((req) => (
                  <span
                    key={req}
                    className="rounded-full bg-[#C9A24A]/10 px-3 py-1 text-sm text-[#E9C77B]"
                  >
                    {req}
                  </span>
                ))}
              </div>

              <div className="flex flex-wrap gap-3">
                <Link
                  href="/marketplace"
                  className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-bold text-black transition hover:bg-[#E9C77B]"
                >
                  Open marketplace shell
                </Link>
                <Link
                  href="/marketplace/post-job"
                  className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white/70 transition hover:bg-white/[0.08]"
                >
                  Draft a task
                </Link>
              </div>
            </article>
          ))}
        </div>

        <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.04] p-6">
          <p className="text-lg font-medium text-white">Payment safety gate</p>
          <p className="mt-2 text-sm leading-7 text-white/60">
            Real checkout, escrow, creator payouts, and Whop or Stripe verification must be connected and tested
            before this page can show active paid jobs or application claims.
          </p>
        </div>
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-center">
      <div className="text-lg font-bold text-[#C9A24A]">{value}</div>
      <div className="mt-1 text-xs text-white/50">{label}</div>
    </div>
  );
}
