"use client";

import { LeeWuhMascot } from "./LeeWuhMascot";
import { LEE_WUH_BRAND } from "../../lib/brand/lee-wuh";

type LeeWuhEmptyStateProps = {
  title?: string;
  message?: string;
  action?: React.ReactNode;
  size?: "sm" | "md" | "lg";
  className?: string;
};

function cn(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(" ");
}

export function LeeWuhEmptyState({
  title = "No sources yet",
  message,
  action,
  size = "md",
  className,
}: LeeWuhEmptyStateProps) {
  const defaultMessage = LEE_WUH_BRAND.messages.empty.primary;
  const emptyMessage = message || defaultMessage;

  return (
    <div className={cn(
      "flex flex-col items-center justify-center py-16 px-6",
      className,
    )}>
      <LeeWuhMascot
        state="watching"
        size={size === "sm" ? "sm" : size === "lg" ? "lg" : "md"}
        showAura={true}
        className="mb-6"
      />
      
      <div className="text-center max-w-md">
        <h3 className="text-2xl font-bold text-white mb-2">
          {title}
        </h3>
        <p className="text-white/80 leading-relaxed mb-6">
          {emptyMessage}
        </p>
        
        {action && (
          <div className="mt-6">
            {action}
          </div>
        )}
      </div>
    </div>
  );
}
