import Link from "next/link";
import { ReactNode } from "react";
import { AIBackground } from "../AIBackground";
import Navbar from "../Navbar";
import { SearchLandingData } from "../../lib/search-pages";

type SearchLandingPageProps = {
  page: SearchLandingData;
  jsonLd?: ReactNode;
};

const searchNavItems = [
  { href: "/generate", label: "Forge Clips" },
  { href: "/compare", label: "Compare" },
  { href: "/use-cases", label: "Use Cases" },
] as const;

export function SearchLandingPage({ page, jsonLd }: SearchLandingPageProps) {
  return (
    <main className="app-shell-grid min-h-screen">
      <AIBackground variant="home" />
      {jsonLd}

      <div className="mx-auto w-full max-w-7xl px-4 pb-20 pt-6 sm:px-6 lg:px-8">
        <Navbar
          items={searchNavItems.map((item) => ({ href: item.href, label: item.label }))}
          variant="home"
          showTagline
          rightSlot={
            <div className="flex items-center gap-2">
              <Link href="/generate" className="primary-button inline-flex rounded-full px-4 py-2.5 text-sm font-semibold">
                Forge Clips
              </Link>
              <Link href="/dashboard" className="secondary-button inline-flex rounded-full px-4 py-2.5 text-sm font-medium">
                Open Control Room
              </Link>
            </div>
          }
        />

        <section className="home-stage grid gap-10 pb-12 pt-16 lg:grid-cols-[1.04fr,0.96fr] lg:items-start">
          <div className="space-y-6">
            <div className="home-stage-grid" aria-hidden="true">
              <div className="home-stage-sigil" />
              <div className="home-stage-constellation" />
              <div className="home-stage-fog" />
            </div>

            <div className="space-y-4">
              <p className="section-kicker">{page.kicker}</p>
              <h1 className="page-title max-w-5xl text-5xl font-semibold leading-[0.98] text-ink sm:text-6xl lg:text-7xl" dir="auto">
                {page.title}
              </h1>
              <p className="max-w-3xl text-base leading-8 text-subtext sm:text-lg" dir="auto">
                {page.description}
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Link href="/generate" className="primary-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold">
                Forge Clips
              </Link>
              <Link href="/dashboard" className="secondary-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-medium">
                Open Control Room
              </Link>
            </div>

            <div className="flex flex-wrap gap-2">
              {page.proofPoints.map((item, index) => (
                <span
                  key={item}
                  className={[
                    "rounded-full border px-3 py-1.5 text-xs font-semibold",
                    index === 0
                      ? "border-accentCrimson/35 bg-[linear-gradient(135deg,rgba(255,0,60,0.2),rgba(255,45,166,0.14),rgba(0,231,255,0.08))] text-white shadow-crimson"
                      : "border-white/10 bg-white/[0.05] text-ink/72",
                  ].join(" ")}
                >
                  {item}
                </span>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div className="home-proof-card home-proof-card-lead rounded-[28px] p-6">
              <p className="section-kicker">Why this page exists</p>
              <h2 className="mt-3 text-2xl font-semibold text-ink">Search should land on something useful, not blog sludge.</h2>
              <p className="mt-3 text-sm leading-7 text-ink/70" dir="auto">
                This page is built to help creators and operators compare tools, understand the workflow, and move directly into a live product path.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              {page.related.map((item, index) => (
                <Link key={item.href} href={item.href} className={index === 0 ? "signal-card rounded-[26px] p-5" : "glass-panel rounded-[26px] p-5"}>
                  <p className="text-sm font-semibold text-ink">{item.label}</p>
                  <p className="mt-2 text-sm leading-6 text-ink/62">Open the next path without leaving the product layer.</p>
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section className="grid gap-5 pb-8 lg:grid-cols-2">
          {page.sections.map((section) => (
            <article key={section.title} className="glass-panel rounded-[28px] p-6">
              <p className="section-kicker">{page.type === "comparison" ? "Compare" : "Use case"}</p>
              <h2 className="mt-3 text-2xl font-semibold text-ink" dir="auto">
                {section.title}
              </h2>
              <p className="mt-4 text-sm leading-7 text-subtext" dir="auto">
                {section.body}
              </p>
              <div className="mt-5 space-y-3">
                {section.bullets.map((bullet) => (
                  <div key={bullet} className="metric-tile rounded-[22px] px-4 py-3 text-sm text-ink/78" dir="auto">
                    {bullet}
                  </div>
                ))}
              </div>
            </article>
          ))}
        </section>

        <section className="hero-card rounded-[30px] p-6 sm:p-8">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <p className="section-kicker">Next move</p>
              <h2 className="mt-3 text-3xl font-semibold text-ink">See the ranked stack live.</h2>
              <p className="mt-4 text-sm leading-7 text-subtext">
                Drop a real source into the generator, open the lead clip first, then move the winners into queue, history, and campaigns.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link href="/generate" className="primary-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold">
                Forge Clips
              </Link>
              <Link href="/campaigns" className="secondary-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-medium">
                Open Missions
              </Link>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
