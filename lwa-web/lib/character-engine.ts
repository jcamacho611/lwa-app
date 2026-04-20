export type CharacterState =
  | "idle"
  | "loading"
  | "analyzing"
  | "generating"
  | "rendering"
  | "ready"
  | "success"
  | "suggestion";

export type CharacterEngineInput = {
  isLoading: boolean;
  loadingStageIndex: number;
  hasSource: boolean;
  hasResult: boolean;
  renderedClipCount: number;
  strategyOnlyClipCount: number;
  recoveryActive?: boolean;
};

export const CHARACTER_STATE_VALUE: Record<CharacterState, number> = {
  idle: 0,
  loading: 1,
  analyzing: 2,
  generating: 3,
  rendering: 4,
  ready: 5,
  success: 6,
  suggestion: 7,
};

export function resolveCharacterState(input: CharacterEngineInput): CharacterState {
  if (input.recoveryActive) {
    return "rendering";
  }

  if (input.isLoading) {
    if (input.loadingStageIndex <= 0) {
      return "loading";
    }

    if (input.loadingStageIndex === 1) {
      return "analyzing";
    }

    return "rendering";
  }

  if (input.hasResult && input.strategyOnlyClipCount > 0) {
    return "suggestion";
  }

  if (input.hasResult && input.renderedClipCount > 0) {
    return "success";
  }

  if (input.hasResult) {
    return "ready";
  }

  return input.hasSource ? "ready" : "idle";
}

export function getCharacterGuidance(state: CharacterState, input: CharacterEngineInput) {
  if (state === "loading") {
    return "Reading the source.";
  }

  if (state === "analyzing") {
    return "Choosing the cuts.";
  }

  if (state === "rendering" || state === "generating") {
    return input.recoveryActive ? "Recovering media proof." : "Preparing the pack.";
  }

  if (state === "success") {
    return "Post the lead cut first.";
  }

  if (state === "suggestion") {
    return "Recover or test next.";
  }

  if (state === "ready") {
    return "Source ready.";
  }

  return "Drop one source.";
}

export function shouldShowStrategist(input: CharacterEngineInput) {
  return input.hasResult || input.strategyOnlyClipCount > 0;
}
