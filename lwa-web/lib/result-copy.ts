export const RESULT_COPY = {
  // Clip status labels
  renderedReady: "READY NOW",
  strategyOnly: "STRATEGY ONLY",
  strategyOnlyShort: "Strategy only",
  recoverRender: "Recover render",

  // Legacy / compat
  whyPicked: "Why this clip ranked",
  previewProcessing: "Strategy only",
  previewRetry: "Recover render",
  ideasOnly: "Strategy only",
  finishedPreviews: "Rendered clips",
  noPreviewYet: "Render not ready",

  // Reasoning copy
  postingPlan: "Keep this in your posting plan — render it when ready.",
  strongSignal: "Strong signal detected.",

  // Package / export
  copyPackage: "Copy package",
  packageCopied: "Package copied",
  copyHook: "Copy hook",
  hookCopied: "Copied!",
  exportClip: "Export clip",
  queuePost: "Queue post",
  queued: "Queued for post",
  packageNotes: "Package notes",
} as const;

export function buildLeadReason(raw?: string | null): string {
  if (!raw?.trim()) {
    return `${RESULT_COPY.strongSignal} ${RESULT_COPY.postingPlan}`;
  }

  return raw
    .replace(/system call/gi, RESULT_COPY.whyPicked)
    .replace(/render proof/gi, "preview")
    .replace(/media proof/gi, "preview")
    .replace(/keep it in the stack/gi, "keep this in your posting plan")
    .replace(/strategy[-\s]only/gi, RESULT_COPY.strategyOnlyShort)
    .replace(/strategy card/gi, "strategy clip")
    .replace(/recover render/gi, RESULT_COPY.recoverRender)
    .replace(/ideas only/gi, RESULT_COPY.strategyOnlyShort);
}
