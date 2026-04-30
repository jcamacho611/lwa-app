import type { CampaignStatus, EarningStatus, IntegrationStatus, SubmissionStatus } from "./types";

export function cn(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(" ");
}

export function formatMoney(amount?: number, currency = "USD") {
  if (typeof amount !== "number") return "-";

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "-";

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

export function statusLabel(status: CampaignStatus | SubmissionStatus | EarningStatus | IntegrationStatus | string) {
  return status
    .split("_")
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(" ");
}

export function statusTone(status: string) {
  if (
    [
      "active",
      "connected",
      "approved",
      "paid",
      "completed",
      "open",
      "recorded",
      "claimed",
      "resolved",
      "cleared",
      "succeeded",
    ].includes(status)
  ) {
    return "border-emerald-400/30 bg-emerald-400/10 text-emerald-700 dark:text-emerald-200";
  }

  if (
    [
      "pending_review",
      "under_review",
      "processing",
      "configured",
      "in_progress",
      "submitted",
      "payable",
      "mocked",
      "pending",
      "in_review",
      "queued",
      "running",
      "retrying",
      "waiting",
      "escalated",
      "information_requested",
    ].includes(status)
  ) {
    return "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--accent-wine)] dark:text-yellow-100";
  }

  if (["warning", "revision_requested", "held", "disputed", "draft", "flagged", "appealed"].includes(status)) {
    return "border-orange-400/30 bg-orange-400/10 text-orange-700 dark:text-orange-200";
  }

  if (
    ["error", "failed", "rejected", "cancelled", "expired", "refunded", "disabled", "not_configured", "blocked", "removed", "confirmed"].includes(
      status,
    )
  ) {
    return "border-red-400/30 bg-red-400/10 text-red-700 dark:text-red-200";
  }

  return "border-[var(--divider)] bg-[var(--surface-soft)] text-ink/70";
}
