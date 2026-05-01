import type { Metadata } from "next";
import Link from "next/link";
import { getAllCouncilRoles, COUNCIL_BRAND_LINE } from "../../lib/production-council";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Operator Command Center",
  description: "Internal LWA command center for generation health, clip quality, revenue intent, and launch readiness.",
  path: "/operator",
  keywords: [
    "LWA operator dashboard",
    "AI clipping command center",
    "creator operations",
    "generation health",
  ],
});

type MetricCard = {
  label: string;
  value: string;
  detail: string;
  status: "ready" | "watch" | "planned";
};

const metrics: MetricCard[] = [
  {
    label: "Generation flow",
    value: "Live",
    detail: "Source-to-clip pipeline active on Railway. URL ingest, upload, and idea modes wired.",
    status: "ready",
  },
  {
    label: "Director Brain",
    value: "Wired",
    detail: "Enrichment + scoring active. Rendered vs strategy-only separation enforced per clip.",
    status: "ready",
  },
  {
    label: "Auto Editor Brain",
    value: "Active",
    detail: "Attaches scores, caption style, font, edit style, filter, b-roll, and export profile to every clip. AI upgrade path runs if Anthropic/OpenAI keys are present; heuristic fallback always fires.",
    status: "ready",
  },
  {
    label: "Whop verification",
    value: "Merged",
    detail: "Signed webhook MVP is merged. Confirm live delivery before claiming paid enforcement.",
    status: "watch",
  },
  {
    label: "Stripe Connect",
    value: "Wired",
    detail: "stripe_connect.py exists in lwa-backend/app/worlds/. Env vars documented. Not live until STRIPE_SECRET_KEY is set.",
    status: "planned",
  },
  {
    label: "Marketplace layer",
    value: "Preview",
    detail: "Seller shell, opportunities page, and inquiry flow exist. Money movement gated behind review.",
    status: "planned",
  },
];

const lanes = [
  {
    title: "Clip quality",
    items: ["Rendered clips", "Raw-only clips", "Strategy-only outputs", "Quality gate warnings"],
  },
  {
    title: "Sales signals",
    items: ["Revenue intent", "Offer fit", "CTA copies", "Demo and upgrade clicks"],
  },
  {
    title: "Reliability",
    items: ["Provider failures", "Fallback reasons", "Blocked URLs", "Upload readiness"],
  },
  {
    title: "Launch readiness",
    items: ["Backend health", "Frontend deploy", "Generate smoke test", "Whop event smoke test"],
  },
];

const councilRoles = getAllCouncilRoles();

const councilRoutes = [
  { label: "Generator", href: "/generate", detail: "Run the main source-to-package flow." },
  { label: "Signal Realms", href: "/realm", detail: "Preview classes, factions, quests, and cosmetic identity." },
  { label: "Marketplace", href: "/marketplace", detail: "Preview template, hook, caption, brand kit, and campaign assets." },
  { label: "Social", href: "/social", detail: "Track future provider readiness without fake posting claims." },
  { label: "Proof", href: "/proof", detail: "Review provenance rules without wallet or unlock claims." },
  { label: "Home", href: "/", detail: "Return to the public landing page." },
];

function statusClass(status: MetricCard["status"]) {
  if (status === "ready") {
    return "border-emerald-300/25 bg-emerald-300/10 text-emerald-100";
  }
  if (status === "watch") {
    return "border-amber-300/25 bg-amber-300/10 text-amber-100";
  }
  return "border-white/12 bg-white/[0.05] text-ink/68";
}

