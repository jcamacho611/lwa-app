import Link from "next/link";

export default function ClipEnginePreview() {
  return (
    <section className="relative py-24 border-t border-[#23232C]">
      <div className="mx-auto max-w-6xl px-6">
        <div className="rounded-[20px] p-8 lg:p-12 bg-[#16161B] ring-1 ring-[#23232C] shadow-[0_0_0_1px_rgba(201,162,74,0.18),0_18px_60px_-24px_rgba(201,162,74,0.35)]">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-7">
              <div className="font-mono text-[0.7rem] uppercase tracking-[0.18em] text-[#7A7568]">
                Clip Engine
              </div>
              <h2 className="mt-2 text-[clamp(2rem,4vw,3.25rem)] font-semibold leading-[1.05] tracking-[-0.015em] text-[#F5F1E8] text-balance">
                One link. The best clip, first.
              </h2>
              <p className="mt-4 max-w-xl leading-relaxed text-[#B8B3A7]">
                Drop a YouTube, podcast, or stream URL. LWA renders the lead
                clip immediately and recommends — never overwhelms. Strategy
                notes are clearly labeled. Renders are downloadable.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  href="/generate"
                  className="inline-flex h-12 items-center justify-center rounded-[10px] bg-[#C9A24A] px-5 text-base font-semibold text-[#1a1407] transition-all duration-200 hover:bg-[#E9C77B] hover:-translate-y-px shadow-[0_0_0_1px_rgba(0,0,0,0.4)_inset,0_12px_32px_-16px_rgba(201,162,74,0.55)]"
                >
                  Open the Clip Engine
                </Link>
                <Link
                  href="/history"
                  className="inline-flex h-12 items-center justify-center rounded-[10px] px-5 text-base font-medium text-[#B8B3A7] transition-colors duration-200 hover:text-[#F5F1E8] hover:bg-white/4"
                >
                  View vault →
                </Link>
              </div>
            </div>

            <div className="lg:col-span-5">
              <div className="relative rounded-[20px] overflow-hidden ring-1 ring-[#2E2E38] bg-[#101013] aspect-[9/16] flex items-center justify-center">
                <div
                  aria-hidden
                  className="absolute inset-0 bg-gradient-to-b from-[#4B3A8C]/22 via-transparent to-[#C9A24A]/14"
                />
                <div className="relative text-center px-6">
                  <div className="font-mono text-[0.7rem] uppercase tracking-[0.18em] text-[#7A7568]">
                    Lead clip
                  </div>
                  <div className="mt-2 text-3xl font-semibold tracking-[-0.01em] text-[#F5F1E8]">
                    0:00 → 0:42
                  </div>
                  <div className="mt-2 text-sm text-[#B8B3A7]">
                    Rendered. Ready to post.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
