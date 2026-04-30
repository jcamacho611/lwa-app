import type { Metadata } from "next";
import Link from "next/link";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "LWA Marketplace",
  description: "Future LWA marketplace shell for templates, hooks, caption packs, brand kits, and creator services.",
  path: "/marketplace",
  keywords: ["LWA marketplace", "creator templates", "hook packs", "caption packs"],
});

const futureListings = [
  { title: "Hook packs", detail: "Reusable short-form openers organized by platform, niche, and offer type." },
  { title: "Caption presets", detail: "Creator-native caption style recipes for rendered clips and packaging workflows." },
  { title: "Brand kits", detail: "Visual direction, tone, CTA rules, and reusable clip packaging systems." },
  { title: "Campaign kits", detail: "Lead, trust, sales, education, retargeting, and community clip bundles." },
];

const readinessRules = [
  "Earnings vary",
  "No guaranteed income claims",
  "Listings require review before public launch",
  "Clear refund and dispute rules first",
  "Digital goods only in the first version",
  "Trust and safety comes before scale",
];

export default function MarketplacePage() {
  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <section className="mx-auto max-w-7xl">
        <div className="rounded-[36px] border border-white/12 bg-[radial-gradient(circle_at_top_left,rgba(16,185,129,0.18),transparent_30%),linear-gradient(180deg,var(--bg-card),var(--bg))] p-6 shadow-card sm:p-8">
          <p className="section-kicker">Future creator economy layer</p>
          <h1 className="mt-5 text-4xl font-semibold leading-tight text-ink sm:text-6xl">LWA Marketplace</h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-ink/66">
            The marketplace will organize hooks, templates, captions, brand kits, and campaign systems into creator-ready assets. This page is a future-phase shell and does not claim the marketplace is publicly launched yet.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/generate" className="primary-button rounded-full px-5 py-3 text-sm font-semibold">Generate first</Link>
            <Link href="/operator" className="secondary-button rounded-full px-5 py-3 text-sm font-medium">Review launch status</Link>
          </div>
        </div>

        <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {futureListings.map((item) => (
            <article key={item.title} className="rounded-[28px] border border-white/12 bg-white/[0.04] p-5 shadow-card">
              <h2 className="text-lg font-semibold text-ink">{item.title}</h2>
              <p className="mt-3 text-sm leading-6 text-ink/62">{item.detail}</p>
            </article>
          ))}
        </section>

        <section className="mt-6 rounded-[30px] border border-white/12 bg-white/[0.04] p-6">
          <h2 className="text-xl font-semibold text-ink">Marketplace readiness gates</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {readinessRules.map((rule) => (
              <div key={rule} className="rounded-[18px] border border-white/10 bg-black/10 p-4 text-sm text-ink/70">{rule}</div>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}
