"use client";

import type { ClipResult, GeneratedScripts, GenerateResponse } from "./types";
import type { ReadyQueueItem } from "./queue";

export type CharacterIntent =
  | "wait"
  | "intake"
  | "analyze"
  | "lead"
  | "recover"
  | "multiply"
  | "post";

export type CharacterActionId =
  | "focus_source"
  | "review_lead"
  | "queue_lead"
  | "recover_strategy"
  | "copy_script";

export type CharacterAction = {
  id: CharacterActionId;
  label: string;
  priority: number;
};

export type CharacterMemory = {
  runsSeen: number;
  renderedSeen: number;
  strategySeen: number;
  queuedSeen: number;
  lastIntent: CharacterIntent;
  lastRequestId?: string | null;
  lastUpdated: string;
};

export type CharacterAgent = {
  id: "clipping-god" | "strategist";
  name: string;
  intent: CharacterIntent;
  mood: "dormant" | "watching" | "locked-in" | "decisive" | "expanding";
  directive: string;
  insight: string;
  focusClipId?: string | null;
  actions: CharacterAction[];
  memory: CharacterMemory;
};

export type CharacterIntelligenceInput = {
  isLoading: boolean;
  loadingStageIndex: number;
  hasSource: boolean;
  result?: GenerateResponse | null;
  orderedClips?: ClipResult[];
  renderedClips?: ClipResult[];
  strategyOnlyClips?: ClipResult[];
  readyQueue?: ReadyQueueItem[];
  recoveryActive?: boolean;
  scripts?: GeneratedScripts | null;
};

const MEMORY_KEY = "lwa-character-agent-memory-v1";

const defaultMemory: CharacterMemory = {
  runsSeen: 0,
  renderedSeen: 0,
  strategySeen: 0,
  queuedSeen: 0,
  lastIntent: "wait",
  lastRequestId: null,
  lastUpdated: "",
};

function canUseStorage() {
  return typeof window !== "undefined";
}

export function readCharacterMemory(): CharacterMemory {
  if (!canUseStorage()) {
    return defaultMemory;
  }

  try {
    return { ...defaultMemory, ...JSON.parse(window.localStorage.getItem(MEMORY_KEY) || "{}") };
  } catch {
    return defaultMemory;
  }
}

export function writeCharacterMemory(memory: CharacterMemory) {
  if (!canUseStorage()) {
    return;
  }

  window.localStorage.setItem(MEMORY_KEY, JSON.stringify(memory));
}

function chooseIntent(input: CharacterIntelligenceInput): CharacterIntent {
  if (input.recoveryActive) {
    return "recover";
  }

  if (input.isLoading) {
    if (input.loadingStageIndex <= 0) {
      return "intake";
    }
    return "analyze";
  }

  if (!input.hasSource && !input.result) {
    return "wait";
  }

  if (!input.result) {
    return "intake";
  }

  if ((input.readyQueue || []).length > 0) {
    return "post";
  }

  if ((input.strategyOnlyClips || []).length > 0 && !(input.renderedClips || []).length) {
    return "recover";
  }

  if (input.scripts?.main) {
    return "multiply";
  }

  return "lead";
}

function chooseMood(intent: CharacterIntent): CharacterAgent["mood"] {
  if (intent === "wait") return "dormant";
  if (intent === "intake") return "watching";
  if (intent === "analyze" || intent === "recover") return "locked-in";
  if (intent === "multiply") return "expanding";
  return "decisive";
}

function chooseDirective(intent: CharacterIntent, input: CharacterIntelligenceInput) {
  const lead = input.orderedClips?.[0];
  const platform = input.result?.processing_summary?.recommended_platform || input.result?.processing_summary?.target_platform || "the best feed";

  if (intent === "wait") return "Drop one source. I will call the first move.";
  if (intent === "intake") return "Source detected. Keep auto on unless this is a fixed campaign.";
  if (intent === "analyze") return "I am reading hook density, pacing, and payoff.";
  if (intent === "recover") return "Media proof is the gap. Recover the strongest strategy cut.";
  if (intent === "multiply") return "The clip stack is ready. Multiply the angle into the next script.";
  if (intent === "post") return "Queue is active. Move the ready stack next.";

  if (lead?.hook) {
    return `Post this first: ${lead.hook}`;
  }

  return `Lead cut is selected for ${platform}.`;
}

