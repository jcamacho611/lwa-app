"use client";

import Link from "next/link";

type FeatureGatePanelProps = {
  label: string;
  title: string;
  description: string;
  requiredPlan: string;
  bullets?: string[];
};

export function FeatureGatePanel({ label, title, description, requiredPlan, bullets = [] }: FeatureGatePanelProps) {
  return (
    <section className="hero-card rounded-[32px] p-6 sm:p-8">
      <p className="section-kicker">{label}</p>
      <h3 className="mt-3 text-3xl font-semibold text-ink">{title}</h3>
      <p className="mt-4 max-w-3xl text-sm leading-7 text-ink/64">{description}</p>

      {bullets.length ? (
        <div className="mt-6 grid gap-3">
          {bullets.map((item) => (
            <div key={item} className="metric-tile rounded-[24px] px-4 py-3 text-sm text-ink/76">
              {item}
            </div>
          ))}
        </div>
      ) : null}

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <span className="rounded-full border border-accentCrimson/24 bg-[linear-gradient(135deg,rgba(68,16,25,0.82),rgba(184,134,50,0.14))] px-4 py-2 text-sm font-medium text-[#fff4d4] shadow-crimson">
          Unlock on {requiredPlan}
        </span>
        <Link href="/settings" className="primary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold">
          Review plan
        </Link>
        <Link href="/generate" className="secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium">
          Back to clips
        </Link>
      </div>
    </section>
  );
}
