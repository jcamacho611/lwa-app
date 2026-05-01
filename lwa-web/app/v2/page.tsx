import type { Metadata } from "next";
import Link from "next/link";
import { Logo } from "../../components/brand/Logo";
import { getAllLwaAgents } from "../../lib/lwa-agents";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "LWA — Afro-futurist Creator Engine",
  description:
    "LWA (pronounced lee-wuh) is an African / Black anime / Afro-futurist mythic sci-fi creator engine. Turn one source into ranked clip packages with hooks, captions, post order, and export-ready packaging.",
  path: "/v2",
  keywords: [
    "lwa",
    "afro-futurist creator engine",
    "ai clipping engine",
    "black anime creator platform",
    "seven agents",
    "signal relics",
  ],
});

const paths = [
  {
    id: "clip-engine",
    title: "Clip Engine",
    badge: "Live",
    badgeTone: "live",
    line: "One source in. Ranked clips, hooks, and a posting package out.",
    cta: "Enter Clip Engine",
    href: "/v2/clip-engine",
  },
  {
    id: "creator-mode",
    title: "Creator Mode",
    badge: "Next",
    badgeTone: "soon",
    line: "Hooks, captions, thumbnails, and posting strategy around every clip.",
    cta: "Open Workspace",
    href: "/dashboard",
  },
  {
    id: "opportunities",
    title: "LWA Opportunities",
    badge: "Open",
    badgeTone: "open",
    line: "Support, advertise, partner, or apply to sell — every path starts with a compliant inquiry.",
    cta: "See Opportunities",
    href: "/opportunities",
  },
  {
    id: "marketplace",
    title: "Marketplace",
    badge: "Apply",
    badgeTone: "inquiry",
    line: "Sellers apply for approved terms. No live payouts until legal review clears.",
    cta: "Apply to Sell",
    href: "/marketplace",
  },
  {
    id: "realm",
    title: "Realm of the Seven",
    badge: "Preview",
    badgeTone: "soon",
    line: "Meet the Seven Agents — guides for clipping, packaging, voice, and trust.",
    cta: "Visit the Realm",
    href: "/realm",
  },
  {
    id: "vault",
    title: "Vault",
    badge: "Soon",
    badgeTone: "soon",
    line: "Past clip packs, exported assets, and proof history (when account is active).",
    cta: "Open Vault",
    href: "/history",
  },
] as const;

const sampleRelics = [
  {
    name: "Threshold Sigil",
    domain: "Hook",
    flavor: "Marks the first three seconds as a covenant.",
    limit: "Loses charge if the hook restates itself.",
  },
  {
    name: "Glyph Veil",
    domain: "Caption",
    flavor: "Renders dense lines into mobile-readable rhythm.",
    limit: "Drains on long monologues.",
  },
  {
    name: "Cadence Drum",
    domain: "Voice",
    flavor: "Marks the natural pulse the speaker is on.",
    limit: "Confuses overlapping speakers.",
  },
];

const badgeStyles: Record<string, string> = {
  live: "bg-emerald-500/14 text-emerald-300 border-emerald-400/26",
  soon: "bg-violet-500/14 text-violet-200 border-violet-400/26",
  inquiry: "bg-amber-500/14 text-amber-200 border-amber-400/26",
  open: "bg-sky-500/14 text-sky-200 border-sky-400/26",
};

