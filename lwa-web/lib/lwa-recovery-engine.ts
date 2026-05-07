import type { ClipResult } from "./types";

export type LwaRecoveryIssueType =
  | "render_failed"
  | "strategy_only"
  | "missing_preview"
  | "provider_unavailable"
  | "export_failed"
  | "asset_missing"
  | "invalid_source"
  | "unknown_error";

export type LwaRecoveryActionType =
  | "retry_render"
  | "export_strategy"
  | "use_fallback_provider"
  | "save_as_proof_idea"
  | "open_support_context"
  | "downgrade_quality"
  | "copy_package_only"
  | "reset_run";

export type LwaRecoverySeverity = "low" | "medium" | "high";

export type LwaRecoveryDecision = {
  issueType: LwaRecoveryIssueType;
  severity: LwaRecoverySeverity;
  userMessage: string;
  technicalReason: string;
  recommendedActions: LwaRecoveryActionType[];
  primaryAction: LwaRecoveryActionType;
  canContinue: boolean;
  shouldBlockExport: boolean;
  leeWuhLine: string;
};

type RecoveryDecisionBlueprint = Omit<LwaRecoveryDecision, "issueType">;

const recoveryBlueprints: Record<LwaRecoveryIssueType, RecoveryDecisionBlueprint> = {
  render_failed: {
    severity: "high",
    userMessage: "Render failed, but the strategy package is still useful.",
    technicalReason: "The clip render path returned an error or failed status.",
    recommendedActions: ["retry_render", "export_strategy", "use_fallback_provider"],
    primaryAction: "retry_render",
    canContinue: true,
    shouldBlockExport: true,
    leeWuhLine: "The render cut failed. Keep the strategy and try again.",
  },
  strategy_only: {
    severity: "medium",
    userMessage: "This result is strategy-only. Export the package or recover later.",
    technicalReason: "The clip has no rendered media, but the ranked guidance is still valid.",
    recommendedActions: ["export_strategy", "copy_package_only", "save_as_proof_idea"],
    primaryAction: "export_strategy",
    canContinue: true,
    shouldBlockExport: false,
    leeWuhLine: "Strategy only is not failure. It is a safe next move.",
  },
  missing_preview: {
    severity: "low",
    userMessage: "Preview media is missing, but the package can still be reviewed.",
    technicalReason: "A preview or download artifact was expected but not found.",
    recommendedActions: ["retry_render", "use_fallback_provider", "copy_package_only"],
    primaryAction: "retry_render",
    canContinue: true,
    shouldBlockExport: false,
    leeWuhLine: "The preview is missing. I can recover the path.",
  },
  provider_unavailable: {
    severity: "high",
    userMessage: "A provider is unavailable. Switch to a fallback path or degrade quality.",
    technicalReason: "Execution provider health or availability is failing.",
    recommendedActions: ["use_fallback_provider", "downgrade_quality", "retry_render"],
    primaryAction: "use_fallback_provider",
    canContinue: true,
    shouldBlockExport: true,
    leeWuhLine: "The provider is down. I’ll route around it.",
  },
  export_failed: {
    severity: "medium",
    userMessage: "Export failed, but the run can still be saved as proof or a package copy.",
    technicalReason: "The export path or asset packaging step failed.",
    recommendedActions: ["copy_package_only", "save_as_proof_idea", "retry_render"],
    primaryAction: "copy_package_only",
    canContinue: true,
    shouldBlockExport: true,
    leeWuhLine: "Export cracked, but the package still has value.",
  },
  asset_missing: {
    severity: "medium",
    userMessage: "A required asset is missing. Use fallback media or rebuild the asset path.",
    technicalReason: "A referenced runtime asset could not be resolved.",
    recommendedActions: ["use_fallback_provider", "open_support_context", "retry_render"],
    primaryAction: "use_fallback_provider",
    canContinue: true,
    shouldBlockExport: false,
    leeWuhLine: "A layer went missing. I can replace the path safely.",
  },
  invalid_source: {
    severity: "high",
    userMessage: "The source looks invalid for this run. Check the input before exporting.",
    technicalReason: "The source does not satisfy the current clipping or render constraints.",
    recommendedActions: ["open_support_context", "reset_run", "save_as_proof_idea"],
    primaryAction: "open_support_context",
    canContinue: false,
    shouldBlockExport: true,
    leeWuhLine: "The source is not clean enough yet.",
  },
  unknown_error: {
    severity: "medium",
    userMessage: "Something failed, but the run can still be analyzed and recovered.",
    technicalReason: "The failure did not match a more specific recovery case.",
    recommendedActions: ["open_support_context", "save_as_proof_idea", "reset_run"],
    primaryAction: "open_support_context",
    canContinue: true,
    shouldBlockExport: false,
    leeWuhLine: "Unknown error. I’ll keep the useful parts and inspect the rest.",
  },
};

export function getRecoveryDecision(
  issueType: LwaRecoveryIssueType,
): LwaRecoveryDecision {
  return {
    issueType,
    ...recoveryBlueprints[issueType],
  };
}

export function isStrategyOnlyResult(clipLike: Pick<ClipResult, "is_strategy_only" | "strategy_only" | "render_status" | "rendered_status" | "rendered" | "is_rendered" | "recovery_recommendation" | "render_error" | "preview_url" | "download_url" | "burned_caption_url" | "download_asset_url" | "edited_clip_url" | "clip_url" | "preview_image_url">): boolean {
  return Boolean(
    clipLike.is_strategy_only ||
      clipLike.strategy_only ||
      clipLike.render_status === "strategy_only" ||
      clipLike.rendered_status === "strategy_only",
  );
}

export function isRenderedResult(
  clipLike: Pick<ClipResult, "is_rendered" | "rendered" | "render_status" | "rendered_status" | "preview_url" | "download_url" | "burned_caption_url" | "download_asset_url" | "edited_clip_url" | "clip_url" | "preview_image_url">,
): boolean {
  return Boolean(
    clipLike.is_rendered ||
      clipLike.rendered ||
      clipLike.render_status === "ready" ||
      clipLike.rendered_status === "ready" ||
      clipLike.preview_url ||
      clipLike.download_url ||
      clipLike.burned_caption_url ||
      clipLike.download_asset_url ||
      clipLike.edited_clip_url ||
      clipLike.clip_url,
  );
}

export function getRecoveryActionsForClip(clipLike: ClipResult): LwaRecoveryDecision {
  if (clipLike.render_status === "failed" || clipLike.render_error) {
    return getRecoveryDecision("render_failed");
  }
  if (isStrategyOnlyResult(clipLike)) {
    return getRecoveryDecision("strategy_only");
  }
  if (clipLike.is_rendered || clipLike.rendered || clipLike.render_status === "ready") {
    const hasPreview = Boolean(
      clipLike.preview_url ||
        clipLike.download_url ||
        clipLike.burned_caption_url ||
        clipLike.download_asset_url ||
        clipLike.edited_clip_url ||
        clipLike.clip_url ||
        clipLike.preview_image_url,
    );

    if (!hasPreview) {
      return getRecoveryDecision("missing_preview");
    }
  }

  if (clipLike.recovery_recommendation && !isRenderedResult(clipLike)) {
    return getRecoveryDecision("strategy_only");
  }

  return getRecoveryDecision("unknown_error");
}

