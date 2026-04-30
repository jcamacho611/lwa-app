import type { Metadata } from "next";
import Link from "next/link";
import { AgentPathPortal } from "../components/AgentPathPortal";
import { WorldHero } from "../components/WorldHero";
import { Logo } from "../components/brand/Logo";
import { buildUtmUrl, getPrimaryMoneyLink } from "../lib/money-links";
import { COUNCIL_BRAND_LINE } from "../lib/production-council";
import { buildPageMetadata } from "../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "LWA — Seven Agents Creator Engine",
  description:
    "LWA, pronounced lee-wuh, is an AI creator engine built around clipping, packaging, creator workflow, and the Seven Agents world portal.",
  path: "/",
  keywords: [
    "LWA lee-wuh",
    "Seven Agents creator engine",
    "AI clipping engine",
    "Afro-futurist creator workflow",
    "viral clip packages",
  ],
});

const proofPoints = [
  "Best clip first",
  "Rendered proof when available",
  "Strategy-only results separated",
  "Hooks, captions, timestamps",
  "Seven Agents path system",
  "Future base-model identity",
];

export default function HomePage() {
  const primaryLink = getPrimaryMoneyLink();
  const primaryLinkUrl = buildUtmUrl(primaryLink, "homepage_agent_world");

  return (
    <main className="relative min-h-screen overflow-hidden px-4 py-6 sm:px-6 lg:px-8">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[#030305]" aria-hidden="true" />
      <div
        className="pointer-events-none fixed inset-0 -z-10 opacity-90"
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(ellipse 90% 70% at 50% 0%, rgba(245,158,11,0.12), transparent 58%), radial-gradient(ellipse 70% 55% at 15% 78%, rgba(124,58,237,0.14), transparent 62%), radial-gradient(ellipse 70% 55% at 88% 72%, rgba(236,72,153,0.10), transparent 58%)",
        }}
      />

      <header className="mx-auto flex max-w-7xl items-center justify-between gap-4 pb-6">
        <Link href="/" aria-label="LWA home">
          <Logo animated />
        </Link>
        <nav className="hidden items-center gap-2 sm:flex">
          <Link href="/generate" className="primary-button rounded-full px-5 py-2.5 text-sm font-semibold">
            Enter Clip Engine
          </Link>
          <a href={primaryLinkUrl} target="_blank" rel="noreferrer" className="secondary-button rounded-full px-5 py-2.5 text-sm font-medium">
            Support LWA
          </a>
        </nav>
      </header>

      <WorldHero />
      <AgentPathPortal />

      <section className="mx-auto grid w-full max-w-7xl gap-4 pb-16 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-[32px] border border-white/10 bg-white/[0.035] p-6">
          <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--gold)]">Clip Engine stays live</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] text-ink">The world points back to the working product.</h2>
          <p className="mt-4 text-sm leading-7 text-ink/62">
            The Seven Agents are the front door, but the core product remains the deployed Clip Engine. Enter `/generate` to paste a source and create ranked clip packages.
          </p>
          <Link href="/generate" className="primary-button mt-6 inline-flex rounded-full px-6 py-3 text-sm font-semibold">
            Open /generate
          </Link>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {proofPoints.map((item) => (
            <div key={item} className="metric-tile rounded-[24px] px-4 py-4 text-sm font-medium text-ink/80 backdrop-blur-sm">
              {item}
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl pb-12">
        <div className="rounded-[32px] border border-white/10 bg-black/35 p-6">
          <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--gold)]">How LWA is built</p>
          <p className="mt-2 text-base font-semibold text-ink sm:text-lg">{COUNCIL_BRAND_LINE}</p>
          <p className="mt-4 text-xs leading-6 text-subtext/70">
            No guaranteed virality or income claims. No live marketplace payouts, live social posting, crypto wallet collection, direct share sales, or blockchain economy. Opportunity paths are inquiry/apply first and require review where needed.
          </p>
        </div>
      </section>
    </main>
  );
}
