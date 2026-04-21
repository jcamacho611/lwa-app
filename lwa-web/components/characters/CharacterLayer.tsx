"use client";

import { useEffect, useMemo, useState } from "react";
import {
  CharacterEngineInput,
  resolveCharacterState,
  shouldShowStrategist,
} from "../../lib/character-engine";
import {
  CharacterActionId,
  createCharacterAgent,
  readCharacterMemory,
  writeCharacterMemory,
} from "../../lib/character-intelligence";
import { ClipResult, GeneratedScripts, GenerateResponse } from "../../lib/types";
import { ReadyQueueItem } from "../../lib/queue";
import ClippingGod from "./ClippingGod";
import Strategist from "./Strategist";

type CharacterLayerProps = CharacterEngineInput & {
  scripts?: GeneratedScripts | null;
  result?: GenerateResponse | null;
  orderedClips?: ClipResult[];
  renderedClips?: ClipResult[];
  strategyOnlyClips?: ClipResult[];
  readyQueue?: ReadyQueueItem[];
  onAction?: (action: CharacterActionId) => void;
};

export default function CharacterLayer(props: CharacterLayerProps) {
  const [memory, setMemory] = useState(readCharacterMemory);
  const state = resolveCharacterState(props);
  const strategistVisible = shouldShowStrategist(props);
  const agent = useMemo(
    () =>
      createCharacterAgent(
        {
          isLoading: props.isLoading,
          loadingStageIndex: props.loadingStageIndex,
          hasSource: props.hasSource,
          result: props.result,
          orderedClips: props.orderedClips,
          renderedClips: props.renderedClips,
          strategyOnlyClips: props.strategyOnlyClips,
          readyQueue: props.readyQueue,
          recoveryActive: props.recoveryActive,
          scripts: props.scripts,
        },
        memory,
      ),
    [
      memory,
      props.hasSource,
      props.isLoading,
      props.loadingStageIndex,
      props.orderedClips,
      props.readyQueue,
      props.recoveryActive,
      props.renderedClips,
      props.result,
      props.scripts,
      props.strategyOnlyClips,
    ],
  );

  useEffect(() => {
    if (agent.memory === memory) {
      return;
    }

    writeCharacterMemory(agent.memory);
    setMemory(agent.memory);
  }, [agent.memory, memory]);

  return (
    <>
      <ClippingGod state={state} agent={agent} onAction={props.onAction} />
      <Strategist state={state} visible={strategistVisible} agent={agent} scripts={props.scripts} onAction={props.onAction} />
    </>
  );
}
