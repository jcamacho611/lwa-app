"use client";

import type { ClipResult, PlatformOption } from "./types";

const FEEDBACK_KEY = "lwa-web-feedback-v1";
const IMPROVE_KEY = "lwa-web-improve-results";

export type ClipFeedbackVote = "good" | "bad";

export type ClipFeedbackRecord = {
  clipId: string;
  requestId?: string | null;
  vote: ClipFeedbackVote;
  hookStyle: string;
  packagingAngle: string;
  platform: PlatformOption;
  score: number;
  timestamp: string;
};

export type PreferenceProfile = {
  preferredAngles: string[];
  preferredHookStyles: string[];
  topPackagingAngle?: string;
  topHookStyle?: string;
};

function canUseStorage() {
  return typeof window !== "undefined";
}

function safeParse<T>(raw: string | null, fallback: T): T {
  if (!raw) {
    return fallback;
  }
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

export function readFeedbackRecords(): ClipFeedbackRecord[] {
  if (!canUseStorage()) {
    return [];
  }
  return safeParse<ClipFeedbackRecord[]>(window.localStorage.getItem(FEEDBACK_KEY), []);
}

export function writeFeedbackRecords(records: ClipFeedbackRecord[]) {
  if (!canUseStorage()) {
    return;
  }
  window.localStorage.setItem(FEEDBACK_KEY, JSON.stringify(records.slice(-120)));
}

export function readImproveResultsPreference() {
  if (!canUseStorage()) {
    return false;
  }
  return window.localStorage.getItem(IMPROVE_KEY) === "true";
}

export function writeImproveResultsPreference(value: boolean) {
  if (!canUseStorage()) {
    return;
  }
  window.localStorage.setItem(IMPROVE_KEY, value ? "true" : "false");
}

export function inferHookStyle(clip: ClipResult) {
  const source = `${clip.hook} ${(clip.hook_variants || []).join(" ")}`.toLowerCase();
  if (source.includes("?") || source.includes("why ") || source.includes("how ")) {
    return "curiosity";
  }
  if (source.includes("most ") || source.includes("wrong") || source.includes("nobody")) {
    return "contrarian";
  }
  if (source.includes("when ") || source.includes("moment") || source.includes("story")) {
    return "story";
  }
  if (source.includes("stop ") || source.includes("before ") || source.includes("exact")) {
    return "direct";
  }
  return "proof";
}

export function createFeedbackRecord(clip: ClipResult, vote: ClipFeedbackVote, platform: PlatformOption): ClipFeedbackRecord {
  return {
    clipId: clip.record_id || clip.clip_id || clip.id,
    requestId: clip.request_id || null,
    vote,
    hookStyle: inferHookStyle(clip),
    packagingAngle: clip.packaging_angle || "value",
    platform,
    score: clip.virality_score ?? clip.score ?? 0,
    timestamp: new Date().toISOString(),
  };
}

export function upsertFeedbackRecord(records: ClipFeedbackRecord[], next: ClipFeedbackRecord) {
  const filtered = records.filter((item) => item.clipId !== next.clipId);
  const updated = [...filtered, next];
  writeFeedbackRecords(updated);
  return updated;
}

export function buildPreferenceProfile(records: ClipFeedbackRecord[]): PreferenceProfile {
  const angleScores = new Map<string, number>();
  const hookScores = new Map<string, number>();

  for (const record of records) {
    const delta = record.vote === "good" ? 2 : -1;
    angleScores.set(record.packagingAngle, (angleScores.get(record.packagingAngle) || 0) + delta);
    hookScores.set(record.hookStyle, (hookScores.get(record.hookStyle) || 0) + delta);
  }

  const preferredAngles = [...angleScores.entries()]
    .sort((left, right) => right[1] - left[1])
    .filter(([, score]) => score > 0)
    .map(([angle]) => angle);

  const preferredHookStyles = [...hookScores.entries()]
    .sort((left, right) => right[1] - left[1])
    .filter(([, score]) => score > 0)
    .map(([style]) => style);

  return {
    preferredAngles,
    preferredHookStyles,
    topPackagingAngle: preferredAngles[0],
    topHookStyle: preferredHookStyles[0],
  };
}

export function applyPreferenceBoost(clips: ClipResult[], profile: PreferenceProfile, enabled: boolean) {
  if (!enabled || (!profile.preferredAngles.length && !profile.preferredHookStyles.length)) {
    return clips;
  }

  return [...clips].sort((left, right) => boostedScore(right, profile) - boostedScore(left, profile));
}

function boostedScore(clip: ClipResult, profile: PreferenceProfile) {
  let boost = clip.virality_score ?? clip.score ?? 0;
  if (clip.packaging_angle && profile.preferredAngles.includes(clip.packaging_angle)) {
    boost += 8;
  }
  if (profile.preferredHookStyles.includes(inferHookStyle(clip))) {
    boost += 5;
  }
  return boost;
}
