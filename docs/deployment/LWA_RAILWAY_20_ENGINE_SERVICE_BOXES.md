# LWA Railway 20 Engine Service Boxes

## Purpose

LWA now has two engine families:

1. Original platform/backend engines
2. Game/world engines

This document defines the Railway service boxes that should exist when the platform is split beyond the main monolith.

Important: this document does not mean all services should be deployed immediately. Some boxes are safe to create now as read-only/demo-safe services. Others must wait until legal, payments, wallets, marketplace, social API, persistence, and safety gates exist.

## Current Railway reality

Expected current boxes:

```text
lwa-web / frontend
lwa-backend / main API
function-bun / unknown legacy function
```

The 20 engine boxes are not created automatically by code commits. Railway services must be created in Railway or by Railway AI/CLI/API.

## Shared service pattern

All engine boxes should use one shared backend codebase and a generic FastAPI engine service entrypoint.

Start command for every original backend engine service:

```bash
cd lwa-backend && uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $PORT
```

Health path:

```text
/health
```

Engine selector:

```text
LWA_ENGINE_SERVICE_ID=<engine_id>
```

Routes expected from dedicated engine services:

```text
GET  /health
GET  /engine
GET  /engine/health
POST /engine/demo
```

## Original 10 backend/platform engine boxes

| Order | Railway service | Engine ID | Deploy status | Purpose |
|---:|---|---|---|---|
| 1 | `lwa-engine-operator-admin` | `operator_admin` | Deploy first | Operator status, readiness, engine snapshot, safe admin visibility |
| 2 | `lwa-engine-safety` | `safety` | Deploy early | Guardrails, claim safety, risk checks, no external action |
| 3 | `lwa-engine-proof-history` | `proof_history` | Deploy early | Proof previews, history foundation, trust/audit trail |
| 4 | `lwa-engine-world-game` | `world_game` | Deploy early | Lee-Wuh world/game backend bridge for missions/XP/relic previews |
| 5 | `lwa-engine-brain` | `brain` | Deploy after smoke | Intelligence/router brain with providers disabled until gated |
| 6 | `lwa-engine-render` | `render` | Deploy after smoke | Render planning and asset/render readiness, paid render disabled |
| 7 | `lwa-engine-creator` | `creator` | Deploy after smoke | Clip/caption/hook/content package planning |
| 8 | `lwa-engine-wallet-entitlements` | `wallet_entitlements` | Hold | Credits, access, entitlements; no payouts until legal/payment gates |
| 9 | `lwa-engine-marketplace` | `marketplace` | Hold | Campaign/money path engine; hold until marketplace verification gates |
| 10 | `lwa-engine-social-distribution` | `social_distribution` | Hold | Social distribution/export/posting; no external posting until OAuth/API gates |

## Game 10 engine boxes

These services should be created after the platform engine service pattern works. The first game boxes should be safe/read-only/demo-state services. Do not connect real money, gambling, hidden mining, payouts, or irreversible marketplace actions.

Recommended start command for game services, if/when a game service app exists:

```bash
cd lwa-backend && uvicorn app.services.game_engine_service_app:app --host 0.0.0.0 --port $PORT
```

If `game_engine_service_app.py` does not exist yet, do not create these Railway boxes as live services. First build the game generic service entrypoint using `LWA_GAME_ENGINE_SERVICE_ID`.

Game engine selector:

```text
LWA_GAME_ENGINE_SERVICE_ID=<game_engine_id>
```

