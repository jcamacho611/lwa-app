"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import { getCharacterDirection, SPINE_LAYER_PLAN } from "../lib/character-art-direction";
import type { CharacterSide, CharacterState, GodName } from "../lib/character-controller";

type GodCharacterProps = {
  god: GodName;
  side: CharacterSide;
  state: CharacterState;
  speech?: string | null;
  asset?: string;
};

const GOD_LABELS: Record<GodName, string> = {
  zeus: "Zeus",
  athena: "Athena",
  hades: "Hades",
  anubis: "Anubis",
  celestial: "Oracle",
  hermes: "Hermes",
};

const DEFAULT_ASSETS: Record<GodName, string> = {
  zeus: "/brand-source/chars/zeus.png",
  athena: "/brand-source/chars/athena.png",
  hades: "/brand-source/chars/hades.png",
  anubis: "/brand-source/chars/anubis.png",
  celestial: "/brand-source/chars/celestial.png",
  hermes: "/brand-source/chars/hermes.png",
};

export function GodCharacter({ god, side, state, speech, asset }: GodCharacterProps) {
  const [streamedSpeech, setStreamedSpeech] = useState("");
  const speechRef = useRef(speech || "");
  const imageSrc = asset || DEFAULT_ASSETS[god];
  const label = GOD_LABELS[god];
  const direction = useMemo(() => getCharacterDirection(god), [god]);
  const glowTone = useMemo(() => (god === "hades" ? "crimson" : god === "anubis" || god === "athena" ? "blue" : "gold"), [god]);

  useEffect(() => {
    speechRef.current = speech || "";
    setStreamedSpeech("");
    if (!speech) return;

    let frame = 0;
    let last = 0;
    let index = 0;

    const tick = (time: number) => {
      if (time - last > 18) {
        index += 1;
        last = time;
        setStreamedSpeech(speechRef.current.slice(0, index));
      }
      if (index < speechRef.current.length) {
        frame = window.requestAnimationFrame(tick);
      }
    };

    frame = window.requestAnimationFrame(tick);
    return () => window.cancelAnimationFrame(frame);
  }, [speech]);

  return (
    <div
      className={[
        "god-character",
        side === "left" ? "god-left" : "god-right",
        `god-character-${state}`,
        `god-glow-${glowTone}`,
      ].join(" ")}
      aria-hidden="true"
      data-god={god}
      data-state={state}
      data-silhouette={direction.silhouette}
      data-emissive={direction.emissive}
      data-armor={direction.armor}
      data-aura={direction.aura}
      data-product-role={direction.productRole}
      data-layer-notes={direction.layerNotes}
      data-animation-notes={direction.animationNotes}
      data-performance-notes={direction.performanceNotes}
      data-spine-layers={SPINE_LAYER_PLAN.join(",")}
    >
      <div className="god-character-art">
        <span className="god-silhouette-frame" />
        <span className="god-character-shadow" />
        <img src={imageSrc} alt="" loading="eager" />
        <span className="god-emissive-core" />
        <span className="god-robe-vignette" />
        <span className="god-crown-line" />
        <span className="god-armor-trace" />
        <span className="god-eye-glow god-eye-glow-a" />
        <span className="god-eye-glow god-eye-glow-b" />
        <span className="god-character-aura" />
      </div>

      <AnimatePresence>
        {streamedSpeech ? (
          <motion.div
            className="god-speech"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.22 }}
          >
            <span>{label}</span>
            <p>{streamedSpeech}</p>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
