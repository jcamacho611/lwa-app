"use client";

import { LEE_WUH_BRAND, getLeeWuhTip, type LeeWuhTone } from "../../lib/brand/lee-wuh";

type LeeWuhTipProps = {
  message?: string;
  tone?: LeeWuhTone;
  size?: "sm" | "md" | "lg";
  showMascot?: boolean;
  className?: string;
};

const toneStyles = {
  default: "bg-[#16161B] border-[#23232C] text-[#B8B3A7]",
  success: "bg-[#0A2E0A] border-[#16A34A] text-[#86EFAC]",
  warning: "bg-[#2A1F0A] border-[#F59E0B] text-[#FDE68A]",
  danger: "bg-[#2A0A0A] border-[#EF4444] text-[#FCA5A5]",
  premium: "bg-[#1A1407] border-[#C9A24A] text-[#E9C77B]",
};

const sizeStyles = {
  sm: "px-3 py-2 text-xs",
  md: "px-4 py-3 text-sm", 
  lg: "px-5 py-4 text-base",
};

function cn(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(" ");
}

export function LeeWuhTip({
  message,
  tone = "default",
  size = "md",
  showMascot = true,
  className,
}: LeeWuhTipProps) {
  const tipMessage = message || getLeeWuhTip();

  return (
    <div
      className={cn(
        "inline-flex items-start gap-3 rounded-lg border",
        toneStyles[tone],
        sizeStyles[size],
        className,
      )}
    >
      {showMascot && (
        <div className="flex-shrink-0">
          <div className="w-6 h-6 rounded-full bg-gradient-to-br from-yellow-400 to-purple-500 flex items-center justify-center">
            <span className="text-[10px] font-bold text-black">W</span>
          </div>
        </div>
      )}
      
      <div className="flex-1">
        <p className="leading-relaxed">{tipMessage}</p>
        {tone === "premium" && (
          <p className="mt-1 text-xs opacity-75">— {LEE_WUH_BRAND.mascotName}</p>
        )}
      </div>
    </div>
  );
}
