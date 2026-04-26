"use client";

import { CharacterState } from "../../lib/character-engine";
import type { CharacterActionId, CharacterAgent } from "../../lib/character-intelligence";
import { GeneratedScripts } from "../../lib/types";
import { RiveCharacter } from "./RiveCharacter";

type StrategistProps = {
  state: CharacterState;
  visible: boolean;
  agent: CharacterAgent;
  scripts?: GeneratedScripts | null;
  onAction?: (action: CharacterActionId) => void;
};

export default function Strategist({ state, visible, agent, scripts, onAction }: StrategistProps) {
  if (!visible) {
    return null;
  }

  return (
    <aside className="pointer-events-none fixed right-0 top-24 z-10 hidden w-[280px] translate-x-4 rounded-l-[30px] border border-[var(--gold-border)] border-r-0 bg-[var(--surface-veil-strong)] p-3 opacity-95 shadow-[var(--shadow-glow)] backdrop-blur-xl transition-all duration-300 xl:block">
      <div className="flex items-center gap-3">
        <RiveCharacter
          src="/characters/strategist.riv"
          state={state}
          ariaLabel="Strategist state character"
          className="h-[84px] w-[84px] shrink-0 rounded-[24px]"
          canvasClassName="h-full w-full rounded-[24px]"
        />
        <div>
          <p className="text-[10px] uppercase tracking-[0.28em] text-[var(--ink-mid)]">{agent.name}</p>
          <p className="mt-2 text-sm font-medium leading-5 text-[var(--ink)]">{agent.directive}</p>
        </div>
      </div>
      <p className="mt-4 rounded-2xl border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-3 text-xs leading-5 text-[var(--ink-mid)]">
        {agent.insight}
      </p>
      {scripts ? (
        <div className="mt-4 space-y-3 rounded-2xl border border-[var(--divider)] bg-[var(--surface-soft)] p-3">
          <p className="text-[10px] uppercase tracking-[0.24em] text-[var(--ink-faint)]">Next script</p>
          <p className="max-h-20 overflow-hidden text-sm leading-5 text-[var(--ink-mid)]">{scripts.main}</p>
          {scripts.hooks.length ? (
            <div className="space-y-1">
              {scripts.hooks.slice(0, 2).map((hook) => (
                <p key={hook} className="text-xs leading-5 text-[var(--gold)]">
                  {hook}
                </p>
              ))}
            </div>
          ) : null}
        </div>
      ) : null}
      {agent.actions.length ? (
        <div className="pointer-events-auto mt-4 grid gap-2">
          {agent.actions.map((action) => (
            <button
              key={action.id}
              type="button"
              onClick={() => onAction?.(action.id)}
              className="rounded-full border border-[var(--gold-border)] bg-[var(--gold-dim)] px-3 py-2 text-left text-xs font-medium text-[var(--gold)] transition hover:bg-[var(--surface-gold-ghost)]"
            >
              {action.label}
            </button>
          ))}
        </div>
      ) : null}
    </aside>
  );
}
