# LWA BITCOIN-REWARD GAME COUNCIL — REPO PACK

**Purpose:** Source-of-truth council prompt, first playable game design, MVP spec, technical architecture, economy model, hiring order, and implementation prompts for LWA’s Bitcoin-reward game layer.

---

## Safety Position

LWA must not emulate specific real people, pretend to be specific individuals, or claim access to anyone’s private thoughts. The company uses role-locked expert cognition: clear expert domains, fixed responsibilities, strict output structure, and execution-grade review.

This council exists to make company decisions sharper, not to create a novelty chatbot.

---

## Council System Prompt

```text
You are the LWA Council — a role-locked, execution-grade decision system composed of elite expert domains required to build a global-scale game platform that distributes real-world value, including Bitcoin payouts, through engaging gameplay.

You are not a creative assistant. You are a systems-level operator.

CORE MANDATE
Design and guide the development of a high-retention, mobile-first game where:
- gameplay is genuinely fun and independent of crypto concepts
- real value is generated in the background through mining-backed or revenue-backed systems
- users are rewarded with real payouts, including Bitcoin where legally and economically appropriate
- the system is economically sustainable and resistant to abuse
- the system integrates with LWA’s AI content engine

HARD CONSTRAINTS
1. No hidden device resource usage.
2. No unsustainable reward systems.
3. No “fun later” design — fun must exist at MVP.
4. Must be buildable by a small team initially.
5. Must scale to millions without redesign.
6. Must preserve user trust.
7. Must be legally and platform-policy aware.
8. Must not depend on user-device Bitcoin mining.

LOCKED ROLES
1. Game Design Architect
2. Gameplay Systems Designer
3. Game Economist
4. Bitcoin / Payments Architect
5. Backend / Distributed Systems Architect
6. LWA AI Integration Architect
7. Product & UX Architect
8. Growth & Retention Strategist

MANDATORY RESPONSE STRUCTURE
1. Problem Definition
2. Role Outputs
3. Unified System Design
4. Gameplay Loop
5. Reward Model
6. Technical Architecture
7. MVP Plan
8. Failure Modes

OPERATING RULES
- No vague language.
- Make decisions.
- Optimize for real-world execution.
- Assume this will be implemented.
- Never claim to be a specific real person.
- Never simulate private opinions of real people.
- Think in role-locked expert patterns only.
```

---

## Primary Council Commands

```text
Design the first playable version of the LWA game that rewards users with Bitcoin. It must be fun without rewards, mobile-first, and testable within 30 days. Use the mandatory LWA Council structure.
```

```text
Design the exact reward and payout system for the LWA Bitcoin-reward game. Include formulas, anti-abuse systems, sustainability constraints, wallet assumptions, payout caps, and MVP-safe limits. Use the mandatory LWA Council structure.
```

```text
Act as a critical investor. Identify why this system fails, what would prevent funding, what legal/compliance issues exist, what unit economics are weak, and what proof points must be achieved before fundraising. Use the mandatory LWA Council structure.
```

```text
Revise the system to eliminate the investor objections while keeping the core LWA vision intact. Convert the revised plan into an implementation checklist that a small engineering team can execute. Use the mandatory LWA Council structure.
```

```text
Convert the LWA Bitcoin-reward game plan into repo tasks for jcamacho611/lwa-app. Preserve existing routes and product structure. Do not touch lwa-ios. Keep live crypto payouts disabled by default and env-gated. Add docs, types, mock wallet logic, event contracts, and a safe demo UI first. Provide exact file paths, code stubs, tests, and manual verification steps.
```

---

## First Playable Decision

Build **Signal Sprint** first.

**Signal Sprint** is a fast mobile arcade game where players dodge Noise, collect Signal, and build streaks to earn LWA credits that can later convert into Bitcoin rewards.

This is the correct MVP because it is playable in browser with React/Next.js, mobile-first, skill-based, fast to prototype, independent of crypto concepts, easy to instrument, and aligned with LWA’s signal-vs-noise brand language.

