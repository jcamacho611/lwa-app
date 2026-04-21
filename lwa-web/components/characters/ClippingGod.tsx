"use client";

import { CharacterState } from "../../lib/character-engine";
import type { CharacterActionId, CharacterAgent } from "../../lib/character-intelligence";
import { RiveCharacter } from "./RiveCharacter";

type ClippingGodProps = {
  state: CharacterState;
  agent: CharacterAgent;
  onAction?: (action: CharacterActionId) => void;
};

export default function ClippingGod({ state, agent, onAction }: ClippingGodProps) {
  return (
    <RiveCharacter
      src="/characters/clipping_god.riv"
      state={state}
      ariaLabel="Clipping God state character"
      className="pointer-events-none fixed bottom-5 right-5 z-20 hidden w-[220px] rounded-[30px] border border-fuchsia-400/15 bg-black/28 p-3 shadow-[0_0_44px_rgba(168,85,247,0.16)] backdrop-blur-xl sm:block lg:bottom-6 lg:right-6"
      canvasClassName="h-[112px] w-full rounded-[22px] lg:h-[134px]"
    >
      <div className="mt-3 rounded-2xl border border-white/10 bg-white/[0.055] px-3 py-3">
        <div className="flex items-center justify-between gap-2">
          <p className="text-[10px] uppercase tracking-[0.26em] text-fuchsia-100/60">{agent.name}</p>
          <span className="rounded-full border border-cyan-300/18 bg-cyan-300/8 px-2 py-1 text-[10px] font-medium text-cyan-100/78">
            {agent.mood}
          </span>
        </div>
        <p className="mt-2 text-xs font-medium leading-5 text-white/82">{agent.directive}</p>
        <p className="mt-2 line-clamp-2 text-[11px] leading-5 text-white/52">{agent.insight}</p>
        {agent.actions.length ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {agent.actions.slice(0, 2).map((action) => (
              <button
                key={action.id}
                type="button"
                onClick={() => onAction?.(action.id)}
                className="pointer-events-auto rounded-full border border-cyan-300/18 bg-cyan-300/8 px-3 py-1.5 text-[11px] font-medium text-cyan-50 transition hover:border-cyan-200/36 hover:bg-cyan-300/14"
              >
                {action.label}
              </button>
            ))}
          </div>
        ) : null}
      </div>
    </RiveCharacter>
  );
}
