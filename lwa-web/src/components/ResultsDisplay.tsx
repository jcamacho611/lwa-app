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
      {/* Summary bar */}
      <div className="rounded-2xl border border-white/8 bg-surface-700 px-5 py-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="inline-flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse-slow" />
              <h2 className="text-sm font-semibold text-white">
                {clips.length} clip{clips.length !== 1 ? 's' : ''} generated
              </h2>
            </div>
            <p className="text-xs text-slate-400">
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

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 rounded-lg border border-white/8 bg-surface-600 px-3 py-1.5">
              <CreditIcon className="h-3.5 w-3.5 text-brand-400" />
              <span className="text-xs text-slate-300">
                <span className="font-semibold text-white">{summary.credits_remaining}</span> credits left
              </span>
            </div>
            <button
              onClick={onReset}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-white/10 hover:text-white transition-colors"
            >
              New video
            </button>
          </div>
        </div>

        {/* Plan + processing mode pills */}
        <div className="mt-3 flex flex-wrap gap-2">
          <Pill label={summary.plan_name} color="brand" />
          <Pill label={summary.processing_mode} color="slate" />
          {summary.trend_used && <Pill label={`Trend: ${summary.trend_used}`} color="violet" />}
        </div>
      </div>

      {/* Clip cards */}
      <div className="space-y-4">
        {clips.map((clip, i) => (
          <ClipCard key={clip.id} clip={clip} index={i} />
        ))}
      </div>

      {/* Footer action */}
      <div className="text-center pt-2">
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-5 py-2.5 text-sm font-medium text-slate-300 hover:bg-white/10 hover:text-white transition-colors"
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

type PillColor = 'brand' | 'violet' | 'slate';
const PILL_CLASSES: Record<PillColor, string> = {
  brand:  'border-brand-500/30 bg-brand-500/10 text-brand-400',
  violet: 'border-violet-500/30 bg-violet-500/10 text-violet-400',
  slate:  'border-white/10 bg-white/5 text-slate-400',
};

function Pill({ label, color }: { label: string; color: PillColor }) {
  return (
    <span className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${PILL_CLASSES[color]}`}>
      {label}
    </span>
  );
}

// ─── Icons ───────────────────────────────────────────────────────────────────

function CreditIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function PlusIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
    </svg>
  );
}
