"use client";

import type { ClipResult } from "./types";

const QUEUE_KEY = "lwa-web-ready-queue-v1";

export type ReadyQueueItem = {
  clipId: string;
  requestId?: string | null;
  hook: string;
  caption: string;
  packagingAngle?: string | null;
  platformFit?: string | null;
  bestPostOrder?: number | null;
  viralityScore?: number | null;
  assetUrl?: string | null;
  targetPlatform: string;
  addedAt: string;
};

function canUseStorage() {
  return typeof window !== "undefined";
}

function readRaw(): ReadyQueueItem[] {
  if (!canUseStorage()) {
    return [];
  }
  try {
    return JSON.parse(window.localStorage.getItem(QUEUE_KEY) || "[]") as ReadyQueueItem[];
  } catch {
    return [];
  }
}

export function readReadyQueue() {
  return readRaw().sort((left, right) => (left.bestPostOrder || 999) - (right.bestPostOrder || 999));
}

export function writeReadyQueue(items: ReadyQueueItem[]) {
  if (!canUseStorage()) {
    return;
  }
  window.localStorage.setItem(QUEUE_KEY, JSON.stringify(items.slice(-40)));
}

export function createReadyQueueItem(clip: ClipResult, targetPlatform: string): ReadyQueueItem {
  return {
    clipId: clip.record_id || clip.clip_id || clip.id,
    requestId: clip.request_id || null,
    hook: clip.hook,
    caption: clip.caption,
    packagingAngle: clip.packaging_angle || null,
    platformFit: clip.platform_fit || null,
    bestPostOrder: clip.best_post_order || clip.rank || null,
    viralityScore: clip.virality_score ?? clip.score ?? null,
    assetUrl: clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url || null,
    targetPlatform,
    addedAt: new Date().toISOString(),
  };
}

export function upsertReadyQueueItem(items: ReadyQueueItem[], item: ReadyQueueItem) {
  const updated = [...items.filter((current) => current.clipId !== item.clipId), item];
  writeReadyQueue(updated);
  return readReadyQueue();
}

export function removeReadyQueueItem(items: ReadyQueueItem[], clipId: string) {
  const updated = items.filter((item) => item.clipId !== clipId);
  writeReadyQueue(updated);
  return readReadyQueue();
}

export function moveReadyQueueItem(items: ReadyQueueItem[], clipId: string, direction: -1 | 1) {
  const index = items.findIndex((item) => item.clipId === clipId);
  if (index < 0) {
    return items;
  }

  const targetIndex = index + direction;
  if (targetIndex < 0 || targetIndex >= items.length) {
    return items;
  }

  const updated = [...items];
  const [item] = updated.splice(index, 1);
  updated.splice(targetIndex, 0, item);
  writeReadyQueue(updated);
  return updated;
}

export function clearReadyQueue() {
  writeReadyQueue([]);
  return [];
}

export function buildReadyQueueExport(items: ReadyQueueItem[]) {
  return items
    .map((item, index) =>
      [
        `#${index + 1} ${item.hook}`,
        `Platform: ${item.targetPlatform}`,
        `Angle: ${item.packagingAngle || "value"}`,
        `Score: ${item.viralityScore ?? "N/A"}`,
        `Caption: ${item.caption}`,
        item.assetUrl ? `Asset: ${item.assetUrl}` : "",
      ]
        .filter(Boolean)
        .join("\n"),
    )
    .join("\n\n");
}
