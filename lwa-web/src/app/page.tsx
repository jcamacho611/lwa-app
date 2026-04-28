'use client';

import { useClipGeneration } from '@/hooks/useClipGeneration';
import { VideoInput } from '@/components/VideoInput';
import { ResultsDisplay } from '@/components/ResultsDisplay';

export default function HomePage() {
  const { state, generate, reset } = useClipGeneration();

  function handleSubmit(url: string, platform: string) {
    generate({ video_url: url, target_platform: platform });
  }

  return (
    <div className="min-h-dvh flex flex-col">
      {/* ── Nav ─────────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-white/6 bg-surface-900/80 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
          <div className="flex items-center gap-2.5">
            <LogoMark />
            <span className="text-sm font-bold tracking-tight text-white">LWA</span>
            <span className="hidden sm:inline-block rounded-full border border-brand-500/30 bg-brand-500/10 px-2 py-0.5 text-xs font-medium text-brand-400">
              AI Clip Generator
            </span>
          </div>
          <nav className="flex items-center gap-1">
            <a
              href="https://lwa-production-c9cc.up.railway.app/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg px-3 py-1.5 text-xs font-medium text-slate-400 hover:bg-white/5 hover:text-white transition-colors"
            >
              API Docs
            </a>
          </nav>
        </div>
      </header>

      {/* ── Main ────────────────────────────────────────────────────────── */}
      <main className="flex-1 mx-auto w-full max-w-5xl px-4 sm:px-6 py-10 sm:py-16">
        {state.status === 'success' && state.data ? (
          /* ── Results view ─────────────────────────────────────────────── */
          <ResultsDisplay data={state.data} onReset={reset} />
        ) : (
          /* ── Input view ───────────────────────────────────────────────── */
          <div className="flex flex-col items-center">
            {/* Hero */}
            <div className="mb-10 text-center space-y-4 max-w-2xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/10 px-4 py-1.5 text-xs font-medium text-brand-400">
                <SparklesIcon className="h-3.5 w-3.5" />
                Powered by AI
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-white text-balance">
                Turn public source material into{' '}
                <span className="bg-gradient-to-r from-brand-400 to-violet-400 bg-clip-text text-transparent">
                  ranked clip packages
                </span>
              </h1>
              <p className="text-base sm:text-lg text-slate-400 text-balance leading-relaxed">
                Paste a public video URL and get hooks, captions, timestamps, and post order
                prepared for TikTok, Reels, Shorts, and more.
              </p>
            </div>

            {/* Input card */}
            <div className="w-full max-w-xl">
              <div className="rounded-2xl border border-white/8 bg-surface-800 p-6 sm:p-8 glow-brand">
                <VideoInput
                  onSubmit={handleSubmit}
                  isLoading={state.status === 'loading'}
                />
              </div>

              {/* Error state */}
              {state.status === 'error' && state.error && (
                <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 flex items-start gap-3 animate-fade-in">
                  <AlertIcon className="h-4 w-4 text-red-400 flex-shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-red-300">Generation failed</p>
                    <p className="text-xs text-red-400/80">{state.error}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Feature grid */}
            <div className="mt-16 w-full grid grid-cols-1 sm:grid-cols-3 gap-4">
              {FEATURES.map((f) => (
                <FeatureCard key={f.title} {...f} />
              ))}
            </div>

            {/* Platform logos row */}
            <div className="mt-12 text-center space-y-3">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                Optimised for
              </p>
              <div className="flex flex-wrap items-center justify-center gap-3">
                {PLATFORMS.map((p) => (
                  <span
                    key={p}
                    className="rounded-full border border-white/8 bg-white/4 px-3 py-1 text-xs text-slate-400"
                  >
                    {p}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <footer className="border-t border-white/6 py-6">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <span>© {new Date().getFullYear()} LWA. All rights reserved.</span>
          <a
            href="https://lwa-production-c9cc.up.railway.app/health"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-slate-300 transition-colors"
          >
            API Status
          </a>
        </div>
      </footer>
    </div>
  );
}

// ─── Static data ─────────────────────────────────────────────────────────────

const PLATFORMS = ['TikTok', 'Instagram Reels', 'YouTube Shorts', 'X / Twitter', 'LinkedIn'];

const FEATURES = [
  {
    icon: <BoltIcon className="h-5 w-5" />,
    title: 'Instant analysis',
    description: 'Hooks, captions, and timestamps generated in under a minute from any public video URL.',
  },
  {
    icon: <TargetIcon className="h-5 w-5" />,
    title: 'Platform-native copy',
    description: 'Each clip is scored and formatted for the platform you choose — not generic output.',
  },
  {
    icon: <LayersIcon className="h-5 w-5" />,
    title: 'Hook variants',
    description: 'Multiple hook angles per clip so you can A/B test without writing a single word.',
  },
];

// ─── Sub-components ───────────────────────────────────────────────────────────

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-white/6 bg-surface-800/60 p-5 space-y-3">
      <div className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-brand-600/20 text-brand-400">
        {icon}
      </div>
      <div className="space-y-1">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
        <p className="text-xs text-slate-400 leading-relaxed">{description}</p>
      </div>
    </div>
  );
}

// ─── Icons ───────────────────────────────────────────────────────────────────

function LogoMark() {
  return (
    <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-violet-600">
      <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
      </svg>
    </div>
  );
}

function SparklesIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
    </svg>
  );
}

function AlertIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
    </svg>
  );
}

function BoltIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
    </svg>
  );
}

function TargetIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
    </svg>
  );
}

function LayersIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.429 9.75L2.25 12l4.179 2.25m0-4.5l5.571 3 5.571-3m-11.142 0L2.25 7.5 12 2.25l9.75 5.25-4.179 2.25m0 0L21.75 12l-4.179 2.25m0 0l4.179 2.25L12 21.75 2.25 16.5l4.179-2.25m11.142 0l-5.571 3-5.571-3" />
    </svg>
  );
}
