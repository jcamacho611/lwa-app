"use client";

type BackgroundWorkerMessage =
  | {
      type: "init";
      canvas: OffscreenCanvas;
      width: number;
      height: number;
      pixelRatio: number;
    }
  | {
      type: "resize";
      width: number;
      height: number;
      pixelRatio: number;
    }
  | {
      type: "visibility";
      hidden: boolean;
    }
  | {
      type: "destroy";
    };

function prefersReducedMotion() {
  return window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
}

function canUseWorkerCanvas(canvas: HTMLCanvasElement) {
  return (
    typeof window !== "undefined" &&
    typeof Worker !== "undefined" &&
    "transferControlToOffscreen" in canvas &&
    !prefersReducedMotion()
  );
}

function viewportPayload(type: "init" | "resize", canvas?: OffscreenCanvas): BackgroundWorkerMessage {
  const payload = {
    type,
    width: Math.max(window.innerWidth, 1),
    height: Math.max(window.innerHeight, 1),
    pixelRatio: Math.min(window.devicePixelRatio || 1, 1.5),
  };

  if (type === "init" && canvas) {
    return { ...payload, canvas };
  }

  return payload as BackgroundWorkerMessage;
}

export class LWABackground {
  private canvas: HTMLCanvasElement | null = null;
  private worker: Worker | null = null;
  private resizeFrame = 0;
  private initialized = false;

  init(canvas: HTMLCanvasElement) {
    this.canvas = canvas;

    if (!canUseWorkerCanvas(canvas)) {
      canvas.dataset.lwaBackgroundFallback = "css";
      return;
    }

    const offscreen = canvas.transferControlToOffscreen();
    this.worker = new Worker(new URL("./lwa-background-worker.ts", import.meta.url), {
      type: "module",
    });
    this.initialized = true;

    this.worker.postMessage(viewportPayload("init", offscreen), [offscreen]);
    window.addEventListener("resize", this.handleResize, { passive: true });
    document.addEventListener("visibilitychange", this.handleVisibility);
  }

  pause() {
    this.worker?.postMessage({ type: "visibility", hidden: true } satisfies BackgroundWorkerMessage);
  }

  resume() {
    this.worker?.postMessage({ type: "visibility", hidden: false } satisfies BackgroundWorkerMessage);
  }

  resize() {
    if (!this.initialized || !this.worker) return;
    this.worker.postMessage(viewportPayload("resize"));
  }

  destroy() {
    window.removeEventListener("resize", this.handleResize);
    document.removeEventListener("visibilitychange", this.handleVisibility);
    window.cancelAnimationFrame(this.resizeFrame);
    this.worker?.postMessage({ type: "destroy" } satisfies BackgroundWorkerMessage);
    this.worker?.terminate();
    this.worker = null;
    this.canvas = null;
    this.initialized = false;
  }

  private handleResize = () => {
    window.cancelAnimationFrame(this.resizeFrame);
    this.resizeFrame = window.requestAnimationFrame(() => this.resize());
  };

  private handleVisibility = () => {
    if (document.hidden) {
      this.pause();
      return;
    }
    this.resume();
  };
}
