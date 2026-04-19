export type WorldState = "idle" | "alert" | "focus" | "surge";
export type WorldSignal = "idle" | "hover" | "focus" | "generating" | "complete";
export type WorldMode = "quick" | "pro";
export type WorldPhase = "idle" | "analyzing" | "generating" | "rendering" | "ready";

type ResolveWorldStateInput = {
  variant?: "workspace" | "home";
  generationMode?: WorldMode;
  inputFocused?: boolean;
  generatorHovered?: boolean;
  isLoading?: boolean;
  loadingStageIndex?: number;
  hasResult?: boolean;
  hasSource?: boolean;
  completionPulse?: boolean;
};

const CHARACTER_RESPONSES: Array<Record<WorldState, WorldState>> = [
  {
    idle: "idle",
    alert: "alert",
    focus: "focus",
    surge: "surge",
  },
  {
    idle: "idle",
    alert: "focus",
    focus: "surge",
    surge: "surge",
  },
  {
    idle: "alert",
    alert: "focus",
    focus: "focus",
    surge: "surge",
  },
];

export function resolveWorldState({
  variant = "workspace",
  generationMode = "quick",
  inputFocused = false,
  generatorHovered = false,
  isLoading = false,
  loadingStageIndex = 0,
  hasResult = false,
  hasSource = false,
  completionPulse = false,
}: ResolveWorldStateInput): WorldState {
  if (isLoading || completionPulse) {
    return "surge";
  }

  if (inputFocused) {
    return "focus";
  }

  if (generatorHovered || hasSource || hasResult) {
    return generationMode === "pro" ? "focus" : "alert";
  }

  if (variant === "home" && generationMode === "pro") {
    return "alert";
  }

  return "idle";
}

export function resolveWorldPhase({
  isLoading = false,
  loadingStageIndex = 0,
  hasResult = false,
  hasSource = false,
  completionPulse = false,
}: ResolveWorldStateInput): WorldPhase {
  if (isLoading) {
    if (loadingStageIndex <= 0) {
      return "analyzing";
    }
    if (loadingStageIndex === 1) {
      return "generating";
    }
    return "rendering";
  }

  if (completionPulse || hasResult) {
    return "ready";
  }

  if (hasSource) {
    return "analyzing";
  }

  return "idle";
}

export function resolveCharacterState(index: number, worldState: WorldState): WorldState {
  const response = CHARACTER_RESPONSES[index] || CHARACTER_RESPONSES[0];
  return response[worldState];
}
