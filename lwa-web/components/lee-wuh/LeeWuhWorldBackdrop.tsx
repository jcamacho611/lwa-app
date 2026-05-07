"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { leeWuhVisualAssets } from "../../lib/lee-wuh-visual-assets";

type LeeWuhWorldBackdropProps = {
  children?: ReactNode;
  className?: string;
  overlay?: "light" | "medium" | "heavy";
  showAura?: boolean;
};

const overlayClasses = {
  light: "bg-black/55",
  medium: "bg-black/65",
  heavy: "bg-black/75",
};

function BackdropLayers({
  imageSrc,
  overlay,
  showAura,
  onImageError,
}: {
  imageSrc: string;
  overlay: "light" | "medium" | "heavy";
  showAura: boolean;
  onImageError: () => void;
}) {
  return (
    <>
      <img
        src={imageSrc}
        alt=""
        aria-hidden="true"
        className="absolute inset-0 h-full w-full object-cover object-center"
        onError={onImageError}
      />
      <div className={["absolute inset-0", overlayClasses[overlay]].join(" ")} />
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(0,0,0,0.9),rgba(0,0,0,0.32)_48%,rgba(0,0,0,0.78)),radial-gradient(circle_at_50%_16%,rgba(201,162,74,0.24),transparent_30%),radial-gradient(circle_at_55%_74%,rgba(126,58,242,0.24),transparent_38%)]" />
      <div className="absolute inset-x-0 bottom-0 h-[45vh] bg-gradient-to-t from-black via-black/75 to-transparent" />

      {showAura ? (
        <>
          <div className="absolute left-1/2 top-[-12%] h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-[#C9A24A]/10 blur-[120px]" />
          <div className="absolute right-[-12%] top-[20%] h-[620px] w-[620px] rounded-full bg-purple-700/20 blur-[130px]" />
          <div className="absolute bottom-[-20%] left-[-10%] h-[520px] w-[520px] rounded-full bg-[#C9A24A]/10 blur-[120px]" />
          <div className="absolute left-[8%] top-[18%] h-28 w-[1px] bg-gradient-to-b from-transparent via-[#C9A24A]/40 to-transparent" />
          <div className="absolute right-[18%] top-[10%] h-40 w-[1px] bg-gradient-to-b from-transparent via-purple-400/40 to-transparent" />
          <div className="absolute bottom-12 left-1/2 h-[1px] w-[80vw] -translate-x-1/2 bg-gradient-to-r from-transparent via-[#C9A24A]/25 to-transparent" />
        </>
      ) : null}
    </>
  );
}

export default function LeeWuhWorldBackdrop({
  children,
  className = "",
  overlay = "heavy",
  showAura = true,
}: LeeWuhWorldBackdropProps) {
  const [imageSrc, setImageSrc] = useState<string>(
    leeWuhVisualAssets.emptyWorldBackground.publicPath,
  );

  useEffect(() => {
    setImageSrc(leeWuhVisualAssets.emptyWorldBackground.publicPath);
  }, []);

  const handleImageError = () => {
    setImageSrc((currentSrc) =>
      currentSrc === leeWuhVisualAssets.fallbackHero.publicPath
        ? currentSrc
        : leeWuhVisualAssets.fallbackHero.publicPath,
    );
  };

  if (children) {
    return (
      <section
        className={[
          "relative isolate overflow-hidden bg-[#050506]",
          className,
        ].join(" ")}
      >
        <BackdropLayers
          imageSrc={imageSrc}
          overlay={overlay}
          showAura={showAura}
          onImageError={handleImageError}
        />
        <div className="relative z-10">{children}</div>
      </section>
    );
  }

  return (
    <div
      className={[
        "pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-[#050506]",
        className,
      ].join(" ")}
    >
      <BackdropLayers
        imageSrc={imageSrc}
        overlay={overlay}
        showAura={showAura}
        onImageError={handleImageError}
      />
    </div>
  );
}
