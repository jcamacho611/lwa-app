"use client";

import Link from "next/link";

type LogoProps = {
  href?: string;
  compact?: boolean;
  showTagline?: boolean;
  className?: string;
};

export function Logo({ href = "/", compact = false, showTagline = false, className = "" }: LogoProps) {
  const content = (
    <span className={["inline-flex items-center gap-3.5", className].join(" ")}>
      <span className="relative inline-flex h-11 w-11 items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-white/[0.035] shadow-[0_0_0_1px_rgba(255,255,255,0.03)_inset,0_14px_40px_rgba(0,0,0,0.32)]">
        <span className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(168,85,247,0.42),transparent_36%),radial-gradient(circle_at_74%_72%,rgba(34,211,238,0.24),transparent_34%),radial-gradient(circle_at_65%_25%,rgba(143,29,54,0.16),transparent_34%)]" />
        <img src="/brand/lwa-mark.svg" alt="LWA mark" className="relative h-8 w-8" />
      </span>
      {compact ? null : (
        <span className="flex min-w-0 flex-col">
          <img src="/brand/lwa-wordmark.svg" alt="LWA" className="h-6 w-auto max-w-[170px]" />
          {showTagline ? (
            <span className="mt-0.5 text-[11px] uppercase tracking-[0.26em] text-muted">
              Ranked clips. Ready fast.
            </span>
          ) : null}
        </span>
      )}
    </span>
  );

  return (
    <Link href={href} className="inline-flex items-center">
      {content}
    </Link>
  );
}
