"use client";

import { useEffect, useState } from "react";

type PollableClip = {
  id?: string | null;
  request_id?: string | null;
  preview_url?: string | null;
  edited_clip_url?: string | null;
  clip_url?: string | null;
  raw_clip_url?: string | null;
  render_status?: string | null;
};

function hasPlayablePreview(clip: PollableClip) {
  return Boolean(clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url);
}

export function useClipPreviewPolling<T extends PollableClip>(initialClip: T, maxAttempts = 24): T {
  const [clip, setClip] = useState(initialClip);

  useEffect(() => {
    setClip(initialClip);
  }, [
    initialClip.id,
    initialClip.request_id,
    initialClip.preview_url,
    initialClip.edited_clip_url,
    initialClip.clip_url,
    initialClip.raw_clip_url,
    initialClip.render_status,
  ]);

  useEffect(() => {
    if (!clip.id || hasPlayablePreview(clip) || clip.render_status === "failed") {
      return;
    }

    let attempts = 0;
    const query = clip.request_id ? `?request_id=${encodeURIComponent(clip.request_id)}` : "";
    const statusUrl = `/api/clip-status/${encodeURIComponent(clip.id)}${query}`;

    const interval = window.setInterval(async () => {
      attempts += 1;
      if (attempts > maxAttempts) {
        window.clearInterval(interval);
        return;
      }

      try {
        const response = await fetch(statusUrl, { cache: "no-store" });
        if (!response.ok) return;
        const updated = await response.json();

        if (updated?.preview_url || updated?.edited_clip_url || updated?.clip_url || updated?.raw_clip_url) {
          setClip((current) => ({ ...current, ...updated }));
          window.clearInterval(interval);
          return;
        }

        if (updated?.render_status === "failed") {
          setClip((current) => ({ ...current, ...updated }));
          window.clearInterval(interval);
        }
      } catch {
        // Network hiccups should not destabilize the preview card.
      }
    }, 2500);

    return () => window.clearInterval(interval);
  }, [
    clip.id,
    clip.request_id,
    clip.preview_url,
    clip.edited_clip_url,
    clip.clip_url,
    clip.raw_clip_url,
    clip.render_status,
    maxAttempts,
  ]);

  return clip;
}
