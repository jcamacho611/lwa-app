/**
 * LWA Public Demo Loop — typed data + helpers.
 *
 * Pure local data module. No fetch, no backend, no auth, no payments.
 * Safe to import from any client component.
 *
 * Companion spec: docs/demo/LWA_PUBLIC_DEMO_LOOP_SPEC.md
 */

// ---------- IDs and unions ----------

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

export type LwaPublicDemoStatus =
  | "live"
  | "local_demo"
  | "placeholder"
  | "disabled"
  | "blocking";

export type LwaPublicDemoPersonaId =
  | "creator_beginner"
  | "creator_operator"
  | "brand_buyer"
  | "investor_demo";

// ---------- Core types ----------

export type LwaPublicDemoAction = {
  /** Short verb shown on the Next Stage button. */
  label: string;
  /** Explanation of what this click represents in the real product. */
  meaning: string;
};

export type LwaPublicDemoStage = {
  id: LwaPublicDemoStageId;
  /** 1-3 word stage title. */
  title: string;
  /** 6-14 word Lee-Wuh judgment line in voice. */
  leeWuhLine: string;
  /** What the user sees on screen at this stage. */
  userSees: string;
  /** What the user is invited to do. */
  userAction: LwaPublicDemoAction;
  /** Named engine this stage will eventually delegate to. */
  engineConnection: string;
  /** Demo readiness state for this stage. */
  demoStatus: LwaPublicDemoStatus;
  /** Why this stage exists in the loop. */
  rationale: string;
  /** Next stage id, or null at the end. */
  nextStageId: LwaPublicDemoStageId | null;
};

export type LwaPublicDemoPersona = {
  id: LwaPublicDemoPersonaId;
  label: string;
  /** One-sentence framing of what this visitor is here to evaluate. */
  framing: string;
  /** Stage ids this persona should pay attention to. */
  emphasisStageIds: LwaPublicDemoStageId[];
  /** Tone Lee-Wuh adopts for this persona. */
  tone: "encouraging" | "operational" | "procurement" | "calm_exact";
};

export type LwaPublicDemoSignalSprintChoice = {
  id: string;
  /** Short label shown on a lane button. */
  label: string;
  /** Lee-Wuh's reaction line if this choice is picked. */
  reaction: string;
};

export type LwaPublicDemoSignalSprintPrompt = {
  id: string;
  /** Scenario the creator is reacting to. */
  scenario: string;
  /** Skill tested by this prompt. */
  skill: "hook" | "caption" | "platform";
  /** 3 lane choices. */
  choices: [
    LwaPublicDemoSignalSprintChoice,
    LwaPublicDemoSignalSprintChoice,
    LwaPublicDemoSignalSprintChoice,
  ];
  correctChoiceId: string;
  /** Why the correct choice is correct. */
  explanation: string;
  xpReward: number;
  relicReward: string;
};

export type LwaPublicDemoReadinessCheck = {
  id: string;
  label: string;
  status: LwaPublicDemoStatus;
  /** What this check is asserting. */
  assertion: string;
};

// ---------- Stage data ----------

