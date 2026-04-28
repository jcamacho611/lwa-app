"use client";

import Link from "next/link";
import { MoneyCtaPanel } from "./money-cta-panel";

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
        <span className="rounded-full border border-[var(--gold-border)] bg-[linear-gradient(135deg,var(--surface-veil-heavy),var(--gold-dim),var(--surface-gold-ghost))] px-4 py-2 text-sm font-medium text-[var(--gold)] shadow-cyan">
          Unlock on {requiredPlan}
        </span>
        <Link href="/generate" className="secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium">
          Back to clips
        </Link>
      </div>

      <div className="mt-6">
        <MoneyCtaPanel
          variant="compact"
          source={`feature_gate_${label.toLowerCase().replace(/\s+/g, "_")}`}
          title="Choose an upgrade path"
          description="Use checkout, demo, or referral paths when configured. Access still depends on the selected platform."
        />
      </div>
    </section>
  );
}
