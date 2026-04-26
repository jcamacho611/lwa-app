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
      className="pointer-events-none fixed bottom-5 right-5 z-20 hidden w-[220px] rounded-[30px] border border-[var(--gold-border)] bg-[var(--surface-veil-strong)] p-3 shadow-[var(--shadow-glow)] backdrop-blur-xl sm:block lg:bottom-6 lg:right-6"
      canvasClassName="h-[112px] w-full rounded-[22px] lg:h-[134px]"
    >
      <div className="mt-3 rounded-2xl border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-3">
        <div className="flex items-center justify-between gap-2">
          <p className="text-[10px] uppercase tracking-[0.26em] text-[var(--ink-mid)]">{agent.name}</p>
          <span className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-2 py-1 text-[10px] font-medium text-[var(--gold)]">
            {agent.mood}
          </span>
        </div>
        <p className="mt-2 text-xs font-medium leading-5 text-[var(--ink)]">{agent.directive}</p>
        <p className="mt-2 line-clamp-2 text-[11px] leading-5 text-[var(--ink-mid)]">{agent.insight}</p>
        {agent.actions.length ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {agent.actions.slice(0, 2).map((action) => (
              <button
                key={action.id}
                type="button"
                onClick={() => onAction?.(action.id)}
                className="pointer-events-auto rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-1.5 text-[11px] font-medium text-[var(--gold)] transition hover:bg-[var(--surface-gold-ghost)]"
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
