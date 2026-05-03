import Link from "next/link";
import { LeeWuhPresence } from "../brand/LeeWuhPresence";

export default function CinematicHero() {
  return (
    <section className="relative min-h-[88vh] flex items-center">
      <div className="mx-auto max-w-6xl px-6 w-full lg:grid lg:grid-cols-[1fr_auto] lg:gap-8">
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center justify-center h-9 w-9 rounded-md bg-[#16161B] ring-1 ring-[#2E2E38]">
            <span className="text-[#C9A24A] text-lg leading-none font-semibold">L</span>
          </span>
          <span className="inline-flex items-baseline gap-1.5 px-2.5 py-1 rounded-full bg-[#C9A24A]/8 text-[#E9C77B] ring-1 ring-[#C9A24A]/20 font-mono text-[0.72rem] tracking-[0.05em]">
            LWA · lee-wuh
          </span>
        </div>

        <h1 className="mt-10 text-[clamp(2.75rem,6vw,5.25rem)] font-semibold leading-[1.02] tracking-[-0.02em] text-balance text-[#F5F1E8]">
          The creator engine.
          <span className="block text-[#C9A24A]">Rendered, not rumored.</span>
        </h1>

        <p className="mt-6 max-w-2xl text-lg leading-relaxed text-balance text-[#B8B3A7]">
          One source in. Best clip first. LWA turns long video into proof —
          the recommended cut, ready to post. Strategy is labeled. Renders are
          real.
        </p>

        <div className="mt-10 flex flex-wrap gap-3">
          <Link
            href="/generate"
            className="inline-flex h-12 items-center justify-center rounded-[10px] bg-[#C9A24A] px-5 text-base font-semibold text-[#1a1407] transition-all duration-200 hover:bg-[#E9C77B] hover:-translate-y-px shadow-[0_0_0_1px_rgba(0,0,0,0.4)_inset,0_12px_32px_-16px_rgba(201,162,74,0.55)]"
          >
            Open the Clip Engine
          </Link>
          <Link
            href="/realm"
            className="inline-flex h-12 items-center justify-center rounded-[10px] bg-[#1D1D24] px-5 text-base font-medium text-[#F5F1E8] ring-1 ring-[#2E2E38] transition-all duration-200 hover:bg-[#24242E] hover:-translate-y-px"
          >
            Meet the Seven Agents
          </Link>
        </div>

        <div className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl">
          {[
            { label: "Source", value: "One in" },
            { label: "Output", value: "Best clip first" },
            { label: "Truth", value: "Rendered" },
            { label: "Center", value: "Sacred" },
          ].map((stat) => (
            <div
              key={stat.label}
              className="rounded-[10px] p-4 bg-[#16161B] ring-1 ring-[#23232C]"
            >
              <div className="font-mono text-[0.7rem] uppercase tracking-[0.18em] text-[#7A7568]">
                {stat.label}
              </div>
              <div className="mt-1 text-xl font-semibold text-[#F5F1E8]">
                {stat.value}
              </div>
            </div>
          ))}
        </div>

        {/* Lee-Wuh side guardian - visible on larger screens */}
        <div className="hidden lg:block">
          <LeeWuhPresence
            screen="home"
            state="idle"
            message="Drop one source. I'll find the strongest first move."
          />
        </div>
      </div>
    </section>
  );
}