function chooseInsight(intent: CharacterIntent, input: CharacterIntelligenceInput) {
  const lead = input.orderedClips?.[0];
  const summary = input.result?.processing_summary;
  const reason = summary?.platform_recommendation_reason;

  if (intent === "wait") return "I stay quiet until there is a source to judge.";
  if (intent === "intake") return "One input is enough. The backend will recommend the destination.";
  if (intent === "analyze") return "I am waiting for real output before giving a posting call.";
  if (intent === "recover") return "Do not treat a strategy card like a finished clip.";
  if (intent === "multiply") return input.scripts?.hooks?.[0] || "A new script can extend the same winning frame.";
  if (intent === "post") return "Queued clips are now the working stack.";

  return lead?.why_this_matters || reason || lead?.thumbnail_text || "The lead clip has the clearest posting signal.";
}

function chooseActions(intent: CharacterIntent, input: CharacterIntelligenceInput): CharacterAction[] {
  const actions: CharacterAction[] = [];
  const hasLead = Boolean(input.orderedClips?.length);
  const hasStrategy = Boolean(input.strategyOnlyClips?.length);
  const hasScript = Boolean(input.scripts?.main);
  const queueCount = input.readyQueue?.length || 0;

  if (intent === "wait" || intent === "intake") {
    actions.push({ id: "focus_source", label: "Focus source", priority: 1 });
  }

  if (hasLead) {
    actions.push({ id: "review_lead", label: "Review lead", priority: 2 });
  }

  if (hasLead && queueCount === 0) {
    actions.push({ id: "queue_lead", label: "Queue lead", priority: 3 });
  }

  if (hasStrategy) {
    actions.push({ id: "recover_strategy", label: "Recover proof", priority: 4 });
  }

  if (hasScript) {
    actions.push({ id: "copy_script", label: "Copy script", priority: 5 });
  }

  return actions.sort((left, right) => left.priority - right.priority).slice(0, 3);
}

function updateMemory(input: CharacterIntelligenceInput, intent: CharacterIntent, memory: CharacterMemory): CharacterMemory {
  const requestId = input.result?.request_id || null;
  const sawNewRun = Boolean(requestId && requestId !== memory.lastRequestId);
  const renderedSeen = Math.max(memory.renderedSeen, input.renderedClips?.length || 0);
  const strategySeen = Math.max(memory.strategySeen, input.strategyOnlyClips?.length || 0);
  const queuedSeen = Math.max(memory.queuedSeen, input.readyQueue?.length || 0);
  const changed =
    sawNewRun ||
    renderedSeen !== memory.renderedSeen ||
    strategySeen !== memory.strategySeen ||
    queuedSeen !== memory.queuedSeen ||
    intent !== memory.lastIntent;

  if (!changed) {
    return memory;
  }

  return {
    runsSeen: sawNewRun ? memory.runsSeen + 1 : memory.runsSeen,
    renderedSeen,
    strategySeen,
    queuedSeen,
    lastIntent: intent,
    lastRequestId: requestId || memory.lastRequestId || null,
    lastUpdated: new Date().toISOString(),
  };
}

export function createCharacterAgent(input: CharacterIntelligenceInput, memory = readCharacterMemory()): CharacterAgent {
  const intent = chooseIntent(input);
  const nextMemory = updateMemory(input, intent, memory);
  const focusClip = input.orderedClips?.[0] || null;

  return {
    id: intent === "multiply" || intent === "post" ? "strategist" : "clipping-god",
    name: intent === "multiply" || intent === "post" ? "Strategist" : "Clipping God",
    intent,
    mood: chooseMood(intent),
    directive: chooseDirective(intent, input),
    insight: chooseInsight(intent, input),
    focusClipId: focusClip?.record_id || focusClip?.clip_id || focusClip?.id || null,
    actions: chooseActions(intent, input),
    memory: nextMemory,
  };
}
