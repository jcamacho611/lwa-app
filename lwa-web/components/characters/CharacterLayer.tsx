"use client";

import {
  CharacterEngineInput,
  getCharacterGuidance,
  resolveCharacterState,
  shouldShowStrategist,
} from "../../lib/character-engine";
import { GeneratedScripts } from "../../lib/types";
import ClippingGod from "./ClippingGod";
import Strategist from "./Strategist";

type CharacterLayerProps = CharacterEngineInput & {
  scripts?: GeneratedScripts | null;
};

export default function CharacterLayer(props: CharacterLayerProps) {
  const state = resolveCharacterState(props);
  const guidance = getCharacterGuidance(state, props);
  const strategistVisible = shouldShowStrategist(props);

  return (
    <>
      <ClippingGod state={state} message={guidance} />
      <Strategist state={state} visible={strategistVisible} message={guidance} scripts={props.scripts} />
    </>
  );
}
