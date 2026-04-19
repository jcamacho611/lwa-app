import type { WorldState } from "../lib/world-state";
import { WorldLayer } from "./WorldLayer";

type WorldCharacterProps = {
  position: "left" | "right" | "center";
  tone: "crimson" | "magenta" | "cyan";
  state: WorldState;
};

export function WorldCharacter({ position, tone, state }: WorldCharacterProps) {
  return (
    <WorldLayer className="world-character-layer">
      <div
        className={`world-character world-character-${position} world-character-${tone}`}
        data-character-state={state}
        data-character-tone={tone}
      >
        <div className="world-character-shell">
          <div className="world-character-aura" />
          <div className="world-character-sigil" />
          <div className="world-character-crown" />
          <div className="world-character-core" />
          <div className="world-character-veil" />
          <div className="world-character-eyes" />
        </div>
      </div>
    </WorldLayer>
  );
}
