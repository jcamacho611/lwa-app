"use client";

import { useEffect, useState } from "react";
import { fireGodTrigger } from "../lib/character-ai";
import {
  addLWACharacterListener,
  type CharacterSide,
  type CharacterState,
  type GodName,
} from "../lib/character-controller";
import { GodCharacter } from "./GodCharacter";

type SideState = {
  god: GodName;
  state: CharacterState;
  speech: string | null;
};

type StageState = Record<CharacterSide, SideState>;

const INITIAL_STAGE: StageState = {
  left: { god: "athena", state: "breathe", speech: null },
  right: { god: "hades", state: "breathe", speech: null },
};

function resolveSide(god?: GodName, requestedSide?: CharacterSide): CharacterSide {
  if (requestedSide) return requestedSide;
  if (!god) return "left";
  return god === "hades" || god === "anubis" ? "right" : "left";
}

export function CharacterStage() {
  const [stage, setStage] = useState<StageState>(INITIAL_STAGE);

  useEffect(() => {
    void fireGodTrigger("first_visit", { route: window.location.pathname });

    return addLWACharacterListener((event) => {
      const side = resolveSide(event.god, event.side);
      const state = event.state || (event.speech ? "speak" : "breathe");

      setStage((current) => ({
        ...current,
        [side]: {
          god: event.god || current[side].god,
          state,
          speech: event.speech ?? (state === "speak" ? current[side].speech : null),
        },
      }));

      if (event.speech || state !== "breathe") {
        window.setTimeout(() => {
          setStage((current) => ({
            ...current,
            [side]: { ...current[side], state: "breathe", speech: null },
          }));
        }, event.speech ? 6200 : 1800);
      }
    });
  }, []);

  return (
    <div className="character-stage" aria-hidden="true">
      <GodCharacter side="left" god={stage.left.god} state={stage.left.state} speech={stage.left.speech} />
      <GodCharacter side="right" god={stage.right.god} state={stage.right.state} speech={stage.right.speech} />
    </div>
  );
}
