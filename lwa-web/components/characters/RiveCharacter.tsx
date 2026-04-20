"use client";

import { ReactNode, useEffect, useState } from "react";
import { useRive, useStateMachineInput } from "@rive-app/react-canvas";
import { CHARACTER_STATE_VALUE, CharacterState } from "../../lib/character-engine";

type RiveCharacterProps = {
  src: string;
  state: CharacterState;
  stateMachineName?: string;
  className?: string;
  canvasClassName?: string;
  ariaLabel: string;
  children?: ReactNode;
};

const stateMachineInputName = "system_state";

function fireStateInput(input: ReturnType<typeof useStateMachineInput>) {
  if (!input) {
    return;
  }

  input.fire();
}

export function RiveCharacter({
  src,
  state,
  stateMachineName = "State Machine 1",
  className,
  canvasClassName,
  ariaLabel,
  children,
}: RiveCharacterProps) {
  const [assetStatus, setAssetStatus] = useState<"checking" | "available" | "missing">("checking");

  useEffect(() => {
    let cancelled = false;

    setAssetStatus("checking");
    fetch(src, { method: "HEAD", cache: "no-store" })
      .then((response) => {
        if (!cancelled) {
          setAssetStatus(response.ok ? "available" : "missing");
        }
      })
      .catch(() => {
        if (!cancelled) {
          setAssetStatus("missing");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [src]);

  const shouldLoad = assetStatus === "available";
  const { rive, RiveComponent } = useRive(
    shouldLoad
      ? {
          src,
          stateMachines: stateMachineName,
          autoplay: true,
          automaticallyHandleEvents: false,
          shouldDisableRiveListeners: true,
          onLoadError: () => setAssetStatus("missing"),
        }
      : null,
    {
      useDevicePixelRatio: true,
      shouldResizeCanvasToContainer: true,
      shouldUseIntersectionObserver: true,
    },
  );

  const numericStateInput = useStateMachineInput(rive, stateMachineName, stateMachineInputName, CHARACTER_STATE_VALUE[state]);
  const idleInput = useStateMachineInput(rive, stateMachineName, "idle");
  const loadingInput = useStateMachineInput(rive, stateMachineName, "loading");
  const analyzingInput = useStateMachineInput(rive, stateMachineName, "analyzing");
  const generatingInput = useStateMachineInput(rive, stateMachineName, "generating");
  const renderingInput = useStateMachineInput(rive, stateMachineName, "rendering");
  const readyInput = useStateMachineInput(rive, stateMachineName, "ready");
  const successInput = useStateMachineInput(rive, stateMachineName, "success");
  const suggestionInput = useStateMachineInput(rive, stateMachineName, "suggestion");

  useEffect(() => {
    if (numericStateInput) {
      numericStateInput.value = CHARACTER_STATE_VALUE[state];
    }

    const triggerByState: Record<CharacterState, ReturnType<typeof useStateMachineInput>> = {
      idle: idleInput,
      loading: loadingInput,
      analyzing: analyzingInput,
      generating: generatingInput,
      rendering: renderingInput,
      ready: readyInput,
      success: successInput,
      suggestion: suggestionInput,
    };

    fireStateInput(triggerByState[state]);
  }, [
    analyzingInput,
    generatingInput,
    idleInput,
    loadingInput,
    numericStateInput,
    readyInput,
    renderingInput,
    state,
    successInput,
    suggestionInput,
  ]);

  if (!shouldLoad) {
    return null;
  }

  return (
    <div className={className} aria-label={ariaLabel}>
      <RiveComponent className={canvasClassName} />
      {children}
    </div>
  );
}
