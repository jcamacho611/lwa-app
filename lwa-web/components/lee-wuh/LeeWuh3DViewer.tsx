"use client";

import LeeWuhCharacterStage from "./LeeWuhCharacterStage";

export default function LeeWuh3DViewer() {
  return (
    <div className="rounded-[32px] border border-[#C9A24A]/20 bg-black/30 p-3">
      <LeeWuhCharacterStage
        mood="idle"
        variant="hero"
        glbPath="/brand/lee-wuh/lee-wuh-mascot.glb"
        posterPath="/brand/lee-wuh/lee-wuh-transparent.png"
        title="Lee-Wuh GLB Viewer"
        message="Loads the optimized mascot GLB when available and falls back to the static Lee-Wuh image when the model is missing."
      />
    </div>
  );
}