| Order | Railway service | Game engine ID | Deploy status | Purpose |
|---:|---|---|---|---|
| 11 | `lwa-game-engine-state` | `game_state` | Build service app first | Player/session state, current realm, stage, progress |
| 12 | `lwa-game-engine-mission` | `mission` | Build service app first | Creator actions converted into missions |
| 13 | `lwa-game-engine-quest-chain` | `quest_chain` | Build service app first | Multi-step story/realm progression arcs |
| 14 | `lwa-game-engine-xp-leveling` | `xp_leveling` | Build service app first | XP thresholds, levels, streaks, safe progression math |
| 15 | `lwa-game-engine-reward-relic` | `reward_relic` | Build service app first | Non-monetary rewards, relics, badges, cosmetic unlocks |
| 16 | `lwa-game-engine-realm` | `realm` | Build service app first | Realm catalog, unlocks, visual worlds, portals |
| 17 | `lwa-game-engine-signal-sprint` | `signal_sprint` | Build service app first | First playable micro-game, hook/caption/platform scoring |
| 18 | `lwa-game-engine-inventory` | `inventory` | Build service app first | Relics, badges, cosmetics, sword/aura/avatar items |
| 19 | `lwa-game-engine-economy-balance` | `game_economy` | Build service app first | XP/reward caps, cooldowns, rarity, anti-spam limits |
| 20 | `lwa-game-engine-events-telemetry` | `game_events` | Build service app first | Mission/reward/realm/sprint events and telemetry validation |

## Safe deploy order

Deploy original platform boxes first:

```text
1. lwa-engine-operator-admin
2. lwa-engine-safety
3. lwa-engine-proof-history
4. lwa-engine-world-game
5. lwa-engine-brain
6. lwa-engine-render
7. lwa-engine-creator
```

Then stop and verify the pattern.

Next, only after the generic game engine service app exists:

```text
8.  lwa-game-engine-state
9.  lwa-game-engine-mission
10. lwa-game-engine-quest-chain
11. lwa-game-engine-xp-leveling
12. lwa-game-engine-reward-relic
13. lwa-game-engine-realm
14. lwa-game-engine-signal-sprint
15. lwa-game-engine-inventory
16. lwa-game-engine-economy-balance
17. lwa-game-engine-events-telemetry
```

Hold until gated:

```text
18. lwa-engine-wallet-entitlements
19. lwa-engine-marketplace
20. lwa-engine-social-distribution
```

## Railway AI prompt

Paste this into Railway AI after the engine service code is merged to `main`.

