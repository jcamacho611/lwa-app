'use client';

import { useState, type FormEvent } from 'react';

interface VideoInputProps {
  onSubmit: (url: string, platform: string) => void;
  isLoading: boolean;
}

const PLATFORMS = [
  { value: 'TikTok', label: 'TikTok' },
  { value: 'Instagram', label: 'Instagram Reels' },
  { value: 'YouTube', label: 'YouTube Shorts' },
  { value: 'Twitter', label: 'X / Twitter' },
  { value: 'LinkedIn', label: 'LinkedIn' },
];

const LOADING_MESSAGES = [
  'Analysing video…',
  'Extracting key moments…',
  'Generating hooks…',
  'Ranking clips…',
];

export function VideoInput({ onSubmit, isLoading }: VideoInputProps) {
  const [url, setUrl] = useState('');
  const [platform, setPlatform] = useState('TikTok');
  const [urlError, setUrlError] = useState('');
  const [loadingMsgIdx] = useState(0);

  function validateUrl(value: string): boolean {
    try {
      const parsed = new URL(value);
      return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    } catch {
      return false;
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) {
      setUrlError('Please enter a video URL.');
      return;
    }
    if (!validateUrl(trimmed)) {
      setUrlError('Please enter a valid URL starting with http:// or https://');
      return;
    }
    setUrlError('');
    onSubmit(trimmed, platform);
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="w-full space-y-5">
      {/* Header */}
      <div className="space-y-1">
        <h2 className="text-base font-semibold text-text-primary">
          Generate clips
        </h2>
        <p className="text-xs text-text-muted">
          Paste any public video URL to get started
        </p>
      </div>

      {/* URL field */}
      <div className="space-y-2">
        <label
          htmlFor="video-url"
          className="block text-xs font-semibold text-text-secondary uppercase tracking-wider"
        >
          Video URL
        </label>
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
            <LinkIcon className="h-4 w-4 text-text-muted" />
          </div>
          <input
            id="video-url"
            type="url"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              if (urlError) setUrlError('');
            }}
            placeholder="https://www.youtube.com/watch?v=..."
            disabled={isLoading}
            autoComplete="off"
            spellCheck={false}
            className={[
              'w-full rounded-xl border bg-surface-700/60 py-3.5 pl-11 pr-4 text-sm text-text-primary placeholder-text-muted',
              'transition-all duration-200 outline-none',
              'focus:ring-2 focus:ring-neon-purple/60 focus:border-neon-purple/50',
              urlError
                ? 'border-red-500/60 focus:ring-red-500/40'
                : 'border-white/10 hover:border-white/20',
              isLoading ? 'opacity-60 cursor-not-allowed' : '',
            ]
              .filter(Boolean)
              .join(' ')}
          />
        </div>
        {urlError && (
          <p className="text-xs text-red-400 flex items-center gap-1.5">
            <ExclamationIcon className="h-3.5 w-3.5 flex-shrink-0" />
            {urlError}
          </p>
        )}
      </div>

      {/* Platform selector */}
      <div className="space-y-2">
        <label
          htmlFor="platform"
          className="block text-xs font-semibold text-text-secondary uppercase tracking-wider"
        >
          Target Platform
        </label>
        <div className="relative">
          <select
            id="platform"
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            disabled={isLoading}
            className={[
              'w-full rounded-xl border border-white/10 bg-surface-700/60 py-3.5 px-4 text-sm text-text-primary',
              'transition-all duration-200 outline-none appearance-none cursor-pointer',
              'focus:ring-2 focus:ring-neon-purple/60 focus:border-neon-purple/50 hover:border-white/20',
              isLoading ? 'opacity-60 cursor-not-allowed' : '',
            ]
              .filter(Boolean)
              .join(' ')}
          >
            {PLATFORMS.map((p) => (
              <option key={p.value} value={p.value} className="bg-surface-800">
                {p.label}
              </option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
            <ChevronDownIcon className="h-4 w-4 text-text-muted" />
          </div>
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading}
        className={[
          'w-full rounded-xl py-4 px-6 text-sm font-bold text-white',
          'bg-gradient-neon-purple-blue',
          'transition-all duration-200 outline-none',
          'hover:shadow-neon-glow hover:scale-[1.01]',
          'focus:ring-2 focus:ring-neon-purple focus:ring-offset-2 focus:ring-offset-surface-800',
          'disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:shadow-none disabled:hover:scale-100',
          'active:scale-[0.99]',
          isLoading ? 'animate-glow-pulse' : '',
        ]
          .filter(Boolean)
          .join(' ')}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2.5">
            <SpinnerIcon className="h-4 w-4 animate-spin" />
            {LOADING_MESSAGES[loadingMsgIdx]}
          </span>
        ) : (
          <span className="flex items-center justify-center gap-2.5">
            <SparklesIcon className="h-4 w-4" />
            Generate Clips
          </span>
        )}
      </button>

      <p className="text-center text-xs text-text-muted">
        Supports YouTube, TikTok, Instagram, Twitter/X, and direct MP4 links
      </p>
    </form>
  );
}

// ─── Inline SVG icons ────────────────────────────────────────────────────────

function LinkIcon({ className }: { className?: string }) {
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
        d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244"
      />
    </svg>
  );
}

function ExclamationIcon({ className }: { className?: string }) {
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
        d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
      />
    </svg>
  );
}

function SpinnerIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24">
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  );
}

function SparklesIcon({ className }: { className?: string }) {
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
        d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
      />
    </svg>
  );
}

function ChevronDownIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
    </svg>
  );
}
