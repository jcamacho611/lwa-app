import type { ClipResult } from "@/lib/types";

type ClipCardProps = {
  clip: ClipResult;
  index: number;
};

export function ClipCard({ clip, index }: ClipCardProps) {
  const timestamp = `${clip.start_time} - ${clip.end_time}`;
  const scoreLabel =
    clip.score > 1 ? `${clip.score}/100` : `${Math.round(clip.score * 100)}%`;

  return (
    <article className="glass-panel group rounded-[1.5rem] p-5 transition duration-200 hover:-translate-y-0.5 hover:border-white/15 hover:bg-white/[0.07]">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-3">
          <div className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-accent">
            Clip {index + 1}
          </div>
          <h3 className="text-xl font-semibold tracking-tight text-white">
            {clip.hook}
          </h3>
        </div>

        <div className="rounded-full bg-white px-3 py-2 text-xs font-semibold text-black shadow-[0_10px_26px_rgba(255,255,255,0.12)]">
          {scoreLabel}
        </div>
      </div>

      <div className="mt-5 grid gap-4 text-sm text-muted sm:grid-cols-2">
        <div className="space-y-1">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/40">
            Caption
          </p>
          <p className="leading-6 text-white/80">{clip.caption}</p>
        </div>

        <div className="space-y-1">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/40">
            Timestamp
          </p>
          <p className="text-white/80">{timestamp}</p>
        </div>

        <div className="space-y-1">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/40">
            CTA Suggestion
          </p>
          <p className="text-white/80">
            {clip.cta_suggestion ?? "Drive viewers into the next action."}
          </p>
        </div>

        <div className="space-y-1">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/40">
            Why This Works
          </p>
          <p className="text-white/80">
            {clip.reason ?? "Strong pacing and a clean attention hook."}
          </p>
        </div>
      </div>
    </article>
  );
}
