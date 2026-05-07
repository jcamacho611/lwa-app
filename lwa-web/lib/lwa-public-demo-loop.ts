export type LwaPublicDemoStageId =
  | "landing"
  | "first_mission"
  | "source_added"
  | "clips_ready"
  | "recovery_available"
  | "proof_saved"
  | "signal_sprint"
  | "marketplace_teaser"
  | "return_loop";

export type LwaPublicDemoPersonaId =
  | "creator_beginner"
  | "creator_operator"
  | "brand_buyer"
  | "investor_demo";

export type LwaPublicDemoStatus = "live" | "local_demo" | "placeholder" | "disabled";

export type LwaPublicDemoStage = {
  id: LwaPublicDemoStageId;
  title: string;
  leeWuhLine: string;
  userSees: string;
  userAction: string;
  engineConnection: string;
  demoStatus: LwaPublicDemoStatus;
  nextStageId: LwaPublicDemoStageId | null;
};

export type LwaPublicDemoPersona = {
  id: LwaPublicDemoPersonaId;
  title: string;
  summary: string;
  focus: string;
};

export type LwaSignalSprintChoice = {
  id: string;
  label: string;
  kind: "hook" | "caption" | "platform";
  score: number;
  explanation: string;
};

export type LwaSignalSprintPrompt = {
  id: string;
  scenario: string;
  leeWuhLine: string;
  choices: LwaSignalSprintChoice[];
  correctChoiceId: string;
  xpReward: number;
  relicReward: string;
};

export type LwaDemoReadinessCheck = {
  id: string;
  label: string;
  status: "pass" | "blocker";
  note: string;
};

export const lwaPublicDemoStages: LwaPublicDemoStage[] = [
  {
    id: "landing",
    title: "Landing",
    leeWuhLine: "I’ll show you the loop first.",
    userSees: "Lee-Wuh, a source-first promise, and a path into clips.",
    userAction: "Open the demo and read the mission.",
    engineConnection: "Connects to the experience state engine and mission orchestration.",
    demoStatus: "live",
    nextStageId: "first_mission",
  },
  {
    id: "first_mission",
    title: "First Mission",
    leeWuhLine: "Your first mission is simple: bring me a source.",
    userSees: "A clear first action and a mission card.",
    userAction: "Start with source input or a public demo flow.",
    engineConnection: "Connects to mission selection and source ingest.",
    demoStatus: "live",
    nextStageId: "source_added",
  },
  {
    id: "source_added",
    title: "Source Added",
    leeWuhLine: "Good. Now the ranking engine can think.",
    userSees: "Source acceptance, preview context, and next-step guidance.",
    userAction: "Trigger generate / review the ranked clips.",
    engineConnection: "Connects to generate, attention scoring, and event bridge.",
    demoStatus: "live",
    nextStageId: "clips_ready",
  },
  {
    id: "clips_ready",
    title: "Clips Ready",
    leeWuhLine: "The best clip rises to the top.",
    userSees: "Ranked clips, hooks, captions, and proof-ready output.",
    userAction: "Pick the best clip and move toward export or proof.",
    engineConnection: "Connects to ranking, render proof, and export bundle.",
    demoStatus: "local_demo",
    nextStageId: "recovery_available",
  },
  {
    id: "recovery_available",
    title: "Recovery Available",
    leeWuhLine: "If render fails, strategy still survives.",
    userSees: "Strategy-only fallback and recovery options.",
    userAction: "Choose recovery, re-render, or export the strategy package.",
    engineConnection: "Connects to recovery engine and render fallback logic.",
    demoStatus: "local_demo",
    nextStageId: "proof_saved",
  },
  {
    id: "proof_saved",
    title: "Proof Saved",
    leeWuhLine: "Proof makes the run count.",
    userSees: "Saved proof, history, and progression feedback.",
    userAction: "Lock the run and claim the proof reward.",
    engineConnection: "Connects to proof history and reward ledger.",
    demoStatus: "local_demo",
    nextStageId: "signal_sprint",
  },
  {
    id: "signal_sprint",
    title: "Signal Sprint",
    leeWuhLine: "Now prove you can choose the strongest move.",
    userSees: "A fast game layer with one best decision.",
    userAction: "Pick the best hook, caption, or platform choice.",
    engineConnection: "Connects to the game engine and score feedback.",
    demoStatus: "local_demo",
    nextStageId: "marketplace_teaser",
  },
  {
    id: "marketplace_teaser",
    title: "Marketplace Teaser",
    leeWuhLine: "Money paths open after the work is real.",
    userSees: "A marketplace path preview without money claims.",
    userAction: "Review the path, not a fake payout promise.",
    engineConnection: "Connects to marketplace gating and entitlements.",
    demoStatus: "placeholder",
    nextStageId: "return_loop",
  },
  {
    id: "return_loop",
    title: "Return Loop",
    leeWuhLine: "You can come back with another source.",
    userSees: "A clean end state and a next-session promise.",
    userAction: "Return to generate, proof, or another demo run.",
    engineConnection: "Connects back into the source-first product loop.",
    demoStatus: "live",
    nextStageId: null,
  },
];

export const lwaPublicDemoPersonas: LwaPublicDemoPersona[] = [
  {
    id: "creator_beginner",
    title: "Creator Beginner",
    summary: "Needs the loop explained with almost no jargon.",
    focus: "Show source -> clip -> proof -> next mission.",
  },
  {
    id: "creator_operator",
    title: "Creator Operator",
    summary: "Cares about throughput, ranking, and repeatability.",
    focus: "Show how the engine ranks clips and keeps momentum.",
  },
  {
    id: "brand_buyer",
    title: "Brand Buyer",
    summary: "Needs campaign readiness and proof clarity.",
    focus: "Show ranked output, proof, and marketplace path.",
  },
  {
    id: "investor_demo",
    title: "Investor Demo",
    summary: "Needs the product loop and platform thesis fast.",
    focus: "Show the living system, not isolated features.",
  },
];

