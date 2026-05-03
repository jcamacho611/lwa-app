"use client";

import { LeeWuhMascot } from "./LeeWuhMascot";
import { LEE_WUH_BRAND } from "../../lib/brand/lee-wuh";

type LeeWuhLoadingStateProps = {
  title?: string;
  message?: string;
  progress?: number;
  showProgress?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
};

function cn(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(" ");
}

export function LeeWuhLoadingState({
  title = "Lee-Wuh is working...",
  message,
  progress,
  showProgress = false,
  size = "md",
  className,
}: LeeWuhLoadingStateProps) {
  const defaultMessage = LEE_WUH_BRAND.messages.loading.primary;
  const loadingMessage = message || defaultMessage;

  return (
    <div className={cn(
      "flex flex-col items-center justify-center py-12 px-6",
      className,
    )}>
      <LeeWuhMascot
        state="thinking"
        size={size === "sm" ? "sm" : size === "lg" ? "lg" : "md"}
        showAura={true}
        className="mb-6"
      />
      
      <div className="text-center max-w-md">
        <h3 className="text-xl font-semibold text-white mb-2">
          {title}
        </h3>
        <p className="text-white/80 leading-relaxed mb-4">
          {loadingMessage}
        </p>
        
        {showProgress && typeof progress === 'number' && (
          <div className="w-full max-w-xs mx-auto">
            <div className="flex justify-between text-xs text-white/60 mb-2">
              <span>Processing</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
              <div 
                className="h-full w-full bg-gradient-to-r from-yellow-400 to-purple-500 rounded-full transition-all duration-500 ease-out motion-safe:animate-pulse"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
        
        {!showProgress && (
          <div className="mt-4 w-48 h-2 bg-white/10 rounded-full overflow-hidden mx-auto">
            <div className="h-full w-3/4 bg-gradient-to-r from-yellow-400 to-purple-500 rounded-full motion-safe:animate-pulse" />
          </div>
        )}
      </div>
    </div>
  );
}
