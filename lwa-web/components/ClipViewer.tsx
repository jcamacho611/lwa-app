"use client";

import { useEffect, useRef, useCallback } from "react";
import { ClipResult } from "../lib/types";
import { isRenderedClip } from "../lib/clip-utils";

type ClipViewerProps = {
  clip: ClipResult;
  isOpen: boolean;
  onClose: () => void;
};

export function ClipViewer({ clip, isOpen, onClose }: ClipViewerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const hasVideo = isRenderedClip(clip);
  const videoUrl = clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url || null;

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === "Escape") onClose();
  }, [onClose]);

  useEffect(() => {
    if (!isOpen) return;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, handleKeyDown]);

  useEffect(() => {
    if (isOpen && videoRef.current) {
      videoRef.current.currentTime = 0;
      void videoRef.current.play().catch(() => {});
    } else if (!isOpen && videoRef.current) {
      videoRef.current.pause();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center"
      onClick={onClose}
    >
      {/* Glass backdrop */}
      <div className="absolute inset-0 bg-black/88 backdrop-blur-2xl" />

      {/* Viewer shell */}
      <div
        className="relative z-10 flex max-h-screen w-full max-w-sm flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close */}
        <button
          type="button"
          onClick={onClose}
          className="absolute -top-10 right-0 flex h-8 w-8 items-center justify-center rounded-full border border-white/15 bg-white/8 text-white/60 transition hover:bg-white/14 hover:text-white"
          aria-label="Close viewer"
        >
          ✕
        </button>

        {/* Video / poster */}
        <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-black shadow-[0_0_80px_rgba(245,200,66,0.12)]">
          {hasVideo && videoUrl ? (
            <video
              ref={videoRef}
              src={videoUrl}
              className="aspect-[9/16] w-full object-cover"
              playsInline
              loop
              muted={false}
              controls={false}
              onClick={(e) => {
                const v = e.currentTarget;
                v.paused ? void v.play() : v.pause();
              }}
            />
          ) : (
            <div className="flex aspect-[9/16] w-full flex-col items-center justify-center bg-[radial-gradient(circle_at_center,var(--surface-gold-glow),transparent_60%),linear-gradient(180deg,#0a0a0f_0%,#111118_100%)] p-8">
              <span className="mb-4 text-3xl">✦</span>
              <p className="text-center text-base font-semibold leading-7 text-[var(--gold)]">
                {clip.hook || clip.title}
              </p>
              <p className="mt-3 text-center text-xs text-white/40">Ideas-only — no rendered preview</p>
            </div>
          )}

          {/* Hook overlay at bottom of video */}
          {hasVideo ? (
            <div className="pointer-events-none absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent px-5 pb-5 pt-16">
              <p className="text-sm font-semibold leading-6 text-white drop-shadow">
                {clip.hook}
              </p>
            </div>
          ) : null}
        </div>

        {/* Meta strip */}
        <div className="mt-4 space-y-3 rounded-[22px] border border-white/8 bg-white/[0.04] p-4 backdrop-blur">
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1 text-[10px] font-bold tracking-widest text-[var(--gold)]">
              {clip.post_rank === 1 ? "POST FIRST" : clip.post_rank === 2 ? "POST SECOND" : clip.post_rank === 3 ? "TEST THIRD" : "MOVE LATER"}
            </span>
            {clip.packaging_angle ? (
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[10px] font-medium capitalize text-white/55">
                {clip.packaging_angle}
              </span>
            ) : null}
          </div>

          {clip.caption ? (
            <p className="text-xs leading-5 text-white/60">{clip.caption}</p>
          ) : null}

          {clip.cta_suggestion ? (
            <p className="text-[11px] text-[var(--gold)]/70">
              <span className="font-semibold text-[var(--gold)]/90">Move: </span>
              {clip.cta_suggestion}
            </p>
          ) : null}

          {/* Quick copy row */}
          <QuickCopyRow clip={clip} />
        </div>
      </div>
    </div>
  );
}

function QuickCopyRow({ clip }: { clip: ClipResult }) {
  function useCopy(text: string, label: string) {
    const copy = async () => {
      try {
        await navigator.clipboard.writeText(text);
      } catch {}
    };
    return { copy, label };
  }

  async function copyText(text: string) {
    try { await navigator.clipboard.writeText(text); } catch {}
  }

  return (
    <div className="flex flex-wrap gap-2 pt-1">
      {clip.hook ? (
        <button
          type="button"
          onClick={() => void copyText(clip.hook!)}
          className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1.5 text-[11px] font-semibold text-[var(--gold)] transition hover:bg-[var(--gold)] hover:text-black"
        >
          Copy hook
        </button>
      ) : null}
      {clip.caption ? (
        <button
          type="button"
          onClick={() => void copyText(clip.caption!)}
          className="rounded-full border border-white/15 bg-white/5 px-3 py-1.5 text-[11px] font-medium text-white/70 transition hover:border-white/25 hover:text-white"
        >
          Copy caption
        </button>
      ) : null}
    </div>
  );
}