export const lwaPublicDemoStages: readonly LwaPublicDemoStage[] = [
  {
    id: "landing",
    title: "Landing",
    leeWuhLine: "You arrived. The realm is quiet. Begin when ready.",
    userSees: "Lee-Wuh appears in a black-gold space with one line of text and one button.",
    userAction: {
      label: "Begin",
      meaning: "Enter the loop. No login. No backend call.",
    },
    engineConnection: "lib/lee-wuh-asset-registry.ts (visual identity surface)",
    demoStatus: "live",
    rationale: "First impression must be calm, branded, and unambiguous about what to do next.",
    nextStageId: "first_mission",
  },
  {
    id: "first_mission",
    title: "First Mission",
    leeWuhLine: "One source. That is the entire ask. Bring it.",
    userSees: "A single mission card: \"Add one source.\" No menu, no upsell.",
    userAction: {
      label: "Add a Source",
      meaning: "Demo simulation of the upload surface. No file is uploaded.",
    },
    engineConnection: "lib/lwa-mission-engine.ts (mission issuance)",
    demoStatus: "live",
    rationale: "Reduce the first action to one verb so visitors do not bounce.",
    nextStageId: "source_added",
  },
  {
    id: "source_added",
    title: "Source Added",
    leeWuhLine: "Source registered. The system listens now.",
    userSees: "The source row appears with a quiet gold pulse. Status: ingested.",
    userAction: {
      label: "Generate Clips",
      meaning: "Demo placeholder. The real product calls /generate; the demo does not.",
    },
    engineConnection: "lib/source-contract (read-only display)",
    demoStatus: "local_demo",
    rationale: "Show that the system acknowledges work without surfacing latency or errors.",
    nextStageId: "clips_ready",
  },
  {
    id: "clips_ready",
    title: "Clips Ready",
    leeWuhLine: "Three clips. One rendered. Two as strategy. Read them.",
    userSees: "A ranked clip stack: one rendered preview, two strategy-only cards with reasons.",
    userAction: {
      label: "Open the Top Clip",
      meaning: "Visitors learn rendered vs. strategy-only is a feature, not a failure.",
    },
    engineConnection: "lib/clip-studio-event-bridge.ts (event read-only)",
    demoStatus: "placeholder",
    rationale: "Make the rendered/strategy split legible at first glance — this is the product's differentiator.",
    nextStageId: "recovery_available",
  },
  {
    id: "recovery_available",
    title: "Recovery Available",
    leeWuhLine: "Strategy clips have a path back to a render. Take it when ready.",
    userSees: "A strategy-only clip exposes a Recovery button with a one-line explanation.",
    userAction: {
      label: "Show Recovery",
      meaning: "Demo reveals the recovery surface so visitors trust strategy-only output.",
    },
    engineConnection: "lib/lwa-recovery-engine.ts (recovery surface)",
    demoStatus: "placeholder",
    rationale: "Recovery converts a perceived failure into a feature; trust is built here.",
    nextStageId: "proof_saved",
  },
  {
    id: "proof_saved",
    title: "Proof Saved",
    leeWuhLine: "What you keep, you can show. Save proof, not promises.",
    userSees: "One clip is marked as proof. A small ledger entry appears with a timestamp.",
    userAction: {
      label: "Save as Proof",
      meaning: "Demo writes nothing. It only renders the proof card visual.",
    },
    engineConnection: "lib/proof-engine.ts + lib/lwa-event-bridge.ts (event emit, demo only)",
    demoStatus: "placeholder",
    rationale: "Visitors leave the loop with something they could screenshot — proof is the souvenir.",
    nextStageId: "signal_sprint",
  },
  {
    id: "signal_sprint",
    title: "Signal Sprint",
    leeWuhLine: "Choose the lane that earns attention. Three seconds. Decide.",
    userSees: "A scenario, three lane choices, a small countdown. One round, deterministic.",
    userAction: {
      label: "Run a Sprint",
      meaning: "Local-only creator skill prompt. No backend, no scoring service.",
    },
    engineConnection: "Signal Sprint decision variant (local only)",
    demoStatus: "local_demo",
    rationale: "Prove the game layer is creator-skill, not random reflex. Reframes the product as practice.",
    nextStageId: "marketplace_teaser",
  },
  {
    id: "marketplace_teaser",
    title: "Marketplace Teaser",
    leeWuhLine: "There is a market. It opens later. Earn the right.",
    userSees: "A locked card naming the marketplace. No button to open it. No prices.",
    userAction: {
      label: "Continue",
      meaning: "Marketplace is named, not opened. No claims about earnings or splits.",
    },
    engineConnection: "lib/marketplace-engine.ts (named, not invoked)",
    demoStatus: "disabled",
    rationale: "Create future pull without making revenue claims that would invite legal review.",
    nextStageId: "return_loop",
  },
  {
    id: "return_loop",
    title: "Return Loop",
    leeWuhLine: "You saw the loop. Come back with a real source. The realm holds.",
    userSees: "A summary card: what to do next, when to return, one quiet CTA.",
    userAction: {
      label: "Restart Demo",
      meaning: "Resets the local stage to landing. No persistence.",
    },
    engineConnection: "lib/lwa-experience-state.ts (state machine reset)",
    demoStatus: "live",
    rationale: "Close the loop with a clear next action so the visit feels finished, not abandoned.",
    nextStageId: null,
  },
] as const;

// ---------- Personas ----------

