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
} from "./types";

// Mock player state (in-memory for demo)
let mockProfile: SignalSprintPlayerProfile = {
  playerId: "demo-player",
  rank: 1,
  xp: 0,
  coins: 0,
  demoSats: 0,
  withdrawableSats: 0,
  dailySessions: 0,
  dailyCoinsEarned: 0,
  dailyDemoSatsEarned: 0,
  streakDays: 1,
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
    difficultyLevel: Math.max(1, mockProfile.rank),
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

  // Calculate max expected score based on rank
  const maxExpectedScore = 2500 + mockProfile.rank * 250;

  // Performance score (0-1)
  const performanceScore = Math.max(0, Math.min(request.score / maxExpectedScore, 1));

  // Multipliers
  const streakMultiplier = 1 + Math.min(request.maxStreak / 100, 0.5);
  const difficultyMultiplier = 1 + mockProfile.rank * 0.03;
  const dailyDecay = Math.max(0.25, 1 - mockProfile.dailySessions * 0.12);

  // Anti-abuse checks
  const impossibleDuration = request.durationMs < 30000; // Min 30s
  const impossibleScore = request.score > maxExpectedScore * 1.5;
  const dailyCoinCapReached = mockProfile.dailyCoinsEarned >= 1500;
  const dailySatCapReached = mockProfile.dailyDemoSatsEarned >= 10;

  // Determine eligibility
  let rewardEligible = true;
  let reason: string | undefined;

  if (impossibleDuration) {
    rewardEligible = false;
    reason = "Session duration below minimum threshold.";
  } else if (impossibleScore) {
    rewardEligible = false;
    reason = "Score exceeds validation ceiling.";
  } else if (dailyCoinCapReached) {
    rewardEligible = false;
    reason = "Daily coin cap reached.";
  } else if (dailySatCapReached) {
    rewardEligible = false;
    reason = "Daily demo sat cap reached.";
  }

  // Calculate rewards (only if eligible)
  const baseCoins = 100;
  const rawCoins = Math.floor(
    baseCoins * performanceScore * streakMultiplier * difficultyMultiplier * dailyDecay,
  );

  const remainingDailyCoins = Math.max(0, 1500 - mockProfile.dailyCoinsEarned);
  const coinsEarned = rewardEligible
    ? Math.min(rawCoins, 250, remainingDailyCoins)
    : 0;

  const remainingDailyDemoSats = Math.max(0, 10 - mockProfile.dailyDemoSatsEarned);
  const demoSatsEarned = rewardEligible
    ? Math.min(Math.floor(coinsEarned * 0.001), 1, remainingDailyDemoSats)
    : 0;

  // XP always earned (even if rewards blocked)
  const xpEarned = Math.max(5, Math.floor(request.score / 100));

  // Update profile
  mockProfile = {
    ...mockProfile,
    xp: mockProfile.xp + xpEarned,
    rank: Math.floor((mockProfile.xp + xpEarned) / 500) + 1,
    coins: mockProfile.coins + coinsEarned,
    demoSats: mockProfile.demoSats + demoSatsEarned,
    dailySessions: mockProfile.dailySessions + 1,
    dailyCoinsEarned: mockProfile.dailyCoinsEarned + coinsEarned,
    dailyDemoSatsEarned: mockProfile.dailyDemoSatsEarned + demoSatsEarned,
  };

  return {
    reward: {
      xpEarned,
      coinsEarned,
      demoSatsEarned,
      withdrawableSatsEarned: 0, // NEVER in demo mode
      rewardEligible,
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
    rank: 1,
    xp: 0,
    coins: 0,
    demoSats: 0,
    withdrawableSats: 0,
    dailySessions: 0,
    dailyCoinsEarned: 0,
    dailyDemoSatsEarned: 0,
    streakDays: 1,
  };
}

/**
 * Check if rewards system is in demo mode
 */
export function isDemoMode(): boolean {
  return true; // Phase 1: Always demo mode
}
