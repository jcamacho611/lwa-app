'use client';

import { useState } from 'react';
import type { ClipResult } from '@/lib/types';

interface ClipCardProps {
  clip: ClipResult;
  index: number;
  featured?: boolean;
}

export function ClipCard({ clip, index, featured = false }: ClipCardProps) {
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [expandedHooks, setExpandedHooks] = useState(false);

  async function copyToClipboard(text: string, field: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    } catch {
      // Fallback for older browsers / non-HTTPS
      const el = document.createElement('textarea');
      el.value = text;
      el.style.position = 'fixed';
      el.style.opacity = '0';
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    }
  }

  const scoreColor =
    clip.score >= 80
      ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/25'
      : clip.score >= 60
        ? 'text-amber-400 bg-amber-400/10 border-amber-400/25'
        : 'text-text-secondary bg-white/5 border-white/10';

  const cardBorder = featured
    ? 'border-neon-purple/35 shadow-card-premium neon-glow'
    : 'border-white/8';

  return (
    <article
      className={`animate-slide-up rounded-2xl border ${cardBorder} bg-surface-800/50 backdrop-blur-sm overflow-hidden transition-all duration-200 hover:border-neon-purple/20 hover:shadow-card-hover`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4 px-5 pt-5 pb-4 border-b border-white/6">
        <div className="flex items-center gap-3 min-w-0">
          <span
            className={`flex-shrink-0 flex h-8 w-8 items-center justify-center rounded-lg text-sm font-bold ${
              featured
                ? 'bg-gradient-neon-purple-blue text-white'
                : 'bg-surface-700/80 text-text-secondary'
            }`}
          >
            {index + 1}
          </span>
          <h3 className="text-sm font-semibold text-text-primary truncate">
            {clip.title}
          </h3>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {clip.format && (
            <span className="rounded-md border border-white/10 bg-white/5 px-2 py-0.5 text-xs text-text-secondary">
              {clip.format}
            </span>
          )}
          <span
            className={`rounded-md border px-2 py-0.5 text-xs font-bold ${scoreColor}`}
          >
            {clip.score}/100
          </span>
        </div>
      </div>

      <div className="px-5 py-4 space-y-4">
        {/* Timestamps */}
        <div className="flex items-center gap-3 text-xs text-text-muted">
          <ClockIcon className="h-3.5 w-3.5 flex-shrink-0" />
          <span className="font-mono">
            {clip.start_time} → {clip.end_time}
          </span>
          {clip.platform_fit && (
            <>
              <span className="text-white/10">·</span>
              <span className="text-text-secondary">{clip.platform_fit}</span>
            </>
          )}
        </div>

        {/* Hook */}
        <CopyField
          label="Hook"
          value={clip.hook}
          fieldKey="hook"
          copiedField={copiedField}
          onCopy={copyToClipboard}
          accent="purple"
        />

        {/* Caption */}
        <CopyField
          label="Caption"
          value={clip.caption}
          fieldKey="caption"
          copiedField={copiedField}
          onCopy={copyToClipboard}
          accent="violet"
        />

        {/* Why this matters */}
        {clip.why_this_matters && (
          <div className="rounded-xl border border-white/6 bg-surface-700/40 px-4 py-3 space-y-1">
            <p className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              Why it works
            </p>
            <p className="text-sm text-text-secondary leading-relaxed">
              {clip.why_this_matters}
            </p>
          </div>
        )}

        {/* CTA suggestion */}
        {clip.cta_suggestion && (
          <CopyField
            label="CTA"
            value={clip.cta_suggestion}
            fieldKey="cta"
            copiedField={copiedField}
            onCopy={copyToClipboard}
            accent="cyan"
          />
        )}

        {/* Thumbnail text */}
        {clip.thumbnail_text && (
          <CopyField
            label="Thumbnail Text"
            value={clip.thumbnail_text}
            fieldKey="thumbnail"
            copiedField={copiedField}
            onCopy={copyToClipboard}
            accent="amber"
          />
        )}

        {/* Hook variants */}
        {clip.hook_variants && clip.hook_variants.length > 0 && (
          <div className="space-y-2">
            <button
              onClick={() => setExpandedHooks((v) => !v)}
              className="flex items-center gap-1.5 text-xs font-semibold text-text-muted hover:text-text-secondary transition-colors"
            >
              <ChevronIcon
                className={`h-3.5 w-3.5 transition-transform ${expandedHooks ? 'rotate-180' : ''}`}
              />
              {expandedHooks ? 'Hide' : 'Show'} {clip.hook_variants.length} hook
              variant{clip.hook_variants.length !== 1 ? 's' : ''}
            </button>
            {expandedHooks && (
              <div className="space-y-2 pl-1">
                {clip.hook_variants.map((variant, i) => (
                  <CopyField
                    key={i}
                    label={`Variant ${i + 1}`}
                    value={variant}
                    fieldKey={`variant-${i}`}
                    copiedField={copiedField}
                    onCopy={copyToClipboard}
                    accent="slate"
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Transcript excerpt */}
        {clip.transcript_excerpt && (
          <details className="group">
            <summary className="cursor-pointer text-xs font-semibold text-text-muted hover:text-text-secondary transition-colors list-none flex items-center gap-1.5">
              <ChevronIcon className="h-3.5 w-3.5 transition-transform group-open:rotate-180" />
              Transcript excerpt
            </summary>
            <blockquote className="mt-2 rounded-xl border border-white/6 bg-surface-700/40 px-4 py-3 text-xs text-text-secondary italic leading-relaxed">
              &ldquo;{clip.transcript_excerpt}&rdquo;
            </blockquote>
          </details>
        )}

        {/* Clip download links */}
        {(clip.clip_url || clip.edited_clip_url || clip.raw_clip_url) && (
          <div className="flex flex-wrap gap-2 pt-1">
            {clip.edited_clip_url && (
              <a
                href={clip.edited_clip_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg border border-neon-purple/30 bg-neon-purple/10 px-3 py-1.5 text-xs font-semibold text-neon-violet hover:bg-neon-purple/20 transition-colors"
              >
                <DownloadIcon className="h-3.5 w-3.5" />
                Edited Clip
              </a>
            )}
            {clip.clip_url && !clip.edited_clip_url && (
              <a
                href={clip.clip_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg border border-neon-purple/30 bg-neon-purple/10 px-3 py-1.5 text-xs font-semibold text-neon-violet hover:bg-neon-purple/20 transition-colors"
              >
                <DownloadIcon className="h-3.5 w-3.5" />
                Download Clip
              </a>
            )}
            {clip.raw_clip_url && (
              <a
                href={clip.raw_clip_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-text-secondary hover:bg-white/10 transition-colors"
              >
                <DownloadIcon className="h-3.5 w-3.5" />
                Raw Clip
              </a>
            )}
          </div>
        )}
      </div>
    </article>
  );
}

// ─── CopyField ───────────────────────────────────────────────────────────────

type AccentColor = 'purple' | 'violet' | 'cyan' | 'amber' | 'slate';

const ACCENT_CLASSES: Record<
  AccentColor,
  { label: string; button: string; border: string; bg: string }
> = {
  purple:  { label: 'text-neon-violet',    button: 'hover:text-neon-purple',   border: 'border-neon-purple/20',  bg: 'bg-neon-purple/5' },
  violet:  { label: 'text-violet-400',     button: 'hover:text-violet-300',    border: 'border-violet-500/20',   bg: 'bg-violet-500/5' },
  cyan:    { label: 'text-neon-cyan',      button: 'hover:text-neon-cyan',     border: 'border-neon-cyan/20',    bg: 'bg-neon-cyan/5' },
  amber:   { label: 'text-amber-400',      button: 'hover:text-amber-300',     border: 'border-amber-500/20',    bg: 'bg-amber-500/5' },
  slate:   { label: 'text-text-secondary', button: 'hover:text-text-primary',  border: 'border-white/8',         bg: 'bg-white/5' },
};

interface CopyFieldProps {
  label: string;
  value: string;
  fieldKey: string;
  copiedField: string | null;
  onCopy: (text: string, field: string) => void;
  accent: AccentColor;
}

function CopyField({
  label,
  value,
  fieldKey,
  copiedField,
  onCopy,
  accent,
}: CopyFieldProps) {
  const isCopied = copiedField === fieldKey;
  const colors = ACCENT_CLASSES[accent];

  return (
    <div
      className={`rounded-xl border ${colors.border} ${colors.bg} px-4 py-3 space-y-1.5`}
    >
      <div className="flex items-center justify-between gap-2">
        <span
          className={`text-xs font-bold uppercase tracking-wider ${colors.label}`}
        >
          {label}
        </span>
        <button
          onClick={() => onCopy(value, fieldKey)}
          className={`flex items-center gap-1 text-xs text-text-muted ${colors.button} transition-colors`}
          title={`Copy ${label}`}
        >
          {isCopied ? (
            <>
              <CheckIcon className="h-3.5 w-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-semibold">Copied!</span>
            </>
          ) : (
            <>
              <CopyIcon className="h-3.5 w-3.5" />
              Copy
            </>
          )}
        </button>
      </div>
      <p className="text-sm text-text-primary leading-relaxed whitespace-pre-wrap">
        {value}
      </p>
    </div>
  );
}

// ─── Icons ───────────────────────────────────────────────────────────────────

function ClockIcon({ className }: { className?: string }) {
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
        d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  );
}

function CopyIcon({ className }: { className?: string }) {
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
        d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 01-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 011.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 00-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 01-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 00-3.375-3.375h-1.5a1.125 1.125 0 01-1.125-1.125v-1.5a3.375 3.375 0 00-3.375-3.375H9.75"
      />
    </svg>
  );
}

function CheckIcon({ className }: { className?: string }) {
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
        d="M4.5 12.75l6 6 9-13.5"
      />
    </svg>
  );
}

function ChevronIcon({ className }: { className?: string }) {
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
        d="M19.5 8.25l-7.5 7.5-7.5-7.5"
      />
    </svg>
  );
}

function DownloadIcon({ className }: { className?: string }) {
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
        d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
      />
    </svg>
  );
}