export const lwaPublicDemoPersonas: readonly LwaPublicDemoPersona[] = [
  {
    id: "creator_beginner",
    label: "Creator (beginner)",
    framing: "Wants to see if LWA can turn one source into something postable today.",
    emphasisStageIds: ["first_mission", "clips_ready", "proof_saved"],
    tone: "encouraging",
  },
  {
    id: "creator_operator",
    label: "Creator / operator",
    framing: "Already runs a clipping workflow. Wants to know what LWA does that their stack does not.",
    emphasisStageIds: ["clips_ready", "recovery_available", "proof_saved", "signal_sprint"],
    tone: "operational",
  },
  {
    id: "brand_buyer",
    label: "Brand / buyer",
    framing: "Evaluating LWA as a creator-output supplier. Cares about proof, governance, and the marketplace path.",
    emphasisStageIds: ["proof_saved", "marketplace_teaser", "return_loop"],
    tone: "procurement",
  },
  {
    id: "investor_demo",
    label: "Investor demo",
    framing: "Needs the whole nine-stage arc plus the readiness checklist in under two minutes.",
    emphasisStageIds: [
      "landing",
      "first_mission",
      "clips_ready",
      "recovery_available",
      "proof_saved",
      "signal_sprint",
      "return_loop",
    ],
    tone: "calm_exact",
  },
] as const;

// ---------- Signal Sprint decision prompts ----------

export const lwaSignalSprintDemoChoices: readonly LwaPublicDemoSignalSprintPrompt[] = [
  {
    id: "sprint_hook_01",
    scenario:
      "A 14-minute interview with a fitness coach. The strongest moment: she explains why most clients quit at week three.",
    skill: "hook",
    choices: [
      {
        id: "sprint_hook_01_a",
        label: "Most clients quit at week three. Here is why.",
        reaction: "Direct. Names the curiosity gap. Lee-Wuh approves.",
      },
      {
        id: "sprint_hook_01_b",
        label: "Welcome back to my channel, today we discuss…",
        reaction: "Soft open. The realm sleeps through this.",
      },
      {
        id: "sprint_hook_01_c",
        label: "Fitness tips you need to know — part 27.",
        reaction: "Generic. Indexable, not memorable.",
      },
    ],
    correctChoiceId: "sprint_hook_01_a",
    explanation:
      "Hooks that name a specific failure or moment outperform vague openers and channel intros on every short-form platform.",
    xpReward: 60,
    relicReward: "Hook Cutter relic",
  },
  {
    id: "sprint_caption_01",
    scenario:
      "A 38-second clip of a finance founder explaining the one mistake first-time fundraisers make in their seed deck.",
    skill: "caption",
    choices: [
      {
        id: "sprint_caption_01_a",
        label: "First-time fundraisers always make this one mistake on their seed deck.",
        reaction: "Specific. Promises a payoff. Lane chosen well.",
      },
      {
        id: "sprint_caption_01_b",
        label: "Some thoughts on fundraising from a founder.",
        reaction: "Vague. The viewer has nothing to anticipate.",
      },
      {
        id: "sprint_caption_01_c",
        label: "🔥🔥🔥 must-watch finance tips 🔥🔥🔥",
        reaction: "Emoji curtain. The realm sees through it.",
      },
    ],
    correctChoiceId: "sprint_caption_01_a",
    explanation:
      "A caption that names the audience and the payoff out-performs hashtags-as-content. The viewer needs a reason to start.",
    xpReward: 50,
    relicReward: "Caption Carver relic",
  },
  {
    id: "sprint_platform_01",
    scenario:
      "A 9-second reaction laugh from a streamer. High visual energy. No spoken line.",
    skill: "platform",
    choices: [
      {
        id: "sprint_platform_01_a",
        label: "TikTok and Reels first — 9-second visual loops.",
        reaction: "Right surface, right shape. Lee-Wuh nods.",
      },
      {
        id: "sprint_platform_01_b",
        label: "LinkedIn first — looks professional with a caption.",
        reaction: "Wrong realm. The visit is too short to land there.",
      },
      {
        id: "sprint_platform_01_c",
        label: "YouTube long-form upload as a member moment.",
        reaction: "Misuses the asset. Length punishes the loop.",
      },
    ],
    correctChoiceId: "sprint_platform_01_a",
    explanation:
      "Short, voiceless, high-energy clips are native to short-form vertical surfaces. Platform fit must match shape, not aspiration.",
    xpReward: 55,
    relicReward: "Platform Compass relic",
  },
] as const;

