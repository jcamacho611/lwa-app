"use client";

import { useState } from "react";
import { leeWuhAssetFallback, leeWuhExpectedPublicPaths } from "../../lib/lee-wuh-assets";
import { LeeWuhAgentProvider } from "./LeeWuhAgentProvider";
import LeeWuhChatPanel from "./LeeWuhChatPanel";
import styles from "./LeeWuhLayeredStage.module.css";

function StageImage({
  src,
  fallback,
  alt,
  className,
}: {
  src: string;
  fallback: string;
  alt: string;
  className: string;
}) {
  const [activeSrc, setActiveSrc] = useState(src);
  const [isFallback, setIsFallback] = useState(false);

  return (
    <>
      <img
        src={activeSrc}
        alt={alt}
        className={className}
        onError={() => {
          if (activeSrc !== fallback) {
            setActiveSrc(fallback);
            setIsFallback(true);
          }
        }}
      />
      {isFallback ? (
        <span className="absolute left-4 top-4 z-20 rounded-full border border-[#C9A24A]/30 bg-black/75 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-[#E9C77B]">
          fallback image
        </span>
      ) : null}
    </>
  );
}

export default function LeeWuhLayeredStage() {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <LeeWuhAgentProvider surface="layered-stage">
      <section className={styles.stage} aria-label="Lee-Wuh layered living agent stage">
        <div className={styles.fallbackWorld} aria-hidden="true" />
        <StageImage
          src={leeWuhExpectedPublicPaths.background}
          fallback={leeWuhAssetFallback}
          alt="Lee-Wuh world background layer"
          className={styles.world}
        />
        <div className={styles.aura} aria-hidden="true" />
        <div className={styles.floorGlow} aria-hidden="true" />
        <StageImage
          src={leeWuhExpectedPublicPaths.character}
          fallback="/brand/lee-wuh/lee-wuh-transparent.png"
          alt="Lee-Wuh character transparent layer"
          className={styles.character}
        />
        <StageImage
          src={leeWuhExpectedPublicPaths.sword}
          fallback={leeWuhAssetFallback}
          alt="Lee-Wuh Realm Blade prop layer"
          className={styles.sword}
        />

        <div className="absolute inset-0 z-[5] bg-gradient-to-t from-black/75 via-transparent to-black/20" />

        <div className="absolute left-6 top-6 z-[6] max-w-xl">
          <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">
            Layered stage preview
          </p>
          <h2 className="mt-4 text-4xl font-black uppercase leading-none text-white sm:text-6xl">
            Lee-Wuh can move separately now.
          </h2>
          <p className="mt-4 max-w-lg text-sm leading-7 text-white/62">
            Background, character, sword, aura, and chat are independent layers.
            Missing production PNGs stay fallback-safe until generated assets land.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setChatOpen((value) => !value)}
          className={[
            styles.openButton,
            "rounded-full border border-[#C9A24A]/35 bg-[#C9A24A] px-5 py-3 text-sm font-black text-black shadow-[0_0_42px_rgba(126,58,242,0.45)] transition hover:scale-[1.03]",
          ].join(" ")}
        >
          {chatOpen ? "Hide Lee-Wuh chat" : "Open Lee-Wuh chat"}
        </button>

        {chatOpen ? (
          <LeeWuhChatPanel className={styles.chat} onClose={() => setChatOpen(false)} />
        ) : null}
      </section>
    </LeeWuhAgentProvider>
  );
}
