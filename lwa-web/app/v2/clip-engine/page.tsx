import type { Metadata } from "next";
import Link from "next/link";
import { ClipStudio } from "../../../components/clip-studio";
import { Logo } from "../../../components/brand/Logo";
import { buildPageMetadata } from "../../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Clip Engine — LWA",
  description:
    "Source first. Ranked clips out. The LWA Clip Engine turns one long-form source into hooks, captions, timestamps, scores, and a copy-ready posting package.",
  path: "/v2/clip-engine",
  keywords: [
    "lwa clip engine",
    "ai clip generator",
    "rendered clips",
    "strategy only clips",
    "ranked clip packages",
  ],
});

type ClipEnginePageProps = {
  searchParams?: {
    url?: string | string[];
  };
};

const phases = [
  { id: "source", label: "Source" },
  { id: "transcript", label: "Transcript" },
  { id: "ranking", label: "Ranking" },
  { id: "packaging", label: "Packaging" },
  { id: "render", label: "Render" },
];

const laneCopy = [
  {
    label: "Rendered",
    tone: "ready",
    line: "Playable, export-ready, post first.",
    detail:
      "When backend conditions are healthy, rendered cards have a real vertical asset attached. These ship to your platform of choice.",
  },
  {
    label: "Strategy only",
    tone: "strategy",
    line: "Not yet rendered. Recovery available.",
    detail:
      "If a moment is strong but no playable asset is generated, it lands here as a hook + caption + timestamp package you can clip elsewhere or recover later.",
  },
];

export default function V2ClipEnginePage({ searchParams }: ClipEnginePageProps) {
  const queryUrl = Array.isArray(searchParams?.url)
    ? searchParams?.url[0]
    : searchParams?.url;

  return (
    <main className="relative min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      {/* Nav */}
      <header className="mx-auto flex max-w-7xl items-center justify-between gap-4 pb-10">
        <Link href="/v2" aria-label="LWA home (v2)">
          <Logo animated />
        </Link>
        <nav className="hidden items-center gap-2 sm:flex">
          <Link
            href="/v2"
            className="secondary-button rounded-full px-5 py-2.5 text-sm font-medium"
          >
            ← Back to portal
          </Link>
          <Link
            href="/opportunities"
            className="secondary-button rounded-full px-5 py-2.5 text-sm font-medium"
          >
            Opportunities
          </Link>
        </nav>
      </header>

      {/* Operator-grade hero */}
      <section className="mx-auto max-w-7xl pb-12 text-center">
        <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-[var(--accent-wine)]">
          Source first · Ranked out
        </p>
        <h1 className="mx-auto mt-5 max-w-4xl text-4xl font-semibold leading-[1.04] text-ink sm:text-6xl">
          Clip Engine
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-subtext sm:text-lg">
          Paste one source. LWA ranks the strongest short-form cuts, packages
          the hooks, and separates rendered clips from strategy-only ideas.
          Live backend. Honest labeling. No fake video.
        </p>
      </section>

      {/* Phase rail */}
      <section className="mx-auto max-w-5xl pb-10">
        <ol className="grid grid-cols-5 gap-2 rounded-3xl border border-white/10 bg-black/24 p-3 text-center text-[10px] uppercase tracking-[0.28em] text-ink/55">
          {phases.map((phase, idx) => (
            <li
              key={phase.id}
              className="relative rounded-2xl border border-white/6 px-2 py-3"
            >
              <span className="block text-[10px] text-ink/35">
                {String(idx + 1).padStart(2, "0")}
              </span>
              <span className="mt-1 block font-semibold text-ink/75">
                {phase.label}
              </span>
            </li>
          ))}
        </ol>
        <p className="mt-3 text-center text-[11px] uppercase tracking-[0.28em] text-ink/40">
          Live phase tracker arrives next sprint
        </p>
      </section>

      {/* Lane explainer */}
      <section className="mx-auto max-w-7xl pb-12">
        <div className="grid gap-4 sm:grid-cols-2">
          {laneCopy.map((lane) => (
            <div
              key={lane.label}
              className="rounded-3xl border border-white/10 bg-[var(--bg-card)]/40 p-6 backdrop-blur-md"
            >
              <div className="flex items-center justify-between">
                <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--gold-bright)]">
                  {lane.label}
                </p>
                <span
                  className={[
                    "rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em]",
                    lane.tone === "ready"
                      ? "bg-emerald-500/14 text-emerald-300 border-emerald-400/26"
                      : "bg-amber-500/14 text-amber-200 border-amber-400/26",
                  ].join(" ")}
                >
                  {lane.tone === "ready" ? "Live" : "Honest"}
                </span>
              </div>
              <p className="mt-4 text-base font-semibold text-ink">
                {lane.line}
              </p>
              <p className="mt-3 text-sm leading-7 text-ink/60">
                {lane.detail}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Live ClipStudio mounted in new chrome */}
      <section
        id="clip-engine"
        className="relative mx-auto max-w-7xl scroll-mt-24 rounded-[2.5rem] border border-white/10 bg-black/14 p-3 sm:p-6"
      >
        <div className="mb-4 flex items-center justify-between rounded-2xl border border-white/8 bg-black/24 px-4 py-3 text-[11px] uppercase tracking-[0.28em] text-ink/55">
          <span>Live engine · backend connected</span>
          <span className="text-[var(--gold-bright)]">v2 chrome</span>
        </div>
        {/*
          The ClipStudio component below is the existing live engine.
          It is mounted inside the rebuilt v2 chrome above; its internal
          generation flow, API calls, rendered/strategy-only logic, copy
          buttons, and export bundle are preserved exactly.

          The slice-by-slice rebuild of ClipStudio internals continues
          in the next sprint (see components/v2/source-intake-panel.tsx
          for the first extracted slice).
        */}
        <ClipStudio initialSection="generate" initialUrl={queryUrl || ""} />
      </section>

      {/* Compliance footer */}
      <footer className="mx-auto max-w-7xl pb-12 pt-10">
        <p className="text-center text-xs leading-6 text-ink/45">
          Rendered clips ship as real assets when backend conditions allow.
          Strategy-only cards are clearly labeled and never displayed as
          playable video. No guaranteed virality, income, or live posting.
        </p>
      </footer>
    </main>
  );
}