// ---------- Readiness checklist ----------

export const lwaPublicDemoReadinessChecks: readonly LwaPublicDemoReadinessCheck[] = [
  {
    id: "no_backend_writes",
    label: "No backend writes",
    status: "live",
    assertion: "The demo panel performs no POST/PUT/DELETE requests.",
  },
  {
    id: "no_auth",
    label: "No auth required",
    status: "live",
    assertion: "Visitors can experience the loop without sign-in.",
  },
  {
    id: "no_payments",
    label: "No payments / payouts / crypto",
    status: "live",
    assertion: "Wallet, marketplace, and crypto surfaces are disabled in this lane.",
  },
  {
    id: "no_brain_panel_import",
    label: "No Brain Panel coupling",
    status: "live",
    assertion: "Demo does not import lwa-brain-engine.ts or LwaBrainEnginePanel.tsx.",
  },
  {
    id: "lee_wuh_voice",
    label: "Lee-Wuh voice present per stage",
    status: "live",
    assertion: "Each of the 9 stages exposes a Lee-Wuh judgment line.",
  },
  {
    id: "rendered_vs_strategy_legible",
    label: "Rendered vs strategy-only legible",
    status: "local_demo",
    assertion: "clips_ready stage names the split in Lee-Wuh voice.",
  },
  {
    id: "recovery_visible",
    label: "Recovery visible as a feature",
    status: "local_demo",
    assertion: "recovery_available stage exposes a recovery affordance.",
  },
  {
    id: "signal_sprint_skill_prompt",
    label: "Signal Sprint reads as creator skill",
    status: "local_demo",
    assertion: "Decision-lane sprint emphasizes hook/caption/platform skill, not reflex.",
  },
  {
    id: "marketplace_only_named",
    label: "Marketplace named, not opened",
    status: "live",
    assertion: "marketplace_teaser stage shows a locked card with no purchase surface.",
  },
  {
    id: "real_clip_generation",
    label: "Real /generate call",
    status: "disabled",
    assertion: "The demo does not invoke /generate. The live product does.",
  },
  {
    id: "real_proof_save",
    label: "Real proof persistence",
    status: "disabled",
    assertion: "Saving proof in the demo writes nothing; it renders a card.",
  },
  {
    id: "social_posting",
    label: "Direct social posting",
    status: "disabled",
    assertion: "No demo action posts to TikTok / IG / X / YouTube / LinkedIn / Whop.",
  },
];

// ---------- Helpers ----------

export function getPublicDemoStageById(
  id: LwaPublicDemoStageId,
): LwaPublicDemoStage | undefined {
  return lwaPublicDemoStages.find((stage) => stage.id === id);
}

export function getNextPublicDemoStage(
  id: LwaPublicDemoStageId,
): LwaPublicDemoStage | undefined {
  const current = getPublicDemoStageById(id);
  if (!current || current.nextStageId === null) {
    return undefined;
  }
  return getPublicDemoStageById(current.nextStageId);
}

export function getSignalSprintChoiceById(
  id: string,
): LwaPublicDemoSignalSprintPrompt | undefined {
  return lwaSignalSprintDemoChoices.find((prompt) => prompt.id === id);
}

export function getBlockingDemoChecks(): LwaPublicDemoReadinessCheck[] {
  return lwaPublicDemoReadinessChecks.filter(
    (check) => check.status === "blocking",
  );
}

export function getDemoNarrativeForPersona(
  personaId: LwaPublicDemoPersonaId,
): {
  persona: LwaPublicDemoPersona | undefined;
  emphasisStages: LwaPublicDemoStage[];
} {
  const persona = lwaPublicDemoPersonas.find((p) => p.id === personaId);
  if (!persona) {
    return { persona: undefined, emphasisStages: [] };
  }
  const emphasisStages: LwaPublicDemoStage[] = [];
  for (const stageId of persona.emphasisStageIds) {
    const stage = getPublicDemoStageById(stageId);
    if (stage) {
      emphasisStages.push(stage);
    }
  }
  return { persona, emphasisStages };
}

/** Convenience: the canonical first stage. */
export const LWA_PUBLIC_DEMO_FIRST_STAGE_ID: LwaPublicDemoStageId = "landing";
