import type { LeeWuhAnimationState } from "./leeWuhAnimationStates";
import type { LeeWuhMove } from "./leeWuhMoves";

export type LeeWuhAgentPanel = "closed" | "chat" | "moves" | "assets";

export type LeeWuhAgentState = {
  panel: LeeWuhAgentPanel;
  animation: LeeWuhAnimationState;
  activeMove?: LeeWuhMove | null;
  lastUserIntent?: string | null;
};

export type LeeWuhAgentEvent =
  | { type: "open"; panel?: LeeWuhAgentPanel }
  | { type: "close" }
  | { type: "set-animation"; animation: LeeWuhAnimationState }
  | { type: "select-move"; move: LeeWuhMove }
  | { type: "set-intent"; intent: string };

export const initialLeeWuhAgentState: LeeWuhAgentState = {
  panel: "closed",
  animation: "idle",
  activeMove: null,
  lastUserIntent: null,
};

export function leeWuhAgentReducer(
  state: LeeWuhAgentState,
  event: LeeWuhAgentEvent,
): LeeWuhAgentState {
  switch (event.type) {
    case "open":
      return { ...state, panel: event.panel || "chat", animation: "click" };
    case "close":
      return { ...state, panel: "closed", animation: "idle" };
    case "set-animation":
      return { ...state, animation: event.animation };
    case "select-move":
      return { ...state, activeMove: event.move, animation: event.move.state };
    case "set-intent":
      return { ...state, lastUserIntent: event.intent, animation: "thinking" };
    default:
      return state;
  }
}
