import { platforms } from "@/lib/platforms";
import type { PlatformCode } from "@/lib/types";

type InputSectionProps = {
  url: string;
  platform: PlatformCode;
  loading: boolean;
  onUrlChange: (value: string) => void;
  onPlatformChange: (value: PlatformCode) => void;
  onSubmit: () => void;
};

export function InputSection({
  url,
  platform,
  loading,
  onUrlChange,
  onPlatformChange,
  onSubmit,
}: InputSectionProps) {
  return (
    <section
      id="generate"
      className="glass-panel rounded-[1.75rem] px-5 py-5 sm:px-6 sm:py-6"
    >
      <div className="flex flex-col gap-6">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-accent">
            Generate
          </p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-white">
            Build a clip pack
          </h2>
          <p className="mt-2 max-w-2xl text-sm text-muted sm:text-base">
            Paste a public video URL, choose the output surface, and generate a
            ranked pack built for rapid posting decisions.
          </p>
        </div>

        <div className="grid gap-4 lg:grid-cols-[1fr_auto]">
          <label className="space-y-2">
            <span className="text-sm font-medium text-white/80">Video URL</span>
            <input
              type="url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(event) => onUrlChange(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none ring-0 placeholder:text-white/35 transition focus:border-accent/70 focus:bg-white/[0.07]"
            />
          </label>

          <div className="space-y-2">
            <span className="text-sm font-medium text-white/80">Platform</span>
            <div className="flex flex-wrap gap-2">
              {platforms.map((item) => {
                const active = item.value === platform;
                return (
                  <button
                    key={item.value}
                    type="button"
                    onClick={() => onPlatformChange(item.value)}
                    className={[
                      "rounded-full px-4 py-3 text-sm font-medium transition",
                      active
                        ? "bg-white text-black shadow-[0_12px_28px_rgba(255,255,255,0.12)]"
                        : "border border-white/10 bg-white/5 text-white/80 hover:bg-white/[0.08]",
                    ].join(" ")}
                  >
                    {item.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm text-muted">
            Supported output: ranked hooks, captions, timestamps, score, and CTA
            suggestions.
          </div>

          <button
            type="button"
            onClick={onSubmit}
            disabled={loading}
            className="inline-flex items-center justify-center rounded-full bg-button px-6 py-3 text-sm font-semibold text-black transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Analyzing..." : "Generate Clips"}
          </button>
        </div>
      </div>
    </section>
  );
}