export const lwaSignalSprintDemoChoices: LwaSignalSprintPrompt[] = [
  {
    id: "hook-choice",
    scenario: "A creator clip opens with a strong quote, a clear promise, and a fast visual beat. What should lead?",
    leeWuhLine: "Lead with the strongest hook, not the loudest label.",
    choices: [
      {
        id: "hook",
        label: "Lead with the quote that changes the frame",
        kind: "hook",
        score: 96,
        explanation: "Best retention move. It creates a curiosity gap in the first beat.",
      },
      {
        id: "caption",
        label: "Lead with a long explanatory caption",
        kind: "caption",
        score: 42,
        explanation: "Too much setup before the viewer understands the point.",
      },
      {
        id: "platform",
        label: "Lead with the platform tag",
        kind: "platform",
        score: 35,
        explanation: "Platform labels do not earn attention by themselves.",
      },
    ],
    correctChoiceId: "hook",
    xpReward: 120,
    relicReward: "Signal Spark",
  },
  {
    id: "caption-choice",
    scenario: "The clip already has the best hook. What should the next move be?",
    leeWuhLine: "Make the caption support the hook, not fight it.",
    choices: [
      {
        id: "hook",
        label: "Repeat the hook in shorter form",
        kind: "hook",
        score: 88,
        explanation: "Reinforces the opening and keeps the idea sticky.",
      },
      {
        id: "caption",
        label: "Use a clean caption that mirrors the promise",
        kind: "caption",
        score: 97,
        explanation: "Best move. It supports clarity and does not dilute the hook.",
      },
      {
        id: "platform",
        label: "Focus on platform hashtags first",
        kind: "platform",
        score: 40,
        explanation: "Distribution is useful, but the clip still needs a readable frame.",
      },
    ],
    correctChoiceId: "caption",
    xpReward: 90,
    relicReward: "Caption Mark",
  },
  {
    id: "platform-choice",
    scenario: "The clip is strong and the caption is clean. Which platform decision is most useful?",
    leeWuhLine: "Choose the lane that fits the signal.",
    choices: [
      {
        id: "hook",
        label: "Rewrite the hook again",
        kind: "hook",
        score: 44,
        explanation: "Unnecessary churn if the hook already tests well.",
      },
      {
        id: "caption",
        label: "Keep the caption steady and ship the result",
        kind: "caption",
        score: 71,
        explanation: "Good if the platform fit is already solid.",
      },
      {
        id: "platform",
        label: "Pick the strongest platform fit for this clip",
        kind: "platform",
        score: 98,
        explanation: "Best move. Platform fit matters after hook and caption are stable.",
      },
    ],
    correctChoiceId: "platform",
    xpReward: 110,
    relicReward: "Realm Key",
  },
];

export const lwaDemoReadinessChecks: LwaDemoReadinessCheck[] = [
  { id: "first-impression", label: "First impression is obvious", status: "pass", note: "The loop explains itself quickly." },
  { id: "lee-wuh-clarity", label: "Lee-Wuh is the guide", status: "pass", note: "The guide owns the next step." },
  { id: "source-flow", label: "One-source flow is visible", status: "pass", note: "Source to clips to proof remains the spine." },
  { id: "proof-clarity", label: "Rendered proof vs strategy-only is distinct", status: "pass", note: "Fallback is honest and visible." },
  { id: "recovery", label: "Recovery state is present", status: "pass", note: "Failure still produces a useful path." },
  { id: "export-cta", label: "Export / proof CTA exists", status: "pass", note: "The visitor can see the next action." },
  { id: "marketplace", label: "Marketplace is teaser-only", status: "blocker", note: "Do not imply real payouts or campaign access yet." },
  { id: "game-loop", label: "Game loop is understandable", status: "pass", note: "Signal Sprint adds a productive game layer." },
  { id: "mobile", label: "Mobile sanity", status: "pass", note: "The route must stay readable on small screens." },
  { id: "safety", label: "Safety / compliance clear", status: "pass", note: "No payouts, crypto, or auto-posting claims." },
];

export function getPublicDemoStageById(id: LwaPublicDemoStageId): LwaPublicDemoStage {
  return lwaPublicDemoStages.find((stage) => stage.id === id) ?? lwaPublicDemoStages[0];
}

export function getNextPublicDemoStage(id: LwaPublicDemoStageId): LwaPublicDemoStage | null {
  const index = lwaPublicDemoStages.findIndex((stage) => stage.id === id);
  if (index < 0) return lwaPublicDemoStages[0];
  return lwaPublicDemoStages[index + 1] ?? null;
}

export function getSignalSprintChoiceById(id: string): LwaSignalSprintChoice | null {
  for (const prompt of lwaSignalSprintDemoChoices) {
    const choice = prompt.choices.find((item) => item.id === id);
    if (choice) return choice;
  }
  return null;
}

export function getBlockingDemoChecks(): LwaDemoReadinessCheck[] {
  return lwaDemoReadinessChecks.filter((check) => check.status === "blocker");
}

export function getDemoNarrativeForPersona(personaId: LwaPublicDemoPersonaId): string {
  switch (personaId) {
    case "creator_beginner":
      return "Show the source-first loop, the guide, and the next action in plain language.";
    case "creator_operator":
      return "Show ranking, proof, recovery, and repeatability.";
    case "brand_buyer":
      return "Show proof, clip quality, and a clear teaser toward marketplace readiness.";
    case "investor_demo":
      return "Show the product as a living operating system: source, ranking, proof, game, and return loop.";
    default:
      return "Show the source-first creator loop.";
  }
}
