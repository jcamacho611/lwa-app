"use client";

/**
 * LWA analytics abstraction.
 * Uses PostHog if NEXT_PUBLIC_POSTHOG_KEY is configured and posthog-js is loaded.
 * Falls back to a no-op in all other cases — never throws.
 */

declare global {
  interface Window {
    posthog?: {
      capture: (event: string, properties?: Record<string, unknown>) => void;
      identify: (distinctId: string, properties?: Record<string, unknown>) => void;
      reset: () => void;
    };
  }
}

function safePosthog() {
  if (typeof window === "undefined") return null;
  return window.posthog ?? null;
}

export function track(event: string, properties?: Record<string, unknown>) {
  try {
    safePosthog()?.capture(event, properties);
  } catch {
    // never throw from analytics
  }
}

export function identify(userId: string, traits?: Record<string, unknown>) {
  try {
    safePosthog()?.identify(userId, traits);
  } catch {
    // never throw from analytics
  }
}

export function reset() {
  try {
    safePosthog()?.reset();
  } catch {
    // never throw from analytics
  }
}

// Typed event helpers — keeps call sites clean and prevents typos

export const Analytics = {
  clipGenerated(props: {
    request_id: string;
    platform?: string | null;
    source_type?: string | null;
    clip_count?: number;
    rendered_count?: number;
    strategy_only_count?: number;
    ai_provider?: string | null;
    is_guest: boolean;
  }) {
    track("clip_generated", props);
  },

  exportDownloaded(props: {
    request_id: string;
    format?: string | null;
    clip_count?: number;
    is_strategy_bundle?: boolean;
  }) {
    track("export_downloaded", props);
  },

  paywallHit(props: { source: string; platform?: string | null }) {
    track("paywall_hit", props);
  },

  liveStreamWarningShown(props: { url: string }) {
    track("live_stream_warning_shown", props);
  },

  liveStreamWarningBypassed(props: { url: string }) {
    track("live_stream_warning_bypassed", props);
  },

  opportunityInquiryClicked(props: { opportunity: string }) {
    track("opportunity_inquiry_clicked", props);
  },

  pathCardClicked(props: { path_id: string; path_title: string }) {
    track("path_card_clicked", props);
  },

  vaultOpened() {
    track("vault_opened");
  },

  clipExported(props: { clip_id: string; platform?: string | null }) {
    track("clip_exported", props);
  },
};
