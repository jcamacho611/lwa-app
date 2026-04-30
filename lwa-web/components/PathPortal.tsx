"use client";

import Link from "next/link";
import { useState } from "react";

type PathCard = {
  id: string;
  title: string;
  badge: string;
  badgeTone: "live" | "soon" | "inquiry" | "open";
  tagline: string;
  description: string;
  cta: string;
  href: string;
  accentStyle: string;
  external?: boolean;
};

const paths: PathCard[] = [
  {
    id: "clip-engine",
    title: "Clip Engine",
    badge: "Live",
    badgeTone: "live",
    tagline: "Turn long-form content into viral-ready clips.",
    description:
      "Drop any video, audio, stream, or prompt. Get ranked hooks, captions, timestamps, scores, and a copy-ready posting package.",
    cta: "Enter Clip Engine",
    href: "/generate",
    accentStyle:
      "radial-gradient(circle at top left, rgba(109,92,255,0.34), transparent 60%)",
  },
  {
    id: "creator-mode",
    title: "Creator Mode",
    badge: "Next",
    badgeTone: "soon",
    tagline: "Hooks, captions, thumbnails, full content packages.",
    description:
      "Packaging tools, posting strategy, and output review — available inside the workspace when your account is active.",
    cta: "Open Workspace",
    href: "/dashboard",
    accentStyle:
      "radial-gradient(circle at top left, rgba(16,185,129,0.28), transparent 60%)",
  },
  {
    id: "opportunities",
    title: "LWA Opportunities",
    badge: "Open",
    badgeTone: "open",
    tagline: "Support, advertise, partner, or invest with LWA.",
    description:
      "Every opportunity starts with a compliant inquiry so we can protect both sides and build trust first. No securities sold through this page.",
    cta: "See Opportunities",
    href: "/opportunities",
    accentStyle:
      "radial-gradient(circle at top left, rgba(245,158,11,0.28), transparent 60%)",
  },
  {
    id: "marketplace",
    title: "Marketplace",
    badge: "Apply",
    badgeTone: "soon",
    tagline: "Sell products and services through LWA.",
    description:
      "Apply to become a verified seller. LWA helps drive creator attention and collects a platform percentage only through approved terms.",
    cta: "Apply to Sell",
    href: "/opportunities#marketplace",
    accentStyle:
      "radial-gradient(circle at top left, rgba(236,72,153,0.26), transparent 60%)",
  },
  {
    id: "investor",
    title: "Investor Portal",
    badge: "Inquiry",
    badgeTone: "inquiry",
    tagline: "Investment, sponsorship, and partnership inquiries.",
    description:
      "Legal review is required before any securities or equity discussion takes place. Inquiries only — no securities are sold through this website.",
    cta: "Submit Inquiry",
    href: "/opportunities#invest",
    accentStyle:
      "radial-gradient(circle at top left, rgba(139,92,246,0.26), transparent 60%)",
  },
  {
    id: "vault",
    title: "Vault",
    badge: "Soon",
    badgeTone: "soon",
    tagline: "Your saved outputs and history.",
    description:
      "Access past clip packs, archived runs, and saved packages. Sign in to open your vault.",
    cta: "Open Vault",
    href: "/history",
    accentStyle:
      "radial-gradient(circle at top left, rgba(20,184,166,0.26), transparent 60%)",
  },
];

function badgeClass(tone: PathCard["badgeTone"]) {
  if (tone === "live")
    return "border-emerald-300/30 bg-emerald-300/15 text-emerald-100";
  if (tone === "open")
    return "border-amber-300/30 bg-amber-300/15 text-amber-100";
  if (tone === "inquiry")
    return "border-purple-300/30 bg-purple-300/15 text-purple-100";
  return "border-white/15 bg-white/[0.07] text-ink/68";
}

export function PathPortal() {
  const [activeId, setActiveId] = useState<string | null>(null);

  return (
    <section
      className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
      aria-label="LWA path selection"
    >
      {paths.map((path) => {
        const isActive = activeId === path.id;
        const inner = (
          <div className="relative p-6">
            <div
              className="pointer-events-none absolute inset-0 rounded-[28px] transition-opacity duration-300"
              style={{
                background: path.accentStyle,
                opacity: isActive ? 1 : 0.55,
              }}
            />
            <div className="relative">
              <div className="flex items-start justify-between gap-3">
                <h3 className="text-xl font-semibold text-ink">{path.title}</h3>
                <span
                  className={`shrink-0 rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] ${badgeClass(path.badgeTone)}`}
                >
                  {path.badge}
                </span>
              </div>
              <p className="mt-3 text-sm font-medium leading-6 text-ink/72">
                {path.tagline}
              </p>

              <div
                className="overflow-hidden transition-all duration-300"
                style={{
                  maxHeight: isActive ? "220px" : "0px",
                  opacity: isActive ? 1 : 0,
                  marginTop: isActive ? "16px" : "0px",
                }}
              >
                <p className="text-sm leading-6 text-ink/60">
                  {path.description}
                </p>
                <span className="mt-4 inline-flex items-center justify-center rounded-full bg-[var(--gold)] px-5 py-2.5 text-sm font-semibold text-black transition hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[var(--gold)]">
                  {path.cta} →
                </span>
              </div>
            </div>
          </div>
        );

        const cardClass =
          "group relative block overflow-hidden rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.06),rgba(255,255,255,0.02))] transition-all duration-300 hover:border-[var(--gold-border)] hover:shadow-[0_16px_48px_rgba(109,92,255,0.18)] focus-within:border-[var(--gold-border)] focus-within:shadow-[0_16px_48px_rgba(109,92,255,0.18)]";

        return (
          <div
            key={path.id}
            onMouseEnter={() => setActiveId(path.id)}
            onMouseLeave={() => setActiveId(null)}
            onFocus={() => setActiveId(path.id)}
            onBlur={() => setActiveId(null)}
          >
            {path.external ? (
              <a
                href={path.href}
                target="_blank"
                rel="noreferrer"
                className={cardClass}
                aria-label={`${path.title} — ${path.tagline}`}
              >
                {inner}
              </a>
            ) : (
              <Link
                href={path.href}
                className={cardClass}
                aria-label={`${path.title} — ${path.tagline}`}
              >
                {inner}
              </Link>
            )}
          </div>
        );
      })}
    </section>
  );
}
