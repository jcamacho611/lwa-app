'use client';

import type { ClipBatchResponse } from '@/lib/types';
import { ClipCard } from './ClipCard';

interface ResultsDisplayProps {
  data: ClipBatchResponse;
  onReset: () => void;
}

export function ResultsDisplay({ data, onReset }: ResultsDisplayProps) {
  const { clips, processing_summary: summary, source_platform } = data;

  return (
    <section className="w-full space-y-6 animate-fade-in">
      {/* ── Summary bar ─────────────────────────────────────────────────── */}
      <div className="rounded-2xl border border-neon-purple/20 bg-surface-800/60 backdrop-blur-xl px-5 py-4 shadow-card-premium">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2.5">
              <span className="inline-flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse-slow" />
              <h2 className="text-sm font-bold text-text-primary">
                {clips.length} clip{clips.length !== 1 ? 's' : ''} generated
              </h2>
              <span className="rounded-full border border-neon-purple/30 bg-neon-purple/10 px-2 py-0.5 text-xs font-semibold text-neon-violet">
                Ranked
              </span>
            </div>
            <p className="text-xs text-text-secondary">
              {summary.source_title
                ? `"${summary.source_title}"`
                : `Source: ${source_platform}`}
              {summary.source_duration_seconds
                ? ` · ${formatDuration(summary.source_duration_seconds)}`
                : ''}
              {' · '}
              {summary.target_platform}
              {' · '}
              {summary.ai_provider}
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <div className="flex items-center gap-2 rounded-lg border border-white/8 bg-surface-700/60 px-3 py-1.5">
              <CreditIcon className="h-3.5 w-3.5 text-neon-cyan" />
              <span className="text-xs text-text-secondary">
                <span className="font-bold text-text-primary">
                  {summary.credits_remaining}
                </span>{' '}
                credits left
              </span>
            </div>
            <button
              onClick={onReset}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-text-secondary hover:bg-white/10 hover:text-text-primary transition-colors"
            >
              New video
            </button>
          </div>
        </div>

        {/* Metric pills */}
        <div className="mt-3 flex flex-wrap gap-2">
          <Pill label={summary.plan_name} color="purple" />
          <Pill label={summary.processing_mode} color="slate" />
          {summary.trend_used && (
            <Pill label={`Trend: ${summary.trend_used}`} color="cyan" />
          )}
          {summary.assets_created > 0 && (
            <Pill label={`${summary.assets_created} assets`} color="slate" />
          )}
        </div>
      </div>

      {/* ── Featured top clip ────────────────────────────────────────────── */}
      {clips.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <TrophyIcon className="h-4 w-4 text-neon-violet" />
            <span className="text-xs font-bold text-neon-violet uppercase tracking-widest">
              Top Clip
            </span>
          </div>
          <ClipCard clip={clips[0]} index={0} featured />
        </div>
      )}

      {/* ── Remaining clips ──────────────────────────────────────────────── */}
      {clips.length > 1 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-widest">
              All Clips
            </span>
            <span className="text-xs text-text-muted">
              ({clips.length - 1} more)
            </span>
          </div>
          <div className="space-y-3">
            {clips.slice(1).map((clip, i) => (
              <ClipCard key={clip.id} clip={clip} index={i + 1} />
            ))}
          </div>
        </div>
      )}

      {/* ── Footer action ────────────────────────────────────────────────── */}
      <div className="text-center pt-2">
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 rounded-xl border border-neon-purple/25 bg-neon-purple/10 px-5 py-2.5 text-sm font-semibold text-neon-violet hover:bg-neon-purple/20 hover:border-neon-purple/40 transition-all duration-200"
        >
          <PlusIcon className="h-4 w-4" />
          Analyse another video
        </button>
      </div>
    </section>
  );
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

type PillColor = 'purple' | 'cyan' | 'slate';
const PILL_CLASSES: Record<PillColor, string> = {
  purple: 'border-neon-purple/30 bg-neon-purple/10 text-neon-violet',
  cyan:   'border-neon-cyan/30 bg-neon-cyan/10 text-neon-cyan',
  slate:  'border-white/10 bg-white/5 text-text-secondary',
};

function Pill({ label, color }: { label: string; color: PillColor }) {
  return (
    <span
      className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${PILL_CLASSES[color]}`}
    >
      {label}
    </span>
  );
}

// ─── Icons ───────────────────────────────────────────────────────────────────

function CreditIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.5}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  );
}

function PlusIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 4.5v15m7.5-7.5h-15"
      />
    </svg>
  );
}

function TrophyIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.5}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M7.73 9.728a6.726 6.726 0 002.748 1.35m8.272-6.842V4.5c0 2.108-.966 3.99-2.48 5.228m2.48-5.492a46.32 46.32 0 012.916.52 6.003 6.003 0 01-5.395 4.972m0 0a6.726 6.726 0 01-2.749 1.35m0 0a6.772 6.772 0 01-3.044 0"
      />
    </svg>
  );
}
