/**
 * Signal Sprint Mock Game API
 * Phase 1: Frontend demo with mock rewards
 * NO REAL BITCOIN PAYOUTS - Demo sats only
 */

import type {
  SignalSprintPlayerProfile,
  SignalSprintReward,
  SignalSprintSessionCompleteRequest,
  SignalSprintSessionStart,
  Realm,
} from "./types";

// Lee-Wuh's judgment lines based on performance
const LEE_WUH_JUDGMENTS = {
  perfect: [
    "Now you create.",
    "You have seen the signal.",
    "The realm opens to you.",
    "You are becoming.",
  ],
  high: [
    "You are beginning to see.",
    "The signal grows stronger.",
    "Focus. The noise fades.",
    "You walk the path.",
  ],
  medium: [
    "The signal is there. Find it.",
    "Noise still clouds your vision.",
    "Try again. The realm waits.",
    "You chase fragments. Seek the whole.",
  ],
  low: [
    "You chase noise.",
    "The signal eludes you.",
    "Static consumes your focus.",
    "Return when you are ready.",
  ],
};

function getLeeWuhJudgment(performanceScore: number): string {
  if (performanceScore >= 0.9) {
    return LEE_WUH_JUDGMENTS.perfect[Math.floor(Math.random() * LEE_WUH_JUDGMENTS.perfect.length)];
  } else if (performanceScore >= 0.7) {
    return LEE_WUH_JUDGMENTS.high[Math.floor(Math.random() * LEE_WUH_JUDGMENTS.high.length)];
  } else if (performanceScore >= 0.4) {
    return LEE_WUH_JUDGMENTS.medium[Math.floor(Math.random() * LEE_WUH_JUDGMENTS.medium.length)];
  } else {
    return LEE_WUH_JUDGMENTS.low[Math.floor(Math.random() * LEE_WUH_JUDGMENTS.low.length)];
  }
}

function calculateRealm(ascension: number): Realm {
  if (ascension >= 2000) return "Creator Overlord";
  if (ascension >= 1500) return "Realm Builder";
  if (ascension >= 1000) return "Architect of Flow";
  if (ascension >= 500) return "Breaker of Noise";
  return "Initiate of Signal";
}

// Mock player state — Lee-Wuh System (in-memory for demo)
let mockProfile: SignalSprintPlayerProfile = {
  playerId: "demo-player",
  realm: "Initiate of Signal",
  realmLevel: 1,
  ascension: 0,
  signalFragments: 0,
  compressedSignal: 0,
  withdrawableSignal: 0,
  dailyRuns: 0,
  dailyFragmentsEarned: 0,
  dailyCompressedEarned: 0,
  flowStreak: 1,
};

/**
 * Start a new game session
 * Returns session metadata from server
 */
export async function startSignalSprintSession(): Promise<SignalSprintSessionStart> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 100));

  return {
    sessionId: crypto.randomUUID(),
    startedAt: new Date().toISOString(),
    difficultyLevel: Math.max(1, mockProfile.realmLevel),
    serverSeed: crypto.randomUUID(),
  };
}

/**
 * Get current player profile
 */
export async function getSignalSprintProfile(): Promise<SignalSprintPlayerProfile> {
  await new Promise((resolve) => setTimeout(resolve, 50));
  return { ...mockProfile };
}

/**
 * Complete a session and calculate rewards
 * Server-side validation ensures fair rewards
 */
export async function completeSignalSprintSession(
  request: SignalSprintSessionCompleteRequest,
): Promise<{ reward: SignalSprintReward; profile: SignalSprintPlayerProfile }> {
  await new Promise((resolve) => setTimeout(resolve, 200));

  // Calculate max expected score based on realm level
  const maxExpectedScore = 2500 + mockProfile.realmLevel * 250;

  // Performance score (0-1)
  const performanceScore = Math.max(0, Math.min(request.score / maxExpectedScore, 1));

  // Multipliers — Lee-Wuh System
  const flowMultiplier = 1 + Math.min(request.maxStreak / 100, 0.5);
  const difficultyMultiplier = 1 + mockProfile.realmLevel * 0.03;
  const dailyDecay = Math.max(0.25, 1 - mockProfile.dailyRuns * 0.12);

  // Anti-abuse checks
  const impossibleDuration = request.durationMs < 30000;
  const impossibleScore = request.score > maxExpectedScore * 1.5;
  const dailyFragmentCap = mockProfile.dailyFragmentsEarned >= 1500;
  const dailyCompressedCap = mockProfile.dailyCompressedEarned >= 10;

  // Determine eligibility
  let rewardEligible = true;
  let reason: string | undefined;

  if (impossibleDuration) {
    rewardEligible = false;
    reason = "Too fast. The realm rejects haste.";
  } else if (impossibleScore) {
    rewardEligible = false;
    reason = "Signal corrupted. Invalid performance.";
  } else if (dailyFragmentCap) {
    rewardEligible = false;
    reason = "Daily fragment limit reached. Return tomorrow.";
  } else if (dailyCompressedCap) {
    rewardEligible = false;
    reason = "Compressed signal capacity reached.";
  }

  // Lee-Wuh's judgment
  const judgment = getLeeWuhJudgment(performanceScore);

  // Calculate Signal rewards (Lee-Wuh System)
  const baseFragments = 100;
  const rawFragments = Math.floor(
    baseFragments * performanceScore * flowMultiplier * difficultyMultiplier * dailyDecay,
  );

  const remainingDailyFragments = Math.max(0, 1500 - mockProfile.dailyFragmentsEarned);
  const fragmentsEarned = rewardEligible
    ? Math.min(rawFragments, 250, remainingDailyFragments)
    : 0;

  const remainingDailyCompressed = Math.max(0, 10 - mockProfile.dailyCompressedEarned);
  const compressedEarned = rewardEligible
    ? Math.min(Math.floor(fragmentsEarned * 0.001), 1, remainingDailyCompressed)
    : 0;

  // Ascension always earned (even if rewards blocked)
  const ascensionEarned = Math.max(5, Math.floor(request.score / 100));

  // Update profile — Lee-Wuh System
  const newAscension = mockProfile.ascension + ascensionEarned;
  mockProfile = {
    ...mockProfile,
    ascension: newAscension,
    realm: calculateRealm(newAscension),
    realmLevel: Math.floor(newAscension / 500) + 1,
    signalFragments: mockProfile.signalFragments + fragmentsEarned,
    compressedSignal: mockProfile.compressedSignal + compressedEarned,
    dailyRuns: mockProfile.dailyRuns + 1,
    dailyFragmentsEarned: mockProfile.dailyFragmentsEarned + fragmentsEarned,
    dailyCompressedEarned: mockProfile.dailyCompressedEarned + compressedEarned,
  };

  return {
    reward: {
      ascensionEarned,
      fragmentsEarned,
      compressedEarned,
      withdrawableEarned: 0, // NEVER in demo mode
      rewardEligible,
      judgment,
      reason,
    },
    profile: { ...mockProfile },
  };
}

/**
 * Reset demo profile (for testing)
 */
export function resetMockProfile(): void {
  mockProfile = {
    playerId: "demo-player",
    realm: "Initiate of Signal",
    realmLevel: 1,
    ascension: 0,
    signalFragments: 0,
    compressedSignal: 0,
    withdrawableSignal: 0,
    dailyRuns: 0,
    dailyFragmentsEarned: 0,
    dailyCompressedEarned: 0,
    flowStreak: 1,
  };
}

/**
 * Check if rewards system is in demo mode
 */
export function isDemoMode(): boolean {
  return true; // Phase 1: Always demo mode
}
