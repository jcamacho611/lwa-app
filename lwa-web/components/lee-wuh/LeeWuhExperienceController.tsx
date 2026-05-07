"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import {
  applyLwaExperienceEvent,
  type LwaExperienceEvent,
  type LwaExperienceReward,
  type LwaExperienceState,
  type LwaExperienceTransition,
} from "../../lib/lwa-experience-state";
import {
  applyMissionEvent,
  getActiveMission,
  getCompletedMissions,
  getStarterMissions,
} from "../../lib/lwa-mission-engine";
import { getLeeWuhExperienceReaction } from "../../lib/lee-wuh-reactions";
import LeeWuhCharacterStage, {
  type LeeWuhStageMood,
} from "./LeeWuhCharacterStage";
import LeeWuhMissionPanel from "./LeeWuhMissionPanel";
import LeeWuhRewardToast from "./LeeWuhRewardToast";

const controllerEvents: { event: LwaExperienceEvent; label: string }[] = [
  { event: "SOURCE_ADDED", label: "Source added" },
  { event: "GENERATION_STARTED", label: "Generation" },
  { event: "RENDERING_STARTED", label: "Rendering" },
  { event: "CLIPS_RENDERED", label: "Clips ready" },
  { event: "STRATEGY_ONLY_RETURNED", label: "Strategy only" },
  { event: "EXPORT_READY", label: "Export ready" },
  { event: "EXPORT_PACKAGE_COPIED", label: "Copy package" },
  { event: "PROOF_SAVED", label: "Proof saved" },
  { event: "RECOVERY_AVAILABLE", label: "Recovery" },
  { event: "MARKETPLACE_OPENED", label: "Marketplace" },
  { event: "REALM_ENTERED", label: "Realm" },
  { event: "ERROR_OCCURRED", label: "Error" },
  { event: "RESET", label: "Reset" },
];

const initialTransition: LwaExperienceTransition = {
  previousState: "idle",
  state: "idle",
  event: "RESET",
  timestamp: new Date().toISOString(),
  guidance: "Add a source to start the next signal path.",
  nextAction: "Add source",
  leeWuhReaction: "Lee-Wuh is watching for the first source.",
};

function stageMoodForState(state: LwaExperienceState): LeeWuhStageMood {
  switch (state) {
    case "analyzing":
      return "analyzing";
    case "rendering":
      return "focused";
    case "clips_ready":
    case "proof_saved":
    case "mission_complete":
    case "reward_unlocked":
      return "victory";
    case "strategy_only":
    case "error":
      return "warning";
    case "source_added":
    case "marketplace_ready":
    case "realm_open":
    case "export_ready":
      return "focused";
    default:
      return "idle";
  }
}

export default function LeeWuhExperienceController() {
  const [currentState, setCurrentState] = useState<LwaExperienceState>("idle");
  const [transition, setTransition] =
    useState<LwaExperienceTransition>(initialTransition);
  const [missions, setMissions] = useState(() => getStarterMissions());
  const [reward, setReward] = useState<LwaExperienceReward | null>(null);

  const reaction = getLeeWuhExperienceReaction(transition.state);
  const completedMissions = useMemo(
    () => getCompletedMissions(missions),
    [missions],
  );
  const activeMission = useMemo(() => getActiveMission(missions), [missions]);
  const completedXp = completedMissions.reduce(
    (total, mission) => total + mission.reward.xp,
    0,
  );

  const handleEvent = (event: LwaExperienceEvent) => {
    const nextTransition = applyLwaExperienceEvent(currentState, event);
    setCurrentState(nextTransition.state);
    setTransition(nextTransition);

    if (event === "RESET") {
      setMissions(getStarterMissions());
      setReward(null);
      return;
    }

    setMissions((currentMissions) => applyMissionEvent(currentMissions, event));
    if (nextTransition.reward) {
      setReward(nextTransition.reward);
    }
  };

  return (
    <section className="relative mx-auto max-w-7xl px-6 py-12 text-[#F5F1E8]">
      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.88fr)_minmax(0,1.12fr)]">
        <div className="space-y-6">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">
              Lee-Wuh experience controller
            </p>
            <h2 className="mt-5 text-[clamp(2.4rem,5vw,5rem)] font-black uppercase leading-[0.92] tracking-normal text-white">
              The living interface layer.
            </h2>
            <p className="mt-6 text-base leading-8 text-white/62">
              This controller uses the canonical LWA event reducer and local
              mission engine. It is frontend-only and does not change generate,
              auth, payments, payouts, or backend providers.
            </p>
          </div>

          <LeeWuhCharacterStage
            mood={stageMoodForState(transition.state)}
            variant="card"
            posterPath="/brand/lee-wuh/lee-wuh-avatar.png"
            title="Lee-Wuh"
            message={reaction.line}
          />

          {reward ? (
            <LeeWuhRewardToast
              reward={reward}
              onDismiss={() => setReward(null)}
            />
          ) : null}
        </div>

        <div className="space-y-6">
          <section className="rounded-[28px] border border-white/10 bg-black/35 p-6 shadow-[0_28px_90px_-60px_rgba(126,58,242,0.9)]">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
                  Current state
                </p>
                <h3 className="mt-3 text-3xl font-black uppercase text-white">
                  {transition.state.replaceAll("_", " ")}
                </h3>
              </div>
              <span className="rounded-full border border-[#C9A24A]/25 bg-[#C9A24A]/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.16em] text-[#E9C77B]">
                {reaction.mood}
              </span>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                  Lee-Wuh line
                </p>
                <p className="mt-2 text-sm leading-6 text-white/70">
                  {reaction.line}
                </p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                  Next action
                </p>
                <p className="mt-2 text-sm leading-6 text-[#E9C77B]">
                  {reaction.recommendedActionLabel}
                </p>
                {reaction.recommendedHref ? (
                  <Link
                    href={reaction.recommendedHref}
                    className="mt-3 inline-flex rounded-full border border-[#C9A24A]/30 bg-[#C9A24A]/10 px-3 py-2 text-xs font-semibold text-[#E9C77B] transition hover:bg-[#C9A24A]/20"
                  >
                    Open path
                  </Link>
                ) : null}
              </div>
            </div>

            <div className="mt-5 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                Reducer guidance
              </p>
              <p className="mt-2 text-sm leading-6 text-white/62">
                {transition.guidance}
              </p>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              {controllerEvents.map((item) => (
                <button
                  key={item.event}
                  type="button"
                  onClick={() => handleEvent(item.event)}
                  className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-2 text-xs font-semibold text-white/72 transition hover:border-[#C9A24A]/40 hover:bg-[#C9A24A]/10 hover:text-white"
                >
                  {item.label}
                </button>
              ))}
            </div>
          </section>

          <LeeWuhMissionPanel
            activeMission={activeMission}
            completedMissions={completedMissions}
            completedXp={completedXp}
          />
        </div>
      </div>
    </section>
  );
}

