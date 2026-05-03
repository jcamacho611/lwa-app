import Image from "next/image";
import Link from "next/link";

export default function CinematicHero() {
  return (
    <section className="relative min-h-[88vh] flex items-center overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute right-[-10%] top-[8%] h-[520px] w-[520px] rounded-full bg-[#6D3BFF]/20 blur-[120px]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute left-[-12%] bottom-[0%] h-[420px] w-[420px] rounded-full bg-[#C9A24A]/15 blur-[120px]"
      />

      <div className="mx-auto grid w-full max-w-7xl items-center gap-12 px-6 py-20 lg:grid-cols-[0.92fr_1.08fr]">
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-[#16161B] ring-1 ring-[#2E2E38]">
              <span className="text-lg font-semibold leading-none text-[#C9A24A]">
                L
              </span>
            </span>
            <span className="inline-flex items-baseline gap-1.5 rounded-full bg-[#C9A24A]/8 px-2.5 py-1 font-mono text-[0.72rem] tracking-[0.05em] text-[#E9C77B] ring-1 ring-[#C9A24A]/20">
              LWA · lee-wuh
            </span>
          </div>

          <p className="mt-8 font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
            Meet Lee-Wuh
          </p>

          <h1 className="mt-4 text-balance text-[clamp(2.75rem,6vw,5.25rem)] font-semibold leading-[1.02] tracking-[-0.02em] text-[#F5F1E8]">
            The final boss
            <span className="block text-[#C9A24A]">of lazy content.</span>
          </h1>

          <p className="mt-6 max-w-2xl text-balance text-lg leading-relaxed text-[#B8B3A7]">
            Drop one video. LWA finds the best short-form moments, hooks,
            captions, posting angles, and creator-ready clip packages.
          </p>

          <p className="mt-4 max-w-xl text-sm leading-6 text-[#8F897C]">
            Lee-Wuh is the guardian of the creator engine: Afro-futurist,
            anime-final-boss energy wrapped around a real clipping product.
          </p>

          <div className="mt-10 flex flex-wrap gap-3">
            <Link
              href="/generate"
              className="inline-flex h-12 items-center justify-center rounded-[10px] bg-[#C9A24A] px-5 text-base font-semibold text-[#1a1407] shadow-[0_0_0_1px_rgba(0,0,0,0.4)_inset,0_12px_32px_-16px_rgba(201,162,74,0.55)] transition-all duration-200 hover:-translate-y-px hover:bg-[#E9C77B]"
            >
              Generate My Clip Pack
            </Link>
            <Link
              href="/company-os"
              className="inline-flex h-12 items-center justify-center rounded-[10px] bg-[#1D1D24] px-5 text-base font-medium text-[#F5F1E8] ring-1 ring-[#2E2E38] transition-all duration-200 hover:-translate-y-px hover:bg-[#24242E]"
            >
              Open Company OS
            </Link>
            <Link
              href="/realm"
              className="inline-flex h-12 items-center justify-center rounded-[10px] bg-[#1D1D24] px-5 text-base font-medium text-[#F5F1E8] ring-1 ring-[#2E2E38] transition-all duration-200 hover:-translate-y-px hover:bg-[#24242E]"
            >
              Meet the World
            </Link>
          </div>

          <div className="mt-14 grid max-w-3xl grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { label: "Mascot", value: "Lee-Wuh" },
              { label: "Product", value: "LWA" },
              { label: "Output", value: "Best clip first" },
              { label: "Truth", value: "Rendered" },
            ].map((stat) => (
              <div key={stat.label} className="rounded-[10px] bg-[#16161B] p-4 ring-1 ring-[#23232C]">
                <div className="font-mono text-[0.7rem] uppercase tracking-[0.18em] text-[#7A7568]">
                  {stat.label}
                </div>
                <div className="mt-1 text-xl font-semibold text-[#F5F1E8]">
                  {stat.value}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10">
          <div className="relative overflow-hidden rounded-[28px] border border-[#C9A24A]/25 bg-[#111116] shadow-[0_32px_120px_-48px_rgba(201,162,74,0.55)]">
            <Image
              src="/brand/lee-wuh-hero-16x9.svg"
              alt="Lee-Wuh, the LWA mascot"
              width={1600}
              height={900}
              priority
              className="h-auto w-full object-cover"
            />
            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 via-black/35 to-transparent p-5">
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#E9C77B]">
                Lee-Wuh // The Last Creator
              </p>
              <p className="mt-1 text-sm text-[#D8D0BF]">
                Create. Inspire. Clip smarter.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
