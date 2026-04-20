"use client";

import { CharacterState } from "../../lib/character-engine";
import { GeneratedScripts } from "../../lib/types";
import { RiveCharacter } from "./RiveCharacter";

type StrategistProps = {
  state: CharacterState;
  visible: boolean;
  message: string;
  scripts?: GeneratedScripts | null;
};

export default function Strategist({ state, visible, message, scripts }: StrategistProps) {
  if (!visible) {
    return null;
  }

  return (
    <aside className="pointer-events-none fixed right-0 top-24 z-10 hidden w-[280px] translate-x-4 rounded-l-[30px] border border-cyan-300/12 border-r-0 bg-black/24 p-3 opacity-95 shadow-[0_0_48px_rgba(34,211,238,0.12)] backdrop-blur-xl transition-all duration-300 xl:block">
      <div className="flex items-center gap-3">
        <RiveCharacter
          src="/characters/strategist.riv"
          state={state}
          ariaLabel="Strategist state character"
          className="h-[84px] w-[84px] shrink-0 rounded-[24px]"
          canvasClassName="h-full w-full rounded-[24px]"
        />
        <div>
          <p className="text-[10px] uppercase tracking-[0.28em] text-cyan-200/70">Strategist</p>
          <p className="mt-2 text-sm font-medium leading-5 text-white/78">{message}</p>
        </div>
      </div>
      {scripts ? (
        <div className="mt-4 space-y-3 rounded-2xl border border-white/10 bg-white/[0.04] p-3">
          <p className="text-[10px] uppercase tracking-[0.24em] text-white/45">Next script</p>
          <p className="max-h-20 overflow-hidden text-sm leading-5 text-white/75">{scripts.main}</p>
          {scripts.hooks.length ? (
            <div className="space-y-1">
              {scripts.hooks.slice(0, 2).map((hook) => (
                <p key={hook} className="text-xs leading-5 text-cyan-100/70">
                  {hook}
                </p>
              ))}
            </div>
          ) : null}
        </div>
      ) : null}
    </aside>
  );
}
