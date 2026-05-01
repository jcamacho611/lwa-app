import type { Metadata } from "next";
import Link from "next/link";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "LWA Opportunities",
  description:
    "Support, advertise, partner, invest, or apply to sell with LWA. Every opportunity starts with a compliant inquiry so we can protect both sides and build trust first.",
  path: "/opportunities",
  keywords: [
    "LWA opportunities",
    "LWA sponsorship",
    "LWA investor inquiry",
    "LWA AI content engine",
    "support LWA",
    "creator economy investment",
  ],
});

const storyStats = [
  { label: "Clip packages per run", value: "Up to 12" },
  { label: "Platforms supported", value: "TikTok, Reels, Shorts, YouTube, X" },
  { label: "AI providers active", value: "Anthropic + OpenAI" },
  { label: "Backend uptime (Railway)", value: "Live now" },
  { label: "Free launch credits", value: "2 per guest session" },
  { label: "Access path", value: "Whop (live)" },
];

const phases = [
  {
    phase: "Phase 0",
    title: "Signal Engine — Live",
    status: "live",
    description:
      "The clip engine is deployed. Any video, audio, stream URL, or upload goes in. Hooks, captions, timestamps, scores, and a full posting strategy come out. The Auto Editor Brain attaches editorial scores, caption style guidance, b-roll suggestions, and platform-specific export profiles to every clip.",
  },
  {
    phase: "Phase 1",
    title: "Creator Workspace",
    status: "building",
    description:
      "Authenticated creator accounts, saved clip vaults, campaign history, posting queue, and the full workspace dashboard. Whop is the live access path. Stripe Connect is wired for the marketplace payout layer.",
  },
  {
    phase: "Phase 2",
    title: "Marketplace & Seller Network",
    status: "next",
    description:
      "Verified seller listings, creator-to-audience commerce, LWA platform percentage via signed terms. Advertising placements, sponsored content packages, and co-branded creator drops.",
  },
  {
    phase: "Phase 3",
    title: "Signal Realms & Creator Identity",
    status: "next",
    description:
      "Creator progression layer — classes, factions, quests, badges, and cosmetic relics. No XP purchases. No feature unlocks from NFTs. Web-first. The characters guide the world the Council builds.",
  },
];

type OpportunityCard = {
  id: string;
  title: string;
  badge: string;
  badgeColor: string;
  description: string;
  legalNote?: string;
  cta: string;
  subject: string;
  accentStyle: string;
};

const opportunities: OpportunityCard[] = [
  {
    id: "support",
    title: "Support the Build",
    badge: "Open",
    badgeColor: "border-emerald-300/30 bg-emerald-300/15 text-emerald-100",
    description:
      "Back the mission directly. Every dollar funds infrastructure, AI compute, and the team shipping the signal engine. No equity transferred. No income guarantee. This is pure patronage for a product you believe in.",
    cta: "Support Now",
    subject: "Support LWA — Patron Inquiry",
    accentStyle: "radial-gradient(circle at top left, rgba(16,185,129,0.22), transparent 55%)",
  },
  {
    id: "sponsorship",
    title: "Sponsorship",
    badge: "Inquiry",
    badgeColor: "border-amber-300/30 bg-amber-300/15 text-amber-100",
    description:
      "Align your brand with LWA's creator audience. Placement opportunities across the platform, content packages, and launch events. Rates and terms reviewed internally before confirmation.",
    legalNote: "No binding agreement until countersigned. Inquiries acknowledged only.",
    cta: "Submit Sponsorship Inquiry",
    subject: "Sponsorship Inquiry — LWA",
    accentStyle: "radial-gradient(circle at top left, rgba(245,158,11,0.22), transparent 55%)",
  },
  {
    id: "advertising",
    title: "Ad Placement",
    badge: "Inquiry",
    badgeColor: "border-amber-300/30 bg-amber-300/15 text-amber-100",
    description:
      "Reach creators at the clip engine. Featured surfaces, notification slots, and co-branded packages. Placements approved case-by-case. Rates confirmed after internal review.",
    legalNote: "No rates committed until internal approval. Inquiries only.",
    cta: "Submit Ad Inquiry",
    subject: "Ad Placement Inquiry — LWA",
    accentStyle: "radial-gradient(circle at top left, rgba(245,158,11,0.18), transparent 55%)",
  },
  {
    id: "invest",
    title: "Investor Portal",
    badge: "Legal Review",
    badgeColor: "border-purple-300/30 bg-purple-300/15 text-purple-100",
    description:
      "Investment, share interest, and equity inquiries. No securities are offered or sold through this website. Legal review is required before any substantive discussion. Both sides need counsel.",
    legalNote:
      "Nothing here constitutes an offer to sell or solicitation to buy any security. All investment discussions require independent legal counsel on both sides.",
    cta: "Submit Investor Inquiry",
    subject: "Investor Inquiry — LWA",
    accentStyle: "radial-gradient(circle at top left, rgba(139,92,246,0.22), transparent 55%)",
  },
  {
    id: "crypto",
    title: "Crypto Support Interest",
    badge: "Legal Review",
    badgeColor: "border-purple-300/30 bg-purple-300/15 text-purple-100",
    description:
      "Interest in supporting LWA via cryptocurrency. No wallet address is live. All crypto pathways require legal and compliance review before activation. No token, NFT, or blockchain economy offered.",
    legalNote: "No crypto payment is collected here. Interest capture only. Compliance review required.",
    cta: "Register Interest",
    subject: "Crypto Support Interest — LWA",
    accentStyle: "radial-gradient(circle at top left, rgba(109,92,255,0.22), transparent 55%)",
  },
  {
    id: "buy-services",
    title: "Buy Services from LWA",
    badge: "Open",
    badgeColor: "border-emerald-300/30 bg-emerald-300/15 text-emerald-100",
    description:
      "Content packages, clip engine runs, strategy consulting, and done-for-you production. Available through approved service agreements. Whop is the live access path for the core product.",
    cta: "Inquire About Services",
    subject: "Services Inquiry — LWA",
    accentStyle: "radial-gradient(circle at top left, rgba(16,185,129,0.18), transparent 55%)",
  },
  {
    id: "marketplace",
    title: "Sell Through LWA",
    badge: "Apply",
    badgeColor: "border-amber-300/30 bg-amber-300/15 text-amber-100",
    description:
      "Apply to become a verified LWA seller. Reach an audience of active creators. LWA collects a platform percentage only through approved, signed terms. No unsolicited commissions.",
    legalNote: "Seller approval not guaranteed. Terms set per seller. No commissions collected until agreement is signed.",
    cta: "Apply to Sell",
    subject: "Marketplace Seller Application — LWA",
    accentStyle: "radial-gradient(circle at top left, rgba(236,72,153,0.22), transparent 55%)",
  },
];

