import type { Metadata } from "next";
import Link from "next/link";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Proof Layer",
  description: "Future LWA off-chain provenance shell for deterministic proof records and creator asset history.",
  path: "/proof",
  keywords: ["LWA proof", "creator provenance", "off-chain proof", "Merkle proof"],
});

const phases = [
  { title: "Phase 0", detail: "Off-chain records and deterministic JSON proof exports." },
  { title: "Phase 1", detail: "Optional testnet anchoring only after proof records are stable." },
  { title: "Phase 2", detail: "Optional display layer for earned badges and cosmetic relics after legal/product review." },
];

const rules = [
  "No investment language",
  "No income rights",
  "No feature unlocks",
  "No required wallet",
  "No fractionalization",
  "Cosmetic and provenance only",
];

export default function ProofPage() {
  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <section className="mx-auto max-w-7xl">
        <div className="rounded-[36px] border border-white/12 bg-[radial-gradient(circle_at_top_left,rgba(34,197,94,0.16),transparent_30%),linear-gradient(180deg,var(--bg-card),var(--bg))] p-6 shadow-card sm:p-8">
          <p className="section-kicker">Future provenance layer</p>
          <h1 className="mt-5 text-4xl font-semibold leading-tight text-ink sm:text-6xl">Off-Chain Proof Status</h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-ink/66">
            LWA proof starts with deterministic off-chain records for created clips, badges, and cosmetic identity. This shell does not deploy contracts, require wallets, sell tokens, or unlock app functionality.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/realm" className="primary-button rounded-full px-5 py-3 text-sm font-semibold">View Signal Realms</Link>
            <Link href="/operator" className="secondary-button rounded-full px-5 py-3 text-sm font-medium">Operator center</Link>
          </div>
        </div>

        <section className="mt-6 grid gap-4 md:grid-cols-3">
          {phases.map((phase) => (
            <article key={phase.title} className="rounded-[28px] border border-white/12 bg-white/[0.04] p-5 shadow-card">
              <h2 className="text-lg font-semibold text-ink">{phase.title}</h2>
              <p className="mt-3 text-sm leading-6 text-ink/62">{phase.detail}</p>
            </article>
          ))}
        </section>

        <section className="mt-6 rounded-[30px] border border-white/12 bg-white/[0.04] p-6">
          <h2 className="text-xl font-semibold text-ink">Proof safety rules</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {rules.map((rule) => <div key={rule} className="rounded-[18px] border border-white/10 bg-black/10 p-4 text-sm text-ink/70">{rule}</div>)}
          </div>
        </section>
      </section>
    </main>
  );
}
