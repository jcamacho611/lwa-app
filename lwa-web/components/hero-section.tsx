type HeroSectionProps = {
  onStart: () => void;
};

export function HeroSection({ onStart }: HeroSectionProps) {
  return (
    <section className="relative overflow-hidden rounded-[2rem] border border-line bg-panel/80 px-6 py-8 shadow-glow backdrop-blur-xl sm:px-10 sm:py-12">
      <div className="absolute inset-0 bg-hero opacity-90" />
      <div className="relative flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-accent">
            IWA
          </div>
          <h1 className="max-w-3xl text-balance text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
            Turn Videos Into Viral Clips
          </h1>
          <p className="max-w-2xl text-balance text-base text-muted sm:text-lg">
            AI-powered clip generation in seconds. Paste one source, get back a
            ranked pack with hooks, captions, timestamps, and creator-ready CTAs.
          </p>
        </div>

        <button
          type="button"
          onClick={onStart}
          className="inline-flex items-center justify-center rounded-full bg-button px-6 py-3 text-sm font-semibold text-black transition duration-200 hover:scale-[1.01] hover:shadow-[0_16px_48px_rgba(85,191,255,0.35)]"
        >
          Start Generating
        </button>
      </div>
    </section>
  );
}
