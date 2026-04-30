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
    "LWA advertising",
    "LWA investor inquiry",
    "LWA marketplace seller",
    "support LWA",
  ],
});

type OpportunityCard = {
  id: string;
  title: string;
  badge: string;
  badgeColor: string;
  description: string;
  legalNote?: string;
  cta: string;
  href: string;
  accentStyle: string;
};

const opportunities: OpportunityCard[] = [
  {
    id: "support",
    title: "Support LWA",
    badge: "Open",
    badgeColor: "border-emerald-300/30 bg-emerald-300/15 text-emerald-100",
    description:
      "Back the mission directly. Every contribution funds infrastructure, tooling, and the team building the signal engine.",
    cta: "Support Now",
    href: "#inquiry-support",
    accentStyle:
      "radial-gradient(circle at top left, rgba(16,185,129,0.22), transparent 55%)",
  },
  {
    id: "sponsorship",
    title: "Sponsorship Inquiry",
    badge: "Inquiry",
    badgeColor: "border-amber-300/30 bg-amber-300/15 text-amber-100",
    description:
      "Align your brand with LWA's creator audience. Placement opportunities exist across the platform, content packages, and launch events.",
    legalNote:
      "Sponsorship terms reviewed internally before confirmation. No binding agreement until countersigned.",
    cta: "Submit Sponsorship Inquiry",
    href: "#inquiry-sponsorship",
    accentStyle:
      "radial-gradient(circle at top left, rgba(245,158,11,0.22), transparent 55%)",
  },
  {
    id: "advertising",
    title: "Ad Placement Inquiry",
    badge: "Inquiry",
    badgeColor: "border-amber-300/30 bg-amber-300/15 text-amber-100",
    description:
      "Reach creators at the clip engine. Placement options include featured surfaces, notification slots, and co-branded packages.",
    legalNote:
      "Ad placements are approved on a case-by-case basis. Rates confirmed only after internal review.",
    cta: "Submit Ad Inquiry",
    href: "#inquiry-advertising",
    accentStyle:
      "radial-gradient(circle at top left, rgba(245,158,11,0.20), transparent 55%)",
  },
  {
    id: "invest",
    title: "Investor Portal",
    badge: "Legal Review",
    badgeColor: "border-purple-300/30 bg-purple-300/15 text-purple-100",
    description:
      "Investment, share interest, and equity inquiries. No securities are offered or sold through this website. Legal review is required before any substantive discussion takes place.",
    legalNote:
      "This is an inquiry form only. Nothing on this page constitutes an offer to sell, a solicitation of an offer to buy, or a recommendation of any security. All investment discussions require legal counsel on both sides.",
    cta: "Submit Investor Inquiry",
    href: "#inquiry-invest",
    accentStyle:
      "radial-gradient(circle at top left, rgba(139,92,246,0.22), transparent 55%)",
  },
  {
    id: "crypto",
    title: "Crypto Support Interest",
    badge: "Legal Review",
    badgeColor: "border-purple-300/30 bg-purple-300/15 text-purple-100",
    description:
      "Interest in supporting LWA via cryptocurrency. No wallet address is live on this page. All crypto support pathways require legal and compliance review before activation.",
    legalNote:
      "No crypto payment is collected here. This is an interest-capture form only. No blockchain economy, token, or NFT is offered by LWA at this time.",
    cta: "Register Interest",
    href: "#inquiry-crypto",
    accentStyle:
      "radial-gradient(circle at top left, rgba(109,92,255,0.22), transparent 55%)",
  },
  {
    id: "buy-services",
    title: "Buy Services from LWA",
    badge: "Open",
    badgeColor: "border-emerald-300/30 bg-emerald-300/15 text-emerald-100",
    description:
      "Content packages, clip engine runs, strategy consulting, and done-for-you production available through approved service agreements.",
    cta: "Inquire About Services",
    href: "#inquiry-services",
    accentStyle:
      "radial-gradient(circle at top left, rgba(16,185,129,0.18), transparent 55%)",
  },
  {
    id: "marketplace",
    title: "Sell Through LWA Marketplace",
    badge: "Apply",
    badgeColor: "border-amber-300/30 bg-amber-300/15 text-amber-100",
    description:
      "Apply to become a verified LWA seller. Reach an audience of active creators. LWA collects a platform percentage only through approved, signed terms.",
    legalNote:
      "Seller approval is not guaranteed. Terms are set per seller. No commissions are collected until a seller agreement is signed.",
    cta: "Apply to Sell",
    href: "#inquiry-marketplace",
    accentStyle:
      "radial-gradient(circle at top left, rgba(236,72,153,0.22), transparent 55%)",
  },
];

export default function OpportunitiesPage() {
  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <section className="mx-auto max-w-7xl">
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
          <p className="mt-4 text-sm leading-6 text-ink/48">
            No income guarantees. No securities sold through this website. No
            live crypto collection. No binding agreement until documented and
            countersigned.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="/generate"
              className="primary-button rounded-full px-5 py-3 text-sm font-semibold"
            >
              Enter Clip Engine
            </Link>
            <Link
              href="/"
              className="secondary-button rounded-full px-5 py-3 text-sm font-medium"
            >
              Back to Portal
            </Link>
          </div>
        </div>

        {/* Opportunity cards */}
        <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3" id="opportunities-grid">
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
                  <h2 className="text-lg font-semibold text-ink">
                    {opp.title}
                  </h2>
                  <span
                    className={`shrink-0 rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] ${opp.badgeColor}`}
                  >
                    {opp.badge}
                  </span>
                </div>
                <p className="mt-3 text-sm leading-6 text-ink/68">
                  {opp.description}
                </p>
                {opp.legalNote && (
                  <p className="mt-3 rounded-[14px] border border-white/8 bg-black/20 px-3 py-2 text-xs leading-5 text-ink/48">
                    {opp.legalNote}
                  </p>
                )}
                <a
                  href={`mailto:opportunities@lwa.app?subject=${encodeURIComponent(opp.title)}`}
                  className="mt-4 inline-flex items-center justify-center rounded-full bg-[var(--gold)] px-5 py-2.5 text-sm font-semibold text-black transition hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[var(--gold)]"
                >
                  {opp.cta} →
                </a>
              </div>
            </article>
          ))}
        </section>

        {/* Legal footer */}
        <section className="mt-8 rounded-[24px] border border-white/8 bg-white/[0.02] p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-ink/38">
            Legal disclosure
          </p>
          <p className="mt-3 text-xs leading-6 text-ink/48">
            Nothing on this page constitutes an offer to sell securities, an
            investment contract, a guarantee of return, or a binding service
            agreement. All inquiries are acknowledged only — no transaction,
            commitment, or obligation is created until a separate written
            agreement is signed by both parties. LWA does not collect payments,
            donations, crypto, or investment funds through this page. Equity and
            securities discussions require independent legal counsel. LWA
            reserves the right to decline any inquiry without explanation.
          </p>
          <p className="mt-3 text-xs leading-6 text-ink/38">
            Whop is the live and approved access path for LWA product purchases.
            All other commercial relationships are in active development and
            subject to internal review.
          </p>
        </section>
      </section>
    </main>
  );
}
