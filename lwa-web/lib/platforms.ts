import type { PlatformCode } from "./types";

export const platforms: { label: string; value: PlatformCode; short: string }[] = [
  { label: "TikTok", value: "TikTok", short: "TikTok" },
  { label: "Reels", value: "Instagram", short: "Reels" },
  { label: "Shorts", value: "YouTube", short: "Shorts" },
];
