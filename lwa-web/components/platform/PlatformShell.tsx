"use client";

import { ReactNode } from "react";
import { LeeWuhWorldBackground } from "./LeeWuhWorldBackground";
import { PlatformNavigation } from "./navigation";

interface PlatformShellProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  showNavigation?: boolean;
  variant?: "default" | "dashboard" | "generate" | "game" | "marketplace";
}

/**
 * PlatformShell - Lee-Wuh Design System
 * 
 * Philosophy: World as atmosphere, not clutter
 * - Background sets mood without distraction
 * - Clean center for content
 * - Lee-Wuh presence at edges
 * - Premium, smooth, intense, non-crowded
 */
export function PlatformShell({
  children,
  title,
  subtitle,
  showNavigation = true,
  variant = "default",
}: PlatformShellProps) {
  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#0A0A0A]">
      {/* Layer 1: Lee-Wuh World Background (atmospheric) */}
      <LeeWuhWorldBackground variant={variant} />
      
      {/* Layer 2: Navigation (if enabled) */}
      {showNavigation && <PlatformNavigation />}
      
      {/* Layer 3: Main Content Area */}
      <main className="relative z-10 min-h-screen">
        {/* Header Section (if title provided) */}
        {(title || subtitle) && (
          <header className="px-6 pt-8 pb-4 lg:px-12 lg:pt-12">
            <div className="mx-auto max-w-7xl">
              {title && (
                <h1 className="text-3xl font-bold text-white lg:text-4xl">
                  {title}
                </h1>
              )}
              {subtitle && (
                <p className="mt-2 text-lg text-white/60">{subtitle}</p>
              )}
            </div>
          </header>
        )}
        
        {/* Content */}
        <div className="px-6 pb-24 lg:px-12">
          <div className="mx-auto max-w-7xl">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
