"use client";

import { useMemo, useState } from "react";
import {
  applyLwaExperienceEvent,
  type LwaExperienceEvent,
  type LwaExperienceState,
  type LwaExperienceTransition,
} from "../../lib/lwa-experience-state";
import {
  applyMissionEvent,
  getActiveMission,
  getCompletedMissions,
  getStarterMissions,
} from "../../lib/lwa-mission-engine";
import {
  lwaHiddenEngineMap,
  priorityHiddenEngineIds,
  type LwaHiddenEngine,
} from "../../lib/lwa-hidden-engine-map";

const demoEvents: { event: LwaExperienceEvent; label: string }[] = [
  { event: "SOURCE_ADDED", label: "Source" },
  { event: "GENERATION_STARTED", label: "Analyze" },
  { event: "RENDERING_STARTED", label: "Render" },
  { event: "CLIPS_RENDERED", label: "Clips" },
  { event: "STRATEGY_ONLY_RETURNED", label: "Strategy" },
  { event: "EXPORT_PACKAGE_COPIED", label: "Export" },
  { event: "PROOF_SAVED", label: "Proof" },
  { event: "RECOVERY_AVAILABLE", label: "Recover" },
  { event: "MARKETPLACE_OPENED", label: "Market" },
  { event: "REALM_ENTERED", label: "Realm" },
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

function isPriorityEngine(engine: LwaHiddenEngine) {
  return priorityHiddenEngineIds.includes(
    engine.id as (typeof priorityHiddenEngineIds)[number],
  );
}

function statusLabel(status: LwaHiddenEngine["status"]) {
  return status.replaceAll("-", " ");
}

export default function LeeWuhEngineMapPanel() {
  const [currentState, setCurrentState] = useState<LwaExperienceState>("idle");
  const [transition, setTransition] = useState<LwaExperienceTransition>(initialTransition);
  const [missions, setMissions] = useState(() => getStarterMissions());
  const completedMissions = useMemo(() => getCompletedMissions(missions), [missions]);
  const activeMission = useMemo(() => getActiveMission(missions), [missions]);
  const completedXp = completedMissions.reduce(
    (total, mission) => total + mission.reward.xp,
    0,
  );

  const handleEvent = (event: LwaExperienceEvent) => {
    if (event === "RESET") {
      const nextTransition = applyLwaExperienceEvent(currentState, event);
      setCurrentState(nextTransition.state);
      setTransition(nextTransition);
      setMissions(getStarterMissions());
      return;
    }

    const nextTransition = applyLwaExperienceEvent(currentState, event);
    setCurrentState(nextTransition.state);
    setTransition(nextTransition);
    setMissions((currentMissions) => applyMissionEvent(currentMissions, event));
  };

  return (
    <section className="relative mx-auto max-w-7xl px-6 py-12 text-[#F5F1E8]">
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)]">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">
            Hidden engine foundation
          </p>
          <h2 className="mt-5 text-[clamp(2.5rem,5vw,5rem)] font-black uppercase leading-[0.92] tracking-normal text-white">
            Engines, events, states, missions.
          </h2>
          <p className="mt-6 max-w-3xl text-base leading-8 text-white/62">
            This panel is a local frontend foundation. It does not touch auth,
            payment, payout, crypto, backend providers, or the generate API.
          </p>

          <div className="mt-8 grid gap-4 md:grid-cols-2">
            {lwaHiddenEngineMap.map((engine) => {
              const priority = isPriorityEngine(engine);
              return (
                <article
                  key={engine.id}
                  className={[
                    "rounded-[24px] border p-5",
                    priority
                      ? "border-[#C9A24A]/30 bg-[#C9A24A]/10"
                      : "border-white/10 bg-white/[0.04]",
                  ].join(" ")}
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={[
                        "rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em]",
                        priority
                          ? "border-[#C9A24A]/35 bg-black/25 text-[#E9C77B]"
                          : "border-white/10 bg-black/20 text-white/45",
                      ].join(" ")}
                    >
                      {priority ? "priority" : engine.category}
                    </span>
                    <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-white/45">
                      {statusLabel(engine.status)}
                    </span>
                  </div>
                  <h3 className="mt-4 text-xl font-semibold text-white">{engine.name}</h3>
                  <p className="mt-3 text-sm leading-6 text-white/58">{engine.purpose}</p>
                  <div className="mt-4 rounded-2xl border border-white/10 bg-black/25 p-4">
                    <p className="text-xs uppercase tracking-[0.2em] text-[#E9C77B]">
                      First safe slice
                    </p>
                    <p className="mt-2 text-sm leading-6 text-white/62">
                      {engine.firstSafeSlice}
                    </p>
                  </div>
                </article>
              );
            })}
          </div>
        </div>

        <aside className="h-fit rounded-[28px] border border-white/10 bg-black/35 p-6 shadow-[0_28px_90px_-60px_rgba(126,58,242,0.9)] lg:sticky lg:top-6">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
            Experience state
          </p>
          <div className="mt-5 rounded-2xl border border-[#C9A24A]/20 bg-[#C9A24A]/10 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-white/45">Current</p>
            <p className="mt-2 text-3xl font-black uppercase text-white">
              {transition.state.replaceAll("_", " ")}
            </p>
            <p className="mt-3 text-sm leading-6 text-white/62">{transition.guidance}</p>
          </div>

          <div className="mt-5 grid gap-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                Lee-Wuh reaction
              </p>
              <p className="mt-2 text-sm leading-6 text-white/70">
                {transition.leeWuhReaction}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                Next action
              </p>
              <p className="mt-2 text-sm leading-6 text-[#E9C77B]">
                {transition.nextAction}
              </p>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-2">
            {demoEvents.map((item) => (
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

          <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                  Active mission
                </p>
                <h3 className="mt-2 text-xl font-semibold text-white">
                  {activeMission?.title ?? "All starter missions complete"}
                </h3>
              </div>
              <span className="rounded-full border border-[#C9A24A]/25 bg-[#C9A24A]/10 px-3 py-1 text-xs font-bold text-[#E9C77B]">
                {completedXp} XP
              </span>
            </div>

            {activeMission ? (
              <p className="mt-3 text-sm leading-6 text-white/60">
                {activeMission.description}
              </p>
            ) : null}

            <div className="mt-5 space-y-2">
              {completedMissions.length ? (
                completedMissions.map((mission) => (
                  <div
                    key={mission.id}
                    className="rounded-xl border border-[#C9A24A]/20 bg-black/25 px-3 py-2 text-sm text-white/68"
                  >
                    {mission.title}: {mission.reward.xp} XP, {mission.reward.label}
                  </div>
                ))
              ) : (
                <p className="text-sm leading-6 text-white/45">
                  No missions completed in this local demo state.
                </p>
              )}
            </div>
          </section>
        </aside>
      </div>
    </section>
  );
}