function PhaseStatus({ status }: { status: string }) {
  if (status === "live")
    return (
      <span className="rounded-full border border-emerald-300/30 bg-emerald-300/15 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-100">
        Live
      </span>
    );
  if (status === "building")
    return (
      <span className="rounded-full border border-amber-300/30 bg-amber-300/15 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-amber-100">
        Building
      </span>
    );
  return (
    <span className="rounded-full border border-white/15 bg-white/[0.06] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-ink/52">
      Next
    </span>
  );
}

export default function OpportunitiesPage() {
  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <section className="mx-auto max-w-7xl space-y-6">

        {/* Hero */}
        <div className="rounded-[36px] border border-white/12 bg-[radial-gradient(circle_at_top_left,rgba(109,92,255,0.18),transparent_32%),linear-gradient(180deg,var(--bg-card),var(--bg))] p-6 shadow-card sm:p-10">
          <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--accent-wine)]">
            Compliant by design
          </p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight text-ink sm:text-6xl">
            LWA Opportunities
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-ink/70 sm:text-lg">
            Support, advertise, partner, invest, or apply to sell with LWA.
            Every opportunity starts with a compliant inquiry so we can protect
            both sides and build trust first.
          </p>
          <p className="mt-3 text-sm leading-6 text-ink/44">
            No income guarantees. No securities sold through this website. No
            live crypto collection. No binding agreement until documented and
            countersigned by both parties.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/generate" className="primary-button rounded-full px-5 py-3 text-sm font-semibold">
              Try the Clip Engine
            </Link>
            <Link href="/" className="secondary-button rounded-full px-5 py-3 text-sm font-medium">
              Back to Portal
            </Link>
          </div>
        </div>

        {/* The story */}
        <div className="rounded-[30px] border border-white/10 bg-[radial-gradient(ellipse_at_top,rgba(109,92,255,0.10),transparent_50%),linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.01))] p-6 sm:p-8">
          <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--accent-wine)]">
            The signal thesis
          </p>
          <h2 className="mt-4 text-2xl font-semibold text-ink sm:text-3xl">
            Why LWA exists — and why now
          </h2>

          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <div className="space-y-4 text-sm leading-7 text-ink/70">
              <p>
                <span className="font-semibold text-ink">The creator economy is broken at the production layer.</span>{" "}
                Creators with great ideas spend most of their time on packaging —
                writing hooks, cutting clips, writing captions, figuring out
                when to post and in what order. None of that is the creative
                work. It&apos;s operational overhead.
              </p>
              <p>
                LWA is built to absorb that overhead entirely. Drop any source —
                a raw video, a podcast feed, a Twitch stream URL, a YouTube link
                — and the engine returns a ranked, scored, copy-ready content
                package: best clip first, hooks written, captions set, timestamps
                marked, posting order suggested, platform strategy included.
              </p>
              <p>
                The Auto Editor Brain layer adds editorial intelligence on top:
                viral score, retention estimate, silence risk, dead-scene risk,
                pacing score, caption style guidance, font recommendation,
                b-roll suggestions, and a platform-matched export profile.
                Everything a human editor would tell you — delivered in the same
                API call.
              </p>
            </div>

            <div className="space-y-4 text-sm leading-7 text-ink/70">
              <p>
                <span className="font-semibold text-ink">The business model compounds.</span>{" "}
                The clip engine is the top-of-funnel. Creators get their first
                results for free. When they see what a structured, scored,
                copy-ready package looks like versus a raw download, the value
                is self-evident. The Whop access path is live today. Stripe
                Connect, a verified seller marketplace, and a creator-facing
                workspace are being built on top of that engine.
              </p>
              <p>
                <span className="font-semibold text-ink">The characters are the distribution layer.</span>{" "}
                Athena, the seven agents, the twelve Signal Realms classes and
                twelve factions — these are not cosmetics. They are brand
                infrastructure. Each agent owns a product area and is visible
                in the UI. The Council builds the system. The characters guide
                the world. That line is not a tagline — it is an operating
                principle.
              </p>
              <p>
                <span className="font-semibold text-ink">Every opportunity here is the beginning of a relationship,
                not a transaction.</span>{" "}
                The compliant inquiry model protects both sides. Nothing is
                promised before we talk. Everything is documented before it
                is agreed.
              </p>
            </div>
          </div>

          {/* Stats grid */}
          <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {storyStats.map((stat) => (
              <div key={stat.label} className="metric-tile rounded-[18px] px-4 py-4">
                <p className="text-xs font-semibold text-ink/44">{stat.label}</p>
                <p className="mt-1 text-sm font-semibold text-ink">{stat.value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Roadmap */}
        <div className="rounded-[30px] border border-white/10 bg-white/[0.02] p-6 sm:p-8">
          <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--accent-wine)]">
            Build roadmap
          </p>
          <h2 className="mt-3 text-xl font-semibold text-ink">Where we are. Where we&apos;re going.</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {phases.map((p) => (
              <div key={p.phase} className="rounded-[22px] border border-white/10 bg-black/10 p-5">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-ink/42">
                    {p.phase}
                  </p>
                  <PhaseStatus status={p.status} />
                </div>
                <h3 className="mt-2 text-base font-semibold text-ink">{p.title}</h3>
                <p className="mt-2 text-sm leading-6 text-ink/58">{p.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Opportunity cards */}
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--accent-wine)]">
            Choose your path
          </p>
          <h2 className="mt-2 text-xl font-semibold text-ink">Every opportunity starts with an inquiry</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {opportunities.map((opp) => (
              <article
                key={opp.id}
                id={opp.id}
                className="relative overflow-hidden rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.06),rgba(255,255,255,0.02))] p-6"
              >
                <div
                  className="pointer-events-none absolute inset-0 rounded-[28px]"
                  style={{ background: opp.accentStyle }}
                />
                <div className="relative">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-lg font-semibold text-ink">{opp.title}</h3>
                    <span className={`shrink-0 rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] ${opp.badgeColor}`}>
                      {opp.badge}
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-ink/68">{opp.description}</p>
                  {opp.legalNote && (
                    <p className="mt-3 rounded-[14px] border border-white/8 bg-black/20 px-3 py-2 text-xs leading-5 text-ink/44">
                      {opp.legalNote}
                    </p>
                  )}
                  <a
                    href={`mailto:opportunities@lwa.app?subject=${encodeURIComponent(opp.subject)}`}
                    className="mt-4 inline-flex items-center justify-center rounded-full bg-[var(--gold)] px-5 py-2.5 text-sm font-semibold text-black transition hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[var(--gold)]"
                  >
                    {opp.cta} →
                  </a>
                </div>
              </article>
            ))}
          </div>
        </div>

        {/* Legal footer */}
        <div className="rounded-[24px] border border-white/8 bg-white/[0.02] p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-ink/34">
            Legal disclosure
          </p>
          <p className="mt-3 text-xs leading-6 text-ink/44">
            Nothing on this page constitutes an offer to sell securities, an
            investment contract, a guarantee of return, or a binding service
            agreement. All inquiries are acknowledged only — no transaction,
            commitment, or obligation is created until a separate written
            agreement is signed by both parties. LWA does not collect payments,
            donations, crypto, or investment funds through this page. Equity and
            securities discussions require independent legal counsel. LWA
            reserves the right to decline any inquiry without explanation.
            Whop is the live and approved access path for LWA product purchases.
            All other commercial relationships are in active development and
            subject to internal review.
          </p>
        </div>

      </section>
    </main>
  );
}
