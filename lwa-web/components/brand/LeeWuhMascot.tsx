"use client";

import Image from "next/image";
import { LEE_WUH_BRAND, type LeeWuhSize, type LeeWuhState } from "../../lib/brand/lee-wuh";

type LeeWuhMascotProps = {
  state?: LeeWuhState;
  size?: LeeWuhSize;
  variant?: "bust" | "full" | "sticker" | "watermark";
  showAura?: boolean;
  showLabel?: boolean;
  className?: string;
  useHeroAsset?: boolean;
};

const sizeClass: Record<LeeWuhSize, string> = {
  sm: "w-16",
  md: "w-28", 
  lg: "w-44",
  hero: "w-72 md:w-96",
};

function cn(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(" ");
}

export function LeeWuhMascot({
  state = "idle",
  size = "md",
  variant = "full",
  showAura = true,
  showLabel = false,
  className,
  useHeroAsset = false,
}: LeeWuhMascotProps) {
  const isWatermark = variant === "watermark";

  return (
    <div
      className={cn(
        "relative inline-flex flex-col items-center justify-center",
        isWatermark && "opacity-20 grayscale",
        className,
      )}
    >
      {showAura && !isWatermark && (
        <div
          aria-hidden="true"
          className="absolute inset-0 -z-10 rounded-full bg-purple-500/20 blur-3xl motion-safe:animate-pulse"
        />
      )}

      <div className="relative">
        <Image
          src={useHeroAsset ? LEE_WUH_BRAND.heroAssetPath : LEE_WUH_BRAND.assetPath}
          alt="Lee-Wuh, the LWA mascot"
          width={useHeroAsset ? 1280 : 720}
          height={useHeroAsset ? 720 : 720}
          className={cn(
            sizeClass[size],
            "select-none object-contain drop-shadow-[0_0_28px_rgba(139,61,255,0.35)]",
            useHeroAsset && "rounded-lg",
          )}
          priority={size === "hero" || useHeroAsset}
        />

        {state === "success" || state === "overlord" ? (
          <div className="absolute -right-2 top-2 rounded-full border border-yellow-300/40 bg-black/70 px-2 py-1 text-[10px] uppercase tracking-[0.2em] text-yellow-200">
            Overlord
          </div>
        ) : null}
      </div>

      {showLabel && !isWatermark && (
        <div className="mt-2 text-center">
          <div className="font-mono text-xs uppercase tracking-[0.2em] text-yellow-400">
            {LEE_WUH_BRAND.mascotName}
          </div>
          <div className="text-[10px] text-gray-400">
            {LEE_WUH_BRAND.role}
          </div>
        </div>
      )}
    </div>
  );
}
