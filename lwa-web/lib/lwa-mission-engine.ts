import type { LwaExperienceEvent, LwaExperienceReward } from "./lwa-experience-state";

export type LwaMissionStatus = "active" | "completed";

export type LwaMission = {
  id: string;
  title: string;
  triggerEvents: LwaExperienceEvent[];
  description: string;
  reward: LwaExperienceReward;
  status: LwaMissionStatus;
  completedAt?: string;
};

const starterMissions: LwaMission[] = [
  {
    id: "first-signal",
    title: "First Signal",
    triggerEvents: ["CLIPS_RENDERED"],
    description: "Generate a ranked rendered clip pack.",
    reward: { xp: 100, label: "Signal Spark relic" },
    status: "active",
  },
  {
    id: "proof-builder",
    title: "Proof Builder",
    triggerEvents: ["EXPORT_PACKAGE_COPIED", "PROOF_SAVED"],
    description: "Copy an export package or save proof from a useful result.",
    reward: { xp: 75, label: "Proof Mark badge" },
    status: "active",
  },
  {
    id: "money-gate",
    title: "Money Gate",
    triggerEvents: ["MARKETPLACE_OPENED"],
    description: "Open the marketplace path after useful creator output exists.",
    reward: { xp: 50, label: "Money Gate unlocked" },
    status: "active",
  },
  {
    id: "realm-entry",
    title: "Realm Entry",
    triggerEvents: ["REALM_ENTERED"],
    description: "Enter the realm layer from a product workflow.",
    reward: { xp: 50, label: "Realm access pulse" },
    status: "active",
  },
  {
    id: "recovery-operator",
    title: "Recovery Operator",
    triggerEvents: ["RECOVERY_AVAILABLE"],
    description: "Use a recovery path when render, provider, or export output is incomplete.",
    reward: { xp: 40, label: "Operator Focus badge" },
    status: "active",
  },
];

export function getStarterMissions(): LwaMission[] {
  return starterMissions.map((mission) => ({
    ...mission,
    triggerEvents: [...mission.triggerEvents],
    reward: { ...mission.reward },
  }));
}

export function applyMissionEvent(
  missions: LwaMission[],
  event: LwaExperienceEvent,
): LwaMission[] {
  const completedAt = new Date().toISOString();

  return missions.map((mission) => {
    if (mission.status === "completed" || !mission.triggerEvents.includes(event)) {
      return mission;
    }

    return {
      ...mission,
      status: "completed",
      completedAt,
    };
  });
}

export function getCompletedMissions(missions: LwaMission[]): LwaMission[] {
  return missions.filter((mission) => mission.status === "completed");
}

export function getActiveMission(missions: LwaMission[]): LwaMission | null {
  return missions.find((mission) => mission.status === "active") ?? null;
}