---

## Gameplay Loop

1. User enters LWA.
2. User selects **Play Signal Sprint**.
3. Lee-Wuh gives a 10-second tutorial.
4. User plays a 60-second run.
5. User collects Signal and dodges Noise.
6. Game ends with score, streak, and rank progress.
7. Backend validates session.
8. Reward Engine calculates XP, Coins, and demo sats.
9. User sees reward screen.
10. User chooses Play Again, Claim Daily Mission, Open Command Center, or Generate Clip with LWA.
11. User returns tomorrow for streak and mission rewards.

---

## Reward Model

```text
score = raw game score
max_expected_score = expected score ceiling for rank/difficulty
performance_score = clamp(score / max_expected_score, 0, 1)
streak_multiplier = 1 + min(max_streak / 100, 0.5)
difficulty_multiplier = 1 + (difficulty_level * 0.03)
daily_decay = max(0.25, 1 - (eligible_sessions_today * 0.12))
fraud_multiplier = 0 if fraud_flagged else 1
reward_pool_multiplier = daily_reward_pool_remaining / daily_reward_pool_start
```

```text
coins_earned = floor(
  base_coins
  * performance_score
  * streak_multiplier
  * difficulty_multiplier
  * daily_decay
  * fraud_multiplier
)
```

Recommended MVP values:

```text
base_coins = 100
max_coins_per_session = 250
max_coins_per_day = 1500
sat_conversion_rate = 0.001
max_demo_sats_per_session = 1
max_demo_sats_per_day = 10
withdrawals_enabled = false
```

Production guardrail:

```text
total_real_payouts_today <= min(
  daily_reward_budget,
  verified_revenue_today * payout_ratio
)
```

---

## Anti-Abuse Rules

A session becomes reward-ineligible when:

- duration is below minimum possible completion time
- score exceeds physics-based ceiling
- input pattern is bot-like
- repeated identical sessions occur
- device/account/wallet cluster is suspicious
- session submission is duplicated
- app version is unsupported
- user exceeds daily reward cap

Fraud-flagged sessions may still earn non-withdrawable XP to avoid revealing detection rules immediately.

---

## Repo File Plan

Documentation:

```text
docs/game/LWA_BITCOIN_REWARD_GAME_COUNCIL.md
docs/game/SIGNAL_SPRINT_MVP_SPEC.md
docs/game/SIGNAL_SPRINT_ECONOMY.md
docs/game/SIGNAL_SPRINT_TECHNICAL_ARCHITECTURE.md
docs/prompts/LWA_COUNCIL_EXECUTION_PROMPT.md
```

Frontend:

```text
lwa-web/app/game/page.tsx
lwa-web/components/game/SignalSprintGame.tsx
lwa-web/components/game/SignalSprintHud.tsx
lwa-web/components/game/SignalSprintResults.tsx
lwa-web/components/game/RewardWalletPanel.tsx
lwa-web/lib/game/types.ts
lwa-web/lib/game/mockGameApi.ts
```

Backend:

```text
backend/app/game/models.py
backend/app/game/reward_engine.py
backend/app/game/fraud_rules.py
backend/app/game/routes.py
backend/app/game/ledger.py
backend/app/game/settings.py
backend/tests/test_reward_engine.py
backend/tests/test_fraud_rules.py
```

Adapt backend paths to the actual repo structure.

---

## Phase 1 Execution Rule

Phase 1 is documentation plus safe frontend demo only.

Do not start with:

- real Bitcoin payouts
- full multiplayer
- crypto wallet onboarding
- NFTs
- marketplace
- mining infrastructure
- creator raids
- VR worlds

Start with:

- one fun game loop
- one mock wallet
- one reward screen
- one `/game` route
- one testable MVP

The company-level thesis:

**LWA turns play, creativity, and attention into measurable value. Signal Sprint is the first playable proof.**
