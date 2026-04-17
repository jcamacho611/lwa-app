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
      <span className="relative inline-flex h-12 w-12 items-center justify-center overflow-hidden rounded-2xl border border-[rgba(217,181,109,0.2)] bg-[linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.015)),linear-gradient(180deg,rgba(21,17,12,0.96),rgba(7,6,5,0.98))] shadow-[0_0_0_1px_rgba(255,255,255,0.03)_inset,0_16px_44px_rgba(0,0,0,0.38)]">
        <span className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_34%_22%,rgba(245,224,179,0.28),transparent_34%),radial-gradient(circle_at_76%_72%,rgba(185,134,50,0.24),transparent_36%),radial-gradient(circle_at_62%_20%,rgba(122,22,44,0.16),transparent_36%)]" />
        <img src="/brand/lwa-mark.svg" alt="LWA omega mark" className="relative h-8 w-8" />
      </span>
      {compact ? null : (
        <span className="flex min-w-0 flex-col">
          <img src="/brand/lwa-wordmark.svg" alt="LWA" className="h-6 w-auto max-w-[170px]" />
          {showTagline ? (
            <span className="mt-0.5 text-[11px] uppercase tracking-[0.26em] text-muted">
              Ranked clips. Export faster.
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
