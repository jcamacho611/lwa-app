import type { ClipResponse } from "@/lib/types";
import { ClipCard } from "./clip-card";

type ResultsSectionProps = {
  result: ClipResponse;
};

export function ResultsSection({ result }: ResultsSectionProps) {
  const bestClip = result.clips[0];

  return (
    <section className="space-y-5">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-accent">
          Results
        </p>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-white">
          Generated clip pack
        </h2>
        <p className="mt-2 text-sm text-muted sm:text-base">
          Review the top-ranked clip first, then scan the rest of the pack for
          alternate hooks and posting angles.
        </p>
      </div>

      {bestClip ? (
        <div className="glass-panel overflow-hidden rounded-[2rem] p-5 shadow-glow">
          <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="rounded-[1.5rem] border border-white/10 bg-gradient-to-br from-accent/15 via-white/[0.02] to-gold/10 p-5">
              <div className="inline-flex items-center rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-black">
                Best Clip
              </div>
              <h3 className="mt-5 text-3xl font-semibold tracking-tight text-white">
                {bestClip.hook}
              </h3>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-muted sm:text-base">
                {bestClip.reason ??
                  "The system surfaced this moment because it combines a clean hook, fast pacing, and a stronger posting angle."}
              </p>

              <div className="mt-6 flex flex-wrap gap-3 text-sm">
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-white/85">
                  Score {bestClip.score > 1 ? bestClip.score : Math.round(bestClip.score * 100)}
                </span>
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-white/85">
                  {bestClip.start_time} - {bestClip.end_time}
                </span>
                {bestClip.packaging_angle ? (
                  <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-white/85">
                    {bestClip.packaging_angle}
                  </span>
                ) : null}
              </div>
            </div>

            <div className="rounded-[1.5rem] border border-white/10 bg-white/[0.03] p-5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/40">
                Recommended caption
              </p>
              <p className="mt-3 text-sm leading-7 text-white/80 sm:text-base">
                {bestClip.caption}
              </p>

              <div className="mt-6 space-y-4">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/40">
                    CTA suggestion
                  </p>
                  <p className="mt-2 text-sm text-white/80">
                    {bestClip.cta_suggestion ??
                      "Push the viewer into the next action with a clean follow-up prompt."}
                  </p>
                </div>

                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/40">
                    Platform fit
                  </p>
                  <p className="mt-2 text-sm text-white/80">
                    {bestClip.platform_fit ??
                      "Optimized for vertical short-form pacing and fast attention capture."}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      <div className="grid gap-4">
        {result.clips.map((clip, index) => (
          <ClipCard key={clip.id} clip={clip} index={index} />
        ))}
      </div>
    </section>
  );
}
