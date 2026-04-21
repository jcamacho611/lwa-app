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

function fallbackTone(state: CharacterState) {
  if (state === "loading" || state === "analyzing") {
    return "from-fuchsia-400/45 via-cyan-300/28 to-blue-500/20";
  }
  if (state === "generating" || state === "rendering") {
    return "from-cyan-300/48 via-blue-500/30 to-fuchsia-400/18";
  }
  if (state === "success" || state === "suggestion" || state === "ready") {
    return "from-amber-200/36 via-cyan-300/24 to-fuchsia-500/20";
  }
  return "from-fuchsia-400/22 via-blue-400/16 to-cyan-300/12";
}

function CharacterFallbackFigure({ state }: { state: CharacterState }) {
  return (
    <div
      className={[
        "relative h-full min-h-[84px] w-full overflow-hidden rounded-[22px] border border-white/10 bg-black/35",
        "shadow-[inset_0_0_40px_rgba(255,255,255,0.04)]",
      ].join(" ")}
      data-rive-fallback-state={state}
    >
      <div className={["absolute inset-0 bg-gradient-to-br blur-[1px]", fallbackTone(state)].join(" ")} />
      <div className="absolute left-1/2 top-1/2 h-[78%] w-[52%] -translate-x-1/2 -translate-y-1/2 rounded-[44%_44%_36%_36%] border border-cyan-200/20 bg-[radial-gradient(circle_at_50%_18%,rgba(255,255,255,0.38),transparent_12%),linear-gradient(180deg,rgba(12,18,38,0.75),rgba(2,5,16,0.96))] shadow-[0_0_34px_rgba(34,211,238,0.18)]" />
      <div className="absolute left-1/2 top-[36%] h-[10%] w-[32%] -translate-x-1/2 rounded-full bg-cyan-100/75 shadow-[0_0_22px_rgba(34,211,238,0.8)]" />
      <div className="absolute left-1/2 top-[58%] h-[26%] w-[72%] -translate-x-1/2 rounded-full border border-fuchsia-300/20 bg-fuchsia-400/8 blur-sm" />
      <div className="absolute inset-x-[18%] bottom-[12%] h-px bg-gradient-to-r from-transparent via-cyan-200/60 to-transparent" />
    </div>
  );
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
    return (
      <div className={className} aria-label={ariaLabel} data-rive-asset-status={assetStatus}>
        <div className={canvasClassName}>
          <CharacterFallbackFigure state={state} />
        </div>
        {children}
      </div>
    );
  }

  return (
    <div className={className} aria-label={ariaLabel}>
      <RiveComponent className={canvasClassName} />
      {children}
    </div>
  );
}
