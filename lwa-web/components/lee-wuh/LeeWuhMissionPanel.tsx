"use client";

import type { LwaMission } from "../../lib/lwa-mission-engine";

type LeeWuhMissionPanelProps = {
  activeMission: LwaMission | null;
  completedMissions: LwaMission[];
  completedXp: number;
};

function missionTriggerLabel(mission: LwaMission) {
  return mission.triggerEvents.join(" or ").replaceAll("_", " ");
}

export default function LeeWuhMissionPanel({
  activeMission,
  completedMissions,
  completedXp,
}: LeeWuhMissionPanelProps) {
  return (
    <section className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.24em] text-white/35">
            Mission orchestration
          </p>
          <h3 className="mt-2 text-2xl font-semibold text-white">
            {activeMission?.title ?? "Starter chain complete"}
          </h3>
        </div>
        <span className="rounded-full border border-[#C9A24A]/30 bg-[#C9A24A]/10 px-3 py-1 text-sm font-bold text-[#E9C77B]">
          {completedXp} XP
        </span>
      </div>

      {activeMission ? (
        <div className="mt-5 grid gap-3">
          <p className="text-sm leading-6 text-white/62">
            {activeMission.description}
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-black/25 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                Trigger
              </p>
              <p className="mt-2 text-sm font-semibold text-white/75">
                {missionTriggerLabel(activeMission)}
              </p>
            </div>
            <div className="rounded-2xl border border-[#C9A24A]/20 bg-[#C9A24A]/10 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-[#E9C77B]">
                Reward
              </p>
              <p className="mt-2 text-sm font-semibold text-white">
                {activeMission.reward.xp} XP + {activeMission.reward.label}
              </p>
            </div>
          </div>
        </div>
      ) : (
        <p className="mt-4 text-sm leading-6 text-white/58">
          Every starter mission in this local demo has been completed. Backend
          persistence and anti-abuse controls come later.
        </p>
      )}

      <div className="mt-5">
        <p className="text-xs uppercase tracking-[0.2em] text-white/35">
          Completed
        </p>
        <div className="mt-3 space-y-2">
          {completedMissions.length ? (
            completedMissions.map((mission) => (
              <div
                key={mission.id}
                className="rounded-2xl border border-[#C9A24A]/20 bg-black/25 p-3 text-sm text-white/68"
              >
                <span className="font-semibold text-white">{mission.title}</span>{" "}
                <span className="text-white/45">completed</span>
              </div>
            ))
          ) : (
            <p className="rounded-2xl border border-white/10 bg-black/20 p-3 text-sm text-white/45">
              No missions completed yet in this local controller.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

