import type { Metadata } from "next";
import Link from "next/link";
import { Logo } from "../components/brand/Logo";
import { PathPortal } from "../components/PathPortal";
import { buildUtmUrl, getPrimaryMoneyLink } from "../lib/money-links";
import { COUNCIL_BRAND_LINE } from "../lib/production-council";
import { buildPageMetadata } from "../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "LWA — AI Content Engine",
  description:
    "LWA turns long-form videos, uploads, and creator sources into short-form content packages with hooks, captions, timestamps, scores, and platform strategy.",
  path: "/",
  keywords: [
    "LWA ai content engine",
    "viral clip packages",
    "hooks captions timestamps",
    "creator workflow",
    "twitch stream clipping",
  ],
});

const proofPoints = [
  "Best clip first",
  "Rendered proof when available",
  "Strategy fallback stays separate",
  "Hooks, captions, timestamps",
  "Score and post order",
  "Copy-ready package",
];

export default function HomePage() {
  const primaryLink = getPrimaryMoneyLink();
  const primaryLinkUrl = buildUtmUrl(primaryLink, "homepage_hero");

  return (
    <section className="relative min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      {/* Cinematic background radial layers */}
      <div
        className="pointer-events-none fixed inset-0 -z-10"
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(ellipse 80% 60% at 50% -10%, rgba(109,92,255,0.22), transparent 70%), radial-gradient(ellipse 60% 50% at 90% 80%, rgba(185,28,28,0.18), transparent 60%), radial-gradient(ellipse 50% 40% at 10% 90%, rgba(16,185,129,0.12), transparent 60%)",
        }}
      />

      {/* Header */}
      <header className="mx-auto flex max-w-7xl items-center justify-between gap-4 pb-6">
        <Link href="/" aria-label="LWA home">
          <Logo animated />
        </Link>
        <nav className="hidden items-center gap-2 sm:flex">
          <Link
            href="/generate"
            className="primary-button rounded-full px-5 py-2.5 text-sm font-semibold"
          >
            Enter Clip Engine
          </Link>
          <a
            href={primaryLinkUrl}
            target="_blank"
            rel="noreferrer"
            className="secondary-button rounded-full px-5 py-2.5 text-sm font-medium"
          >
            Support LWA
          </a>
        </nav>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-7xl pt-10 pb-14 text-center">
        <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[var(--accent-wine)]">
          Any source in. Creator-ready content out.
        </p>
        <h1 className="mx-auto mt-6 max-w-4xl text-5xl font-semibold leading-[0.96] text-ink sm:text-7xl lg:text-[5.5rem]">
          LWA
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-base leading-8 text-subtext sm:text-lg">
          A deployed AI clipping engine that turns long-form videos, uploads,
          and creator sources into short-form content packages — hooks,
          captions, timestamps, scores, and platform strategy.
        </p>

        {/* Cinematic character visual */}
        <div className="relative mx-auto mt-10 max-w-xs overflow-hidden rounded-[38px] border border-white/14 shadow-[0_28px_90px_rgba(88,70,140,0.22)]">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_18%,rgba(236,72,153,0.20),transparent_30%),radial-gradient(circle_at_78%_24%,rgba(109,92,255,0.18),transparent_34%),radial-gradient(circle_at_56%_86%,rgba(16,185,129,0.18),transparent_30%)]" />
          <div className="relative overflow-hidden rounded-[38px] bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(0,0,0,0.18))]">
            <img
              src="/brand-source/chars/athena.png"
              alt="LWA — the signal engine"
              className="h-full min-h-[280px] w-full object-cover object-center"
            />
            <div className="absolute inset-x-4 bottom-4 rounded-[22px] border border-white/12 bg-black/58 p-4 backdrop-blur-md">
              <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-[var(--gold)]">
                Signal engine active
              </p>
              <p className="mt-1 text-sm font-semibold text-ink">
                The characters guide the world.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/generate"
            className="primary-button inline-flex items-center justify-center rounded-full px-7 py-3.5 text-base font-semibold"
          >
            Enter Clip Engine
          </Link>
          <Link
            href="/operator"
            className="secondary-button inline-flex items-center justify-center rounded-full px-7 py-3.5 text-base font-medium"
          >
            Operator Center
          </Link>
        </div>
      </section>

      {/* Path portal */}
      <section className="mx-auto max-w-7xl pb-10">
        <div className="mb-6 text-center">
          <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--accent-wine)]">
            Choose your path
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-ink sm:text-3xl">
            Where do you want to go?
          </h2>
          <p className="mt-2 text-sm text-ink/52">
            Hover or focus a card to see what each path takes you to.
          </p>
        </div>
        <PathPortal />
      </section>

      {/* Council line */}
      <section className="mx-auto max-w-7xl pb-4">
        <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--accent-wine)]">
          How LWA is built
        </p>
        <p className="mt-2 text-base font-semibold text-ink sm:text-lg">
          {COUNCIL_BRAND_LINE}
        </p>
      </section>

      {/* Proof points */}
      <section className="mx-auto grid w-full max-w-7xl gap-3 pb-16 sm:grid-cols-3 lg:grid-cols-6">
        {proofPoints.map((item) => (
          <div
            key={item}
            className="metric-tile rounded-[22px] px-4 py-4 text-sm font-medium text-ink/80 backdrop-blur-sm"
          >
            {item}
          </div>
        ))}
      </section>

      <p className="mx-auto max-w-7xl pb-10 text-xs leading-6 text-subtext/70">
        No guaranteed virality or income claims. No live marketplace payouts, live social posting, or blockchain economy. Whop is the live access path. All other features are in active development.
      </p>
    </section>
  );
}
