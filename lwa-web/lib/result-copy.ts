export const RESULT_COPY = {
  whyPicked: "Why this was picked",
  previewProcessing: "Preview still processing",
  previewRetry: "Retry preview",
  ideasOnly: "Ideas only",
  finishedPreviews: "Finished previews",
  postingPlan: "Keep this in your posting plan while the preview finishes.",
  strongSignal: "Strong early signal.",
  noPreviewYet: "No preview yet",
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
    .replace(/strategy-only/gi, RESULT_COPY.ideasOnly)
    .replace(/strategy card/gi, "idea card")
    .replace(/recover render/gi, RESULT_COPY.previewRetry);
}
