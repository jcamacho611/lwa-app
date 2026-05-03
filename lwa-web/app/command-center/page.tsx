import Link from "next/link";
import {
  CompanyOsShell,
  SectionHeader,
  StatusBadge,
} from "../../components/company-os/CompanyOsShell";

const mockClips = [
  {
    title: "The strongest opener",
    status: "ready" as const,
    type: "Rendered",
    detail: "Best clip first. Use this as the lead post when a rendered asset is available.",
    action: "Open generate flow",
  },
  {
    title: "The hook test",
    status: "building" as const,
    type: "Strategy",
    detail: "Hook variants, caption style, CTA, and thumbnail text live here when media is not ready.",
    action: "Copy strategy",
  },
  {
    title: "Campaign export",
    status: "queued" as const,
    type: "Package",
    detail: "Future export bundle for clips, captions, CTAs, platform, and campaign requirements.",
    action: "Queue export",
  },
];

const phases = [
  "Source ingest",
  "Moment finding",
  "Ranking / packaging",
  "Render / export",
  "Delivery",
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
              Feed Lee-Wuh one source. Let LWA find the moments worth posting.
            </h2>
            <p className="mt-3 text-sm leading-6 text-white/55">
              This route is the Company OS command surface. The existing
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

          <div className="rounded-[28px] border border-[#C9A24A]/20 bg-[#C9A24A]/10 p-6">
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

        <section>
          <SectionHeader
            eyebrow="Processing"
            title="Useful status instead of a dead spinner"
          />
          <div className="grid gap-3 md:grid-cols-5">
            {phases.map((phase, index) => (
              <div
                key={phase}
                className="rounded-[20px] border border-white/10 bg-white/[0.04] p-4"
              >
                <p className="text-sm font-semibold text-white">{phase}</p>
                <p className="mt-2 text-xs text-white/45">
                  Step {index + 1}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <SectionHeader
            eyebrow="Review lanes"
            title="Rendered proof first. Strategy second. Packaging always visible."
          />
          <div className="grid gap-5 lg:grid-cols-3">
            {mockClips.map((clip) => (
              <div
                key={clip.title}
                className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="font-mono text-xs uppercase tracking-[0.2em] text-white/45">
                    {clip.type}
                  </p>
                  <StatusBadge status={clip.status} />
                </div>
                <h3 className="mt-4 text-xl font-semibold text-white">
                  {clip.title}
                </h3>
                <p className="mt-3 text-sm leading-6 text-white/60">
                  {clip.detail}
                </p>
                <button className="mt-5 rounded-full border border-white/15 px-4 py-2 text-sm text-white/75">
                  {clip.action}
                </button>
              </div>
            ))}
          </div>
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
