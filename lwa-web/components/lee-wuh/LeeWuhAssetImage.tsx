"use client";

import { useEffect, useState } from "react";
import { leeWuhAssetFallback } from "../../lib/lee-wuh-assets";

type LeeWuhAssetImageProps = {
  src: string;
  alt: string;
  className?: string;
};

export default function LeeWuhAssetImage({
  src,
  alt,
  className = "",
}: LeeWuhAssetImageProps) {
  const [activeSrc, setActiveSrc] = useState(src);
  const [isFallback, setIsFallback] = useState(false);

  useEffect(() => {
    setActiveSrc(src);
    setIsFallback(false);
  }, [src]);

  return (
    <div className="relative h-full w-full">
      <img
        src={activeSrc}
        alt={alt}
        className={className}
        onError={() => {
          if (activeSrc !== leeWuhAssetFallback) {
            setActiveSrc(leeWuhAssetFallback);
            setIsFallback(true);
          }
        }}
      />

      {isFallback ? (
        <div className="absolute left-3 top-3 rounded-full border border-[#C9A24A]/30 bg-black/75 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-[#E9C77B]">
          fallback
        </div>
      ) : null}
    </div>
  );
}
