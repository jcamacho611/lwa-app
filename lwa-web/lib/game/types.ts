/**
 * Signal Sprint Game Types
 * Following LWA Bitcoin Reward Game Council specifications
 * Phase 1: Safe demo mode only - no real payouts
 */

export type SignalSprintSessionStatus = "started" | "completed" | "rejected";

export type SignalSprintSessionStart = {
  sessionId: string;
  startedAt: string;
  difficultyLevel: number;
  serverSeed: string;
};

export type SignalSprintSessionCompleteRequest = {
  sessionId: string;
  score: number;
  durationMs: number;
  maxStreak: number;
  signalCollected: number;
  noiseHits: number;
  clientVersion: string;
  endedAt: string;
};

// Lee-Wuh System: Rewards are Signal, not generic currency
export type SignalSprintReward = {
  ascensionEarned: number;
  fragmentsEarned: number;
  compressedEarned: number;
  withdrawableEarned: number; // Always 0 in demo
  rewardEligible: boolean;
  judgment?: string; // Lee-Wuh's words
  reason?: string;
};

// Lee-Wuh System: Realms (not ranks), Ascension (not XP)
export type Realm = 
  | "Initiate of Signal"
  | "Breaker of Noise" 
  | "Architect of Flow"
  | "Realm Builder"
  | "Creator Overlord";

export type SignalSprintPlayerProfile = {
  playerId: string;
  realm: Realm;
  realmLevel: number; // 1-5
  ascension: number; // XP reframed
  signalFragments: number; // Coins reframed
  compressedSignal: number; // Demo sats reframed
  withdrawableSignal: number; // Real sats (always 0 in demo)
  dailyRuns: number;
  dailyFragmentsEarned: number;
  dailyCompressedEarned: number;
  flowStreak: number; // Days in a row
};

// Lee-Wuh System: Ledger tracks Signal, not generic currency
export type SignalSprintLedgerEntry = {
  id: string;
  playerId: string;
  sessionId: string;
  type: "ascension" | "fragment" | "compressed_signal" | "withdrawable_signal";
  amount: number;
  createdAt: string;
  status: "posted" | "rejected" | "pending_review";
  leeWuhJudgment?: string;
  reason?: string;
};

// Game state types
export type GameState = "idle" | "playing" | "paused" | "completed";

export type Lane = 0 | 1 | 2; // 3 lanes: left, center, right

export type GameObject = {
  id: string;
  lane: Lane;
  type: "signal" | "noise";
  position: number; // 0-100 (percentage of screen height)
  collected?: boolean;
};

export type GameStats = {
  score: number;
  streak: number;
  maxStreak: number;
  signalCollected: number;
  noiseHits: number;
  durationMs: number;
  startTime: number;
};
