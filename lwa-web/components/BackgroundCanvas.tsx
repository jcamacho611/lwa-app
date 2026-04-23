"use client";

import { useEffect, useRef } from "react";

export function BackgroundCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    let background: import("../lib/background-scene").LWABackground | null = null;
    let cancelled = false;

    async function boot() {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const { LWABackground } = await import("../lib/background-scene");
      if (cancelled) return;

      background = new LWABackground();
      background.init(canvas);
    }

    void boot();

    return () => {
      cancelled = true;
      background?.destroy();
    };
  }, []);

  return (
    <canvas
      id="lwa-bg"
      ref={canvasRef}
      className="lwa-bg-canvas"
      aria-hidden="true"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        zIndex: 0,
        pointerEvents: "none",
      }}
    />
  );
}
