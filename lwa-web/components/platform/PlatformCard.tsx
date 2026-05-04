"use client";

import { ReactNode } from "react";

interface PlatformCardProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  variant?: "default" | "highlight" | "gold" | "purple";
  className?: string;
  action?: ReactNode;
}

/**
 * PlatformCard - Lee-Wuh Design System Card
 * 
 * Premium card component with:
 * - Clean, non-crowded layout
 * - Gold/purple accent variants
 * - Smooth animations
 * - Glassmorphism effect
 */
export function PlatformCard({
  children,
  title,
  subtitle,
  variant = "default",
  className = "",
  action,
}: PlatformCardProps) {
  const variantStyles = {
    default: "border-white/10 bg-[#1A1A1A]/80",
    highlight: "border-[#C9A24A]/30 bg-gradient-to-br from-[#1A1A1A] to-[#0A0A0A]",
    gold: "border-[#C9A24A]/50 bg-gradient-to-br from-[#C9A24A]/10 to-[#1A1A1A]",
    purple: "border-[#9333EA]/50 bg-gradient-to-br from-[#9333EA]/10 to-[#1A1A1A]",
  };

  return (
    <div
      className={`
        rounded-2xl border backdrop-blur-xl p-6 transition-all duration-300
        hover:border-white/20 hover:shadow-lg hover:shadow-[#C9A24A]/5
        ${variantStyles[variant]}
        ${className}
      `}
    >
      {/* Card Header */}
      {(title || subtitle || action) && (
        <div className="mb-4 flex items-start justify-between">
          <div>
            {title && (
              <h3 className="text-lg font-semibold text-white">{title}</h3>
            )}
            {subtitle && (
              <p className="mt-1 text-sm text-white/50">{subtitle}</p>
            )}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      
      {/* Card Content */}
      {children}
    </div>
  );
}
