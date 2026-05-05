"use client";

import { createContext, useContext, useMemo, useReducer, type ReactNode } from "react";
import {
  initialLeeWuhAgentState,
  leeWuhAgentReducer,
  type LeeWuhAgentEvent,
  type LeeWuhAgentState,
} from "./leeWuhState";

type LeeWuhAgentContextValue = {
  state: LeeWuhAgentState;
  dispatch: React.Dispatch<LeeWuhAgentEvent>;
  surface: string;
};

const LeeWuhAgentContext = createContext<LeeWuhAgentContextValue | null>(null);

export function LeeWuhAgentProvider({
  children,
  surface = "default",
}: {
  children: ReactNode;
  surface?: string;
}) {
  const [state, dispatch] = useReducer(leeWuhAgentReducer, initialLeeWuhAgentState);
  const value = useMemo(() => ({ state, dispatch, surface }), [state, surface]);

  return (
    <LeeWuhAgentContext.Provider value={value}>
      {children}
    </LeeWuhAgentContext.Provider>
  );
}

export function useLeeWuhAgent() {
  const context = useContext(LeeWuhAgentContext);
  if (!context) {
    throw new Error("useLeeWuhAgent must be used inside LeeWuhAgentProvider");
  }
  return context;
}