```text
You are Railway AI helping me configure services for my GitHub repo:

jcamacho611/lwa-app

Goal:
Create deployable Railway service boxes for LWA engines using one shared repo and one shared FastAPI start command per engine family.

Do not modify source code.
Do not create secrets.
Do not deploy payment, wallet, marketplace, or social posting as real external-action services yet.
Do not delete my existing frontend or main backend.
Do not delete function-bun until it is audited.

Existing services to keep:
- frontend web service
- main backend API service
- function-bun legacy service, but audit it before deleting

PHASE 1 — Create original backend engine services

For each service below:
- Source repo: jcamacho611/lwa-app
- Branch: main
- Start command: cd lwa-backend && uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $PORT
- Health check path: /health
- Set the listed environment variable
- Deploy one at a time
- After each deploy, check /health, /engine, /engine/health, and POST /engine/demo with {}

Create these first:

1. Service name: lwa-engine-operator-admin
   Env: LWA_ENGINE_SERVICE_ID=operator_admin

2. Service name: lwa-engine-safety
   Env: LWA_ENGINE_SERVICE_ID=safety

3. Service name: lwa-engine-proof-history
   Env: LWA_ENGINE_SERVICE_ID=proof_history

4. Service name: lwa-engine-world-game
   Env: LWA_ENGINE_SERVICE_ID=world_game

5. Service name: lwa-engine-brain
   Env: LWA_ENGINE_SERVICE_ID=brain
   Note: providers must remain disabled/gated.

6. Service name: lwa-engine-render
   Env: LWA_ENGINE_SERVICE_ID=render
   Note: paid render providers/queues must remain disabled/gated.

7. Service name: lwa-engine-creator
   Env: LWA_ENGINE_SERVICE_ID=creator

Do not create these yet unless I explicitly approve after legal/payment/API gates:
- lwa-engine-wallet-entitlements, LWA_ENGINE_SERVICE_ID=wallet_entitlements
- lwa-engine-marketplace, LWA_ENGINE_SERVICE_ID=marketplace
- lwa-engine-social-distribution, LWA_ENGINE_SERVICE_ID=social_distribution

PHASE 2 — Game engine services

Before creating game engine Railway boxes, verify that this file exists in the repo:

lwa-backend/app/services/game_engine_service_app.py

If it does not exist, stop and tell me the game generic service app is missing.

If it exists, create these game services using:

Start command:
cd lwa-backend && uvicorn app.services.game_engine_service_app:app --host 0.0.0.0 --port $PORT

Health check path:
/health

Engine selector:
LWA_GAME_ENGINE_SERVICE_ID=<game_engine_id>

Create:

8.  lwa-game-engine-state
    LWA_GAME_ENGINE_SERVICE_ID=game_state

9.  lwa-game-engine-mission
    LWA_GAME_ENGINE_SERVICE_ID=mission

10. lwa-game-engine-quest-chain
    LWA_GAME_ENGINE_SERVICE_ID=quest_chain

11. lwa-game-engine-xp-leveling
    LWA_GAME_ENGINE_SERVICE_ID=xp_leveling

12. lwa-game-engine-reward-relic
    LWA_GAME_ENGINE_SERVICE_ID=reward_relic

13. lwa-game-engine-realm
    LWA_GAME_ENGINE_SERVICE_ID=realm

14. lwa-game-engine-signal-sprint
    LWA_GAME_ENGINE_SERVICE_ID=signal_sprint

15. lwa-game-engine-inventory
    LWA_GAME_ENGINE_SERVICE_ID=inventory

16. lwa-game-engine-economy-balance
    LWA_GAME_ENGINE_SERVICE_ID=game_economy

17. lwa-game-engine-events-telemetry
    LWA_GAME_ENGINE_SERVICE_ID=game_events

PHASE 3 — Audit function-bun

Audit the existing function-bun service:
- repo/branch
- start command
- env vars
- recent deploy logs
- whether any frontend/backend env var points to it

If unused, rename it to:
legacy-function-bun-unused

Pause it. Do not delete it until I approve.

Final report:
- services created
- domains for each service
- env vars set
- health check result for each service
- demo endpoint result for each service
- services held
- function-bun audit result
- any failures and exact logs
```

## Local validation commands after Railway setup

Replace each domain with the Railway domain.

```bash
curl -fsS https://SERVICE_DOMAIN/health
curl -fsS https://SERVICE_DOMAIN/engine
curl -fsS https://SERVICE_DOMAIN/engine/health
curl -fsS -X POST https://SERVICE_DOMAIN/engine/demo \
  -H 'content-type: application/json' \
  -d '{}'
```

## Frontend env mapping after domains exist

Once Railway gives domains for the deployed original backend engines, set these on the frontend service:

```text
NEXT_PUBLIC_LWA_ENGINE_OPERATOR_ADMIN_URL=https://...
NEXT_PUBLIC_LWA_ENGINE_SAFETY_URL=https://...
NEXT_PUBLIC_LWA_ENGINE_PROOF_HISTORY_URL=https://...
NEXT_PUBLIC_LWA_ENGINE_WORLD_GAME_URL=https://...
NEXT_PUBLIC_LWA_ENGINE_BRAIN_URL=https://...
NEXT_PUBLIC_LWA_ENGINE_RENDER_URL=https://...
NEXT_PUBLIC_LWA_ENGINE_CREATOR_URL=https://...
```

Do not set public wallet, marketplace, or social distribution URLs yet.

## Important boundaries

No hidden mining.
No gambling mechanics.
No real payouts from game services.
No wallet or marketplace external actions until gated.
No social posting until OAuth and permission flows exist.
No paid provider calls from demo endpoints.
