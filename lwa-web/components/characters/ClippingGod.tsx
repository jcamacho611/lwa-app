"use client";

import { CharacterState } from "../../lib/character-engine";
import { RiveCharacter } from "./RiveCharacter";

type ClippingGodProps = {
  state: CharacterState;
  message: string;
};

export default function ClippingGod({ state, message }: ClippingGodProps) {
  return (
    <RiveCharacter
      src="/characters/clipping_god.riv"
      state={state}
      ariaLabel="Clipping God state character"
      className="pointer-events-none fixed bottom-5 right-5 z-20 hidden w-[128px] rounded-[28px] border border-fuchsia-400/15 bg-black/25 p-2 shadow-[0_0_44px_rgba(168,85,247,0.16)] backdrop-blur-xl sm:block lg:bottom-6 lg:right-6 lg:w-[150px]"
      canvasClassName="h-[112px] w-full rounded-[22px] lg:h-[134px]"
    >
      <div className="mt-2 rounded-2xl border border-white/10 bg-white/[0.05] px-3 py-2 text-center text-[11px] font-medium leading-4 text-white/74">
        {message}
      </div>
    </RiveCharacter>
  );
}
