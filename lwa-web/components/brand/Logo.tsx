"use client";

import Link from "next/link";

type LogoProps = {
  href?: string;
  compact?: boolean;
  showTagline?: boolean;
  className?: string;
  animated?: boolean;
};

export function Logo({
  href = "/",
  compact = false,
  showTagline = false,
  className = "",
  animated = false,
}: LogoProps) {
  const content = (
    <span className={["inline-flex items-center gap-3.5", className].join(" ")}>
      <span className={["logo-mark-shell", animated ? "logo-mark-shell-animated" : ""].join(" ")}>
        <span className="logo-mark-aura" />
        <span className="logo-mark-ring" />
        <span className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_34%_22%,rgba(255,107,139,0.28),transparent_34%),radial-gradient(circle_at_76%_72%,rgba(255,0,60,0.2),transparent_36%),radial-gradient(circle_at_62%_20%,rgba(0,231,255,0.12),transparent_36%)]" />
        <img src="/brand/lwa-mark.svg" alt="LWA omega mark" className="relative h-8 w-8" />
      </span>
      {compact ? null : (
        <span className="flex min-w-0 flex-col">
          <img
            src="/brand/lwa-wordmark.svg"
            alt="LWA"
            className={["h-6 w-auto max-w-[170px]", animated ? "logo-wordmark-glow" : ""].join(" ")}
          />
          {showTagline ? (
            <span className="mt-0.5 text-[11px] uppercase tracking-[0.26em] text-muted">
              Clips worth posting.
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
