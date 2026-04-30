import Link from "next/link";
import { getLwaAgent } from "../lib/lwa-agents";

const primaryAgent = getLwaAgent("omega-prime");

export function WorldHero() {
  return (
    <section className="relative isolate mx-auto grid min-h-[78vh] w-full max-w-7xl items-center gap-10 overflow-hidden rounded-[42px] border border-white/10 bg-black/55 px-5 py-10 shadow-[0_30px_120px_rgba(0,0,0,0.55)] sm:px-8 lg:grid-cols-[0.92fr_1.08fr] lg:px-10 lg:py-12">
      <div className="pointer-events-none absolute inset-0 -z-10" aria-hidden="true">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_-10%,rgba(216,180,92,0.16),transparent_35%),radial-gradient(circle_at_20%_65%,rgba(124,58,237,0.18),transparent_34%),radial-gradient(circle_at_84%_62%,rgba(245,158,11,0.14),transparent_36%),linear-gradient(180deg,rgba(255,255,255,0.055),rgba(0,0,0,0.32))]" />
        <div className="absolute inset-x-8 bottom-10 h-px bg-gradient-to-r from-transparent via-[var(--gold)]/50 to-transparent" />
        <div className="absolute left-1/2 top-1/2 h-[34rem] w-[34rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/10" />
        <div className="absolute left-1/2 top-1/2 h-[24rem] w-[24rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--gold)]/10" />
        <div className="absolute inset-x-10 bottom-0 h-40 rounded-[100%] bg-[radial-gradient(ellipse_at_center,rgba(216,180,92,0.16),transparent_68%)]" />
      </div>

      <div className="relative z-10 text-center lg:text-left">
        <p className="text-[11px] font-semibold uppercase tracking-[0.34em] text-[var(--gold)]">
          LWA — pronounced lee-wuh
        </p>
        <h1 className="mt-5 text-6xl font-semibold leading-[0.88] tracking-[-0.08em] text-ink sm:text-8xl lg:text-[8rem]">
          LWA
        </h1>
        <p className="mt-6 max-w-xl text-lg leading-8 text-ink/72">
          A cinematic AI creator engine for clipping, packaging, creator workflow, and the Seven Agents world system.
        </p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center lg:justify-start">
          <Link href="/generate" className="primary-button inline-flex items-center justify-center rounded-full px-7 py-3.5 text-base font-semibold">
            Enter Clip Engine
          </Link>
          <a href="#agents" className="secondary-button inline-flex items-center justify-center rounded-full px-7 py-3.5 text-base font-medium">
            View Seven Agents
          </a>
        </div>
        <p className="mt-5 max-w-xl text-xs leading-6 text-ink/48">
          The agents are base-model identities and product portals. Character customization is future-ready metadata, not a live avatar editor.
        </p>
      </div>

      <div className="relative min-h-[520px] overflow-hidden rounded-[36px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.07),rgba(255,255,255,0.015))] p-5">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(245,158,11,0.22),transparent_34%),radial-gradient(circle_at_50%_72%,rgba(124,58,237,0.18),transparent_45%)]" />
        <div className="absolute inset-x-10 bottom-14 h-12 rounded-[100%] border border-[var(--gold)]/25 bg-[var(--gold)]/8 blur-[1px]" />
        <div className="absolute left-1/2 top-[54%] h-64 w-44 -translate-x-1/2 -translate-y-1/2 rounded-t-[90px] rounded-b-[36px] border border-[var(--gold)]/30 bg-[linear-gradient(180deg,rgba(255,255,255,0.12),rgba(0,0,0,0.2))] shadow-[0_0_70px_rgba(245,158,11,0.18)]" />
        <div className="absolute left-1/2 top-[39%] h-24 w-24 -translate-x-1/2 rounded-full border border-[var(--gold)]/35 bg-black/35 shadow-[0_0_40px_rgba(245,158,11,0.22)]" />
        <div className="absolute left-[calc(50%-6rem)] top-[50%] h-36 w-10 rotate-[-18deg] rounded-full border border-white/15 bg-white/[0.035]" />
        <div className="absolute right-[calc(50%-6rem)] top-[50%] h-36 w-10 rotate-[18deg] rounded-full border border-white/15 bg-white/[0.035]" />
        <div className="absolute left-1/2 top-[63%] h-28 w-56 -translate-x-1/2 rounded-[40px] border border-white/10 bg-black/25" />
        <div className="absolute left-1/2 top-[50%] h-[23rem] w-[23rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/10" />
        <div className="absolute left-1/2 top-[50%] h-[16rem] w-[16rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[var(--gold)]/15" />
        <div className="absolute inset-x-5 bottom-5 rounded-[26px] border border-white/12 bg-black/62 p-5 backdrop-blur-md">
          <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--gold)]">
            Central Base Model
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-ink">{primaryAgent.name}</h2>
          <p className="mt-2 text-sm leading-6 text-ink/62">{primaryAgent.description}</p>
        </div>
      </div>
    </section>
  );
}
