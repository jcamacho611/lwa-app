"use client";

import Link from "next/link";
import { useRef } from "react";
import { usePointerParallax } from "../../hooks/usePointerParallax";

type LogoProps = {
  href?: string;
  compact?: boolean;
  showTagline?: boolean;
  animated?: boolean;
  className?: string;
};

export function Logo({
  href = "/",
  compact = false,
  showTagline = false,
  animated = false,
  className = "",
}: LogoProps) {
  const logoRef = useRef<HTMLSpanElement>(null);
  usePointerParallax(logoRef, {
    rotate: animated ? 10 : 0,
    shiftSmall: animated ? 8 : 0,
    shiftMedium: animated ? 14 : 0,
    shiftLarge: animated ? 20 : 0,
  });

  const content = (
    <span className={["inline-flex items-center gap-3.5", className].join(" ")}>
      <span
        ref={logoRef}
        className={[
          "lwa-logo-shell relative inline-flex h-11 w-11 items-center justify-center overflow-hidden rounded-2xl border shadow-[0_0_0_1px_rgba(255,255,255,0.03)_inset,0_14px_40px_rgba(0,0,0,0.32)]",
          animated ? "lwa-logo-shell-animated" : "",
        ].join(" ")}
        style={{
          transform: animated
            ? "perspective(900px) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg)) translate3d(var(--px-sm, 0px), var(--py-sm, 0px), 0)"
            : undefined,
        }}
      >
        <span className="lwa-logo-halo absolute inset-0" />
        <span className="lwa-logo-shine absolute inset-0 overflow-hidden rounded-2xl" />
        <span className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_28%_24%,rgba(214,167,78,0.28),transparent_40%),radial-gradient(circle_at_78%_72%,rgba(255,240,191,0.12),transparent_36%),radial-gradient(circle_at_68%_26%,rgba(143,29,54,0.12),transparent_36%)]" />
        <img src="/brand/lwa-mark.svg" alt="LWA mark" className="relative h-8 w-8 drop-shadow-[0_0_14px_rgba(255,214,122,0.26)]" />
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
