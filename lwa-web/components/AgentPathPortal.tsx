"use client";

import Link from "next/link";
import { useState } from "react";
import { getAllLwaAgents, type LwaAgentId } from "../lib/lwa-agents";

const portalMeta: Record<LwaAgentId, {
  pathLabel: string;
  status: "Live" | "Preview" | "Next" | "Inquiry" | "Apply" | "Soon" | "Trust";
  cta: string;
  route: string;
  placement: string;
  accent: string;
}> = {
  "omega-prime": {
    pathLabel: "Clip Engine",
    status: "Live",
    cta: "Enter Clip Engine",
    route: "/generate",
    placement: "Central command",
    accent: "rgba(245,158,11,0.34)",
  },
  "horned-sentinel": {
    pathLabel: "Creator Mode",
    status: "Preview",
    cta: "Build Creator Package",
    route: "/dashboard",
    placement: "Signal lane",
    accent: "rgba(34,211,238,0.26)",
  },
  "veil-oracle": {
    pathLabel: "Director Brain",
    status: "Next",
    cta: "View Director Brain",
    route: "/realm",
    placement: "Oracle ring",
    accent: "rgba(167,139,250,0.3)",
  },
  "grave-monk": {
    pathLabel: "Opportunities",
    status: "Inquiry",
    cta: "Open Opportunities",
    route: "/opportunities",
    placement: "Gold forum",
    accent: "rgba(245,158,11,0.25)",
  },
  "iron-seraph": {
    pathLabel: "Marketplace",
    status: "Apply",
    cta: "Apply to Sell",
    route: "/opportunities#marketplace",
    placement: "Forge market",
    accent: "rgba(236,72,153,0.24)",
  },
  "shadow-scribe": {
    pathLabel: "Vault / Proof",
    status: "Soon",
    cta: "View Vault",
    route: "/history",
    placement: "Archive gate",
    accent: "rgba(45,212,191,0.24)",
  },
  "jackal-warden": {
    pathLabel: "Trust Layer",
    status: "Trust",
    cta: "Review Trust",
    route: "/opportunities#legal-disclosure",
    placement: "Firewall temple",
    accent: "rgba(248,113,113,0.22)",
  },
};

function statusClass(status: string) {
  if (status === "Live") return "border-emerald-300/30 bg-emerald-300/15 text-emerald-100";
  if (status === "Inquiry" || status === "Apply") return "border-amber-300/30 bg-amber-300/15 text-amber-100";
  if (status === "Trust") return "border-rose-300/30 bg-rose-300/15 text-rose-100";
  return "border-white/15 bg-white/[0.07] text-ink/70";
}

export function AgentPathPortal() {
  const agents = getAllLwaAgents();
  const [activeId, setActiveId] = useState<LwaAgentId | null>("omega-prime");

  return (
    <section id="agents" className="mx-auto w-full max-w-7xl py-16" aria-label="Seven Agents path portal">
      <div className="mb-8 text-center">
        <p className="text-[10px] font-semibold uppercase tracking-[0.32em] text-[var(--gold)]">Seven Agents Portal</p>
        <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] text-ink sm:text-5xl">Choose an agent. Enter a product path.</h2>
        <p className="mx-auto mt-4 max-w-2xl text-sm leading-6 text-ink/58">
          Each LWA agent is a base model, a product guide, and a future customization foundation. Hover, focus, or tap to reveal the destination.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {agents.map((agent) => {
            const meta = portalMeta[agent.id];
            const isActive = activeId === agent.id;

            return (
              <Link
                key={agent.id}
                href={meta.route}
                onMouseEnter={() => setActiveId(agent.id)}
                onFocus={() => setActiveId(agent.id)}
                onClick={() => setActiveId(agent.id)}
                className="group relative min-h-[285px] overflow-hidden rounded-[30px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.065),rgba(255,255,255,0.018))] p-5 transition duration-300 hover:-translate-y-1 hover:border-[var(--gold-border)] hover:shadow-[0_20px_70px_rgba(0,0,0,0.32)] focus:outline-none focus:ring-2 focus:ring-[var(--gold)]/60"
                aria-label={`${agent.name} opens ${meta.pathLabel}`}
              >
                <div className="absolute inset-0 opacity-80 transition duration-300 group-hover:opacity-100" style={{ background: `radial-gradient(circle at 50% 12%, ${meta.accent}, transparent 44%)` }} />
                <div className="absolute left-1/2 top-16 h-28 w-20 -translate-x-1/2 rounded-t-[60px] rounded-b-[24px] border border-white/15 bg-black/25 shadow-[0_0_38px_rgba(255,255,255,0.055)]" />
                <div className="absolute left-1/2 top-9 h-12 w-12 -translate-x-1/2 rounded-full border border-white/18 bg-black/35" />
                <div className="absolute left-1/2 top-[7.5rem] h-10 w-32 -translate-x-1/2 rounded-[100%] border border-white/10 bg-white/[0.025]" />

                <div className="relative z-10 flex h-full flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-ink/48">{meta.placement}</p>
                      <span className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.18em] ${statusClass(meta.status)}`}>{meta.status}</span>
                    </div>
                    <h3 className="mt-20 text-xl font-semibold text-ink">{agent.name}</h3>
                    <p className="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gold)]">{meta.pathLabel}</p>
                    <p className="mt-3 text-sm leading-6 text-ink/62">{agent.tagline}</p>
                  </div>

                  <div className={`mt-5 overflow-hidden transition-all duration-300 ${isActive ? "max-h-56 opacity-100" : "max-h-20 opacity-90 sm:max-h-0 sm:opacity-0 sm:group-hover:max-h-56 sm:group-hover:opacity-100 sm:group-focus:max-h-56 sm:group-focus:opacity-100"}`}>
                    <p className="text-sm leading-6 text-ink/62">{agent.description}</p>
                    <span className="mt-4 inline-flex rounded-full bg-[var(--gold)] px-4 py-2 text-sm font-semibold text-black">{meta.cta} →</span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        <aside className="relative overflow-hidden rounded-[34px] border border-white/10 bg-black/45 p-6 lg:sticky lg:top-6 lg:self-start">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(245,158,11,0.18),transparent_42%)]" />
          <div className="relative">
            <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--gold)]">World routing</p>
            <h3 className="mt-3 text-2xl font-semibold text-ink">No generic homepage. The agents are the map.</h3>
            <p className="mt-4 text-sm leading-7 text-ink/62">
              The portal is built so final 3D character renders can drop into the prepared asset paths without breaking the current build. Until then, the CSS model frames hold the world structure.
            </p>
            <div className="mt-6 space-y-3 text-sm text-ink/62">
              <p><span className="text-ink">Primary:</span> Sovereign Director routes to the working Clip Engine.</p>
              <p><span className="text-ink">Safe money paths:</span> opportunities and marketplace stay inquiry/apply first.</p>
              <p><span className="text-ink">Future identity:</span> base-model customization remains preview-only.</p>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