export default function V2HomePage() {
  const agents = getAllLwaAgents();

  return (
    <main className="relative min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      {/* Nav */}
      <header className="mx-auto flex max-w-7xl items-center justify-between gap-4 pb-10">
        <Link href="/v2" aria-label="LWA home (v2)">
          <Logo animated />
        </Link>
        <nav className="hidden items-center gap-2 sm:flex">
          <Link
            href="/v2/clip-engine"
            className="primary-button rounded-full px-5 py-2.5 text-sm font-semibold"
          >
            Enter Clip Engine
          </Link>
          <Link
            href="/opportunities"
            className="secondary-button rounded-full px-5 py-2.5 text-sm font-medium"
          >
            Opportunities
          </Link>
        </nav>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-7xl pb-20 text-center">
        <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[var(--accent-wine)]">
          Afro-futurist · Mythic Sci-Fi · Creator Engine
        </p>
        <h1
          className="mx-auto mt-6 max-w-5xl text-6xl font-semibold leading-[0.94] text-ink sm:text-8xl lg:text-[7rem]"
          style={{
            background:
              "linear-gradient(180deg, var(--ink) 0%, var(--ink-mid) 110%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            textShadow: "0 0 40px rgba(179,155,255,0.18)",
          }}
        >
          LWA
        </h1>
        <p className="mt-3 text-[11px] font-medium uppercase tracking-[0.36em] text-ink/55">
          pronounced <span className="text-[var(--gold-bright)]">lee-wuh</span>
        </p>
        <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-subtext">
          A deployed AI creator engine. One source in — ranked clips, hooks,
          captions, timestamps, scores, and a copy-ready posting package out.
          The Seven Agents guide the work. Signal Relics carry the lore.
        </p>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/v2/clip-engine"
            className="primary-button inline-flex items-center justify-center rounded-full px-8 py-4 text-base font-semibold"
          >
            Enter Clip Engine →
          </Link>
          <Link
            href="#seven-agents"
            className="secondary-button inline-flex items-center justify-center rounded-full px-8 py-4 text-base font-medium"
          >
            Meet the Seven Agents
          </Link>
        </div>
      </section>

      {/* Seven Agents grid */}
      <section
        id="seven-agents"
        className="mx-auto max-w-7xl scroll-mt-24 pb-20"
      >
        <div className="mb-10 flex flex-col items-center text-center">
          <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[var(--accent-wine)]">
            The Seven Agents
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-ink sm:text-4xl">
            In-world guides. Future base models.
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-ink/60">
            African / Black anime / Afro-futurist mythic sci-fi character
            foundation. Each agent stewards a layer of the creator workflow.
            Avatar editor, payouts, NFTs, and game economy are{" "}
            <span className="text-ink/80">not live</span> — these are the
            structural roots for what ships next.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {agents.map((agent) => (
            <article
              key={agent.id}
              className="group relative overflow-hidden rounded-3xl border border-white/10 bg-[var(--bg-card)]/40 p-6 backdrop-blur-md transition-all duration-300 hover:border-[var(--gold-border)] hover:shadow-[var(--shadow-glow)]"
              style={{
                background:
                  "linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(0,0,0,0.18) 100%)",
              }}
            >
              <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-500 group-hover:opacity-100"
                style={{
                  background:
                    "radial-gradient(circle at 50% 0%, rgba(179,155,255,0.18), transparent 60%)",
                }}
              />
              <div className="relative">
                <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--gold-bright)]">
                  {agent.title}
                </p>
                <h3 className="mt-2 text-xl font-semibold text-ink">
                  {agent.name}
                </h3>
                <p className="mt-2 text-sm italic text-ink/65">
                  {agent.tagline}
                </p>
                <p className="mt-4 text-xs leading-6 text-ink/50">
                  {agent.productArea}
                </p>
                <div className="mt-5 flex items-center justify-between text-[10px] uppercase tracking-[0.24em]">
                  <span className="text-ink/40">Future base model</span>
                  <span className="text-[var(--accent-wine)]">
                    customizable
                  </span>
                </div>
              </div>
            </article>
          ))}
        </div>
        <p className="mt-8 text-center text-xs leading-6 text-ink/50">
          Visual identity is documented in{" "}
          <span className="text-ink/70">
            docs/lwa-worlds/seven-agents-customization-foundation.md
          </span>{" "}
          — referenced from the live agent registry, not invented per page.
        </p>
      </section>

      {/* Signal Relics teaser */}
      <section className="mx-auto max-w-7xl pb-20">
        <div className="mb-10 text-center">
          <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[var(--accent-wine)]">
            Signal Relics
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-ink sm:text-4xl">
            Original LWA mechanic — not a copy.
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-sm leading-7 text-ink/60">
            Signal Relics are creator-energy artifacts tied to the workflow
            primitives — hook, source, caption, timing, voice, remix,
            packaging, audience, archive. Lore-only today. Cosmetic /
            progression / identity flavor when enabled.{" "}
            <span className="text-ink/80">
              Not NFTs. Not tokens. Not investment.
            </span>{" "}
            Full doc: <span>docs/lwa-worlds/signal-relics.md</span>.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {sampleRelics.map((relic) => (
            <article
              key={relic.name}
              className="rounded-3xl border border-white/10 bg-[var(--bg-card)]/40 p-6 backdrop-blur-md"
            >
              <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--gold-bright)]">
                {relic.domain} relic
              </p>
              <h3 className="mt-2 text-lg font-semibold text-ink">
                {relic.name}
              </h3>
              <p className="mt-3 text-sm leading-6 text-ink/70">
                {relic.flavor}
              </p>
              <p className="mt-4 border-t border-white/8 pt-3 text-xs leading-6 text-ink/45">
                Limit · {relic.limit}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* Path portal */}
      <section className="mx-auto max-w-7xl pb-20">
        <div className="mb-10 text-center">
          <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[var(--accent-wine)]">
            Choose your path
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-ink sm:text-4xl">
            Where do you want to go?
          </h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {paths.map((path) => (
            <Link
              key={path.id}
              href={path.href}
              className="group relative overflow-hidden rounded-3xl border border-white/10 bg-[var(--bg-card)]/40 p-6 backdrop-blur-md transition-all duration-300 hover:border-[var(--gold-border)] hover:shadow-[var(--shadow-glow)]"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-ink">
                  {path.title}
                </h3>
                <span
                  className={[
                    "rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em]",
                    badgeStyles[path.badgeTone] ?? badgeStyles.soon,
                  ].join(" ")}
                >
                  {path.badge}
                </span>
              </div>
              <p className="mt-4 text-sm leading-7 text-ink/65">
                {path.line}
              </p>
              <p className="mt-6 text-sm font-semibold text-[var(--gold-bright)] opacity-70 transition-opacity group-hover:opacity-100">
                {path.cta} →
              </p>
            </Link>
          ))}
        </div>
      </section>

      {/* Compliance footer */}
      <footer className="mx-auto max-w-7xl pb-12">
        <div className="rounded-3xl border border-white/8 bg-black/24 p-6 text-xs leading-6 text-ink/55">
          <p>
            <span className="text-ink/80">LWA</span> is pronounced{" "}
            <span className="text-[var(--gold-bright)]">lee-wuh</span>. African
            / Black anime / Afro-futurist mythic sci-fi creator engine. The
            Clip Engine is live. Whop is the live access path.
          </p>
          <p className="mt-3">
            No guaranteed virality or income claims. No live marketplace
            payouts, live social posting, or live blockchain economy. Marketplace
            participation is application-based and subject to approval. All
            investment, equity, crypto, and revenue-share discussions require
            legal/compliance review before any transaction.
          </p>
        </div>
      </footer>
    </main>
  );
}