export default function OperatorPage() {
  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <section className="mx-auto max-w-7xl">
        <div className="rounded-[36px] border border-white/12 bg-[radial-gradient(circle_at_top_left,rgba(109,92,255,0.18),transparent_30%),linear-gradient(180deg,var(--bg-card),var(--bg))] p-6 shadow-card sm:p-8">
          <p className="section-kicker">LWA internal operations</p>
          <div className="mt-5 grid gap-6 lg:grid-cols-[minmax(0,1fr),320px] lg:items-end">
            <div>
              <h1 className="text-4xl font-semibold leading-tight text-ink sm:text-6xl">
                Operator Command Center
              </h1>
              <p className="mt-4 max-w-3xl text-base leading-8 text-ink/66">
                A launch-safe control room for watching the parts that make LWA valuable: generation reliability,
                Director Brain packaging, clip quality, revenue intent, and smoke-test readiness. This shell does not
                claim marketplace payouts, direct posting, or blockchain systems are live.
              </p>
            </div>
            <div className="grid gap-3 rounded-[28px] border border-white/12 bg-white/[0.04] p-4">
              <Link href="/generate" className="primary-button rounded-full px-5 py-3 text-center text-sm font-semibold">
                Open generator
              </Link>
              <Link href="/" className="secondary-button rounded-full px-5 py-3 text-center text-sm font-medium">
                Return home
              </Link>
            </div>
          </div>
        </div>

        <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {metrics.map((metric) => (
            <article key={metric.label} className="rounded-[28px] border border-white/12 bg-white/[0.04] p-5 shadow-card">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-semibold text-ink">{metric.label}</p>
                <span className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] ${statusClass(metric.status)}`}>
                  {metric.status}
                </span>
              </div>
              <p className="mt-5 text-3xl font-semibold text-ink">{metric.value}</p>
              <p className="mt-3 text-sm leading-6 text-ink/62">{metric.detail}</p>
            </article>
          ))}
        </section>

        <section className="mt-6 grid gap-4 lg:grid-cols-4">
          {lanes.map((lane) => (
            <article key={lane.title} className="rounded-[28px] border border-white/12 bg-white/[0.04] p-5">
              <h2 className="text-sm font-semibold text-ink">{lane.title}</h2>
              <div className="mt-4 grid gap-2">
                {lane.items.map((item) => (
                  <div key={item} className="rounded-[18px] border border-white/10 bg-black/10 px-3 py-2 text-sm text-ink/70">
                    {item}
                  </div>
                ))}
              </div>
            </article>
          ))}
        </section>

        <section className="mt-6 rounded-[30px] border border-white/12 bg-white/[0.04] p-6">
          <p className="section-kicker">Council lanes</p>
          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {councilRoutes.map((route) => (
              <Link key={route.href} href={route.href} className="rounded-[20px] border border-white/10 bg-black/10 p-4 transition hover:border-white/22 hover:bg-white/[0.06]">
                <p className="text-sm font-semibold text-ink">{route.label}</p>
                <p className="mt-2 text-sm leading-6 text-ink/62">{route.detail}</p>
              </Link>
            ))}
          </div>
        </section>

        <section className="mt-6 rounded-[30px] border border-white/12 bg-white/[0.04] p-6">
          <p className="section-kicker">Production council</p>
          <div className="mt-2 flex items-end justify-between gap-3">
            <h2 className="text-2xl font-semibold text-ink">Who builds this</h2>
            <p className="text-xs font-semibold text-ink/42">{COUNCIL_BRAND_LINE}</p>
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {councilRoles.map((role) => (
              <div key={role.id} className="rounded-[20px] border border-white/10 bg-black/10 p-4">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="text-sm font-semibold text-ink">{role.realTitle}</p>
                    <p className="mt-0.5 text-[11px] font-medium text-[var(--gold)]">{role.mythicTitle}</p>
                  </div>
                </div>
                <p className="mt-3 text-xs leading-5 text-ink/55">{role.owns}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-6 rounded-[30px] border border-white/12 bg-white/[0.04] p-6">
          <p className="section-kicker">Next execution order</p>
          <ol className="mt-4 grid gap-3 text-sm leading-6 text-ink/70 md:grid-cols-2">
            <li className="rounded-[18px] border border-white/10 bg-black/10 p-4">1. Run backend compile and tests.</li>
            <li className="rounded-[18px] border border-white/10 bg-black/10 p-4">2. Run frontend type-check and build.</li>
            <li className="rounded-[18px] border border-white/10 bg-black/10 p-4">3. Smoke test health and generation on Railway.</li>
            <li className="rounded-[18px] border border-white/10 bg-black/10 p-4">4. Confirm Whop event delivery before paid claims.</li>
          </ol>
        </section>
      </section>
    </main>
  );
}
