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
    <section className="glass-panel rounded-[32px] p-6 sm:p-8">
      <p className="text-xs uppercase tracking-[0.24em] text-muted">{label}</p>
      <h3 className="mt-3 text-3xl font-semibold text-ink">{title}</h3>
      <p className="mt-4 max-w-3xl text-sm leading-7 text-ink/64">{description}</p>

      {bullets.length ? (
        <div className="mt-6 grid gap-3">
          {bullets.map((item) => (
            <div key={item} className="rounded-[24px] border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-ink/76">
              {item}
            </div>
          ))}
        </div>
      ) : null}

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <span className="rounded-full border border-neonPurple/30 bg-neonPurple/12 px-4 py-2 text-sm font-medium text-white">
          Requires {requiredPlan}
        </span>
        <Link href="/settings" className="primary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold">
          Review plan
        </Link>
        <Link href="/generate" className="secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium">
          Keep generating
        </Link>
      </div>
    </section>
  );
}
