# LWA CHUNK 9 — EXECUTION ORDER AND REMAINING CODEX PROMPTS

This chunk defines the safe order for turning the algorithm chunks into production work.

## Global rule

```text
Preserve what already works.
Build missing systems behind feature flags.
Do not mark unfinished systems as live.
Do not mix backend, frontend, and iOS changes in the same implementation prompt.
```

## Safe implementation order

```text
1. Merge safe docs and frontend staging branches.
2. Add remaining algorithm/database documentation chunks.
3. Build backend service modules in isolation.
4. Build unit tests for pure functions.
5. Add SQL migrations or SQL setup files.
6. Wire generation output with optional fields only.
7. Update frontend types and display components.
8. Add upload pipeline behind feature flag.
9. Add campaign manager behind feature flag.
10. Add direct social OAuth shell behind feature flag.
11. Add marketplace behind feature flag.
12. Add Signal Realms behind feature flag.
13. Add off-chain proof behind feature flag.
14. Plan full iOS rebuild on a dedicated branch.
```

## Backend implementation prompt

```text
You are the LWA backend implementation engineer.

Task:
Implement backend service modules and tests from docs/lwa-worlds/chunk-4-sql-repository-layer.md, chunk-6-campaign-social-algorithms.md, chunk-7-marketplace-realms-proof.md, and chunk-8-editor-ios-rebuild.md, but only for backend-safe scaffolds.

Rules:
- Preserve existing backend routes.
- Add optional fields only.
- Do not touch lwa-web.
- Do not touch lwa-ios.
- Do not fake upload completion.
- Do not fake direct posting.
- Do not fake marketplace checkout.
- Do not fake blockchain publishing.
- Strategy-only clips must never be shown as rendered.
- Rendered clips must require real asset URLs.
- Money uses integer cents.
- Webhooks are idempotent.
- XP cannot be bought.
- Badges are earned.
- Relics/cosmetics provide no paid advantage.
- Off-chain proof comes before testnet or mainnet work.

Verification:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant backend tests

Expected output:
1. files changed
2. services added
3. migrations added
4. tests added
5. verification results
6. risks or skipped work
7. commit message
```

## Frontend implementation prompt

```text
You are the LWA frontend implementation engineer.

Task:
Implement the frontend display logic from docs/lwa-worlds/chunk-5-frontend-display-logic.md.

Rules:
- Touch lwa-web only.
- Do not touch backend.
- Do not touch lwa-ios.
- Preserve existing generation flow.
- Rendered clips show playable media only when URLs exist.
- Raw-only clips show raw asset actions only when raw URLs exist.
- Strategy-only clips never show fake players.
- Show Director Brain package fields safely when present.
- Keep UI premium, creator-native, and not overloaded.

Verification:
- cd lwa-web
- npm run type-check if available
- npm run lint if available
- npm run build if available

Expected output:
1. files changed
2. fields displayed
3. media-state behavior
4. verification results
5. commit message
```

## Upload pipeline prompt

```text
You are the LWA upload pipeline engineer.

Task:
Implement a real upload pipeline behind the upload_pipeline feature flag.

Rules:
- Do not claim upload is live until end-to-end upload, scan/probe, source_asset creation, and generation handoff work.
- Add upload session creation.
- Add upload finalization scaffold.
- Validate MIME type and file size.
- Preserve URL-based generation.
- Do not touch iOS unless this is the dedicated iOS upload prompt.

Verification:
- backend py_compile
- backend tests
- one upload-session unit test
```

## Campaign manager prompt

```text
You are the LWA campaign systems engineer.

Task:
Build campaign manager scaffolding behind feature flag.

Rules:
- Campaign Mode may assign clip roles.
- Campaign Manager must not appear live until workspace, brief, calendar, approval status, and schedule status are implemented.
- Do not fake social publishing.
- Keep direct posting disabled unless the social posting feature flag is live.

Verification:
- backend py_compile
- backend tests
```

## Marketplace prompt

```text
You are the LWA marketplace engineer.

Task:
Scaffold marketplace products, seller trust, orders, and integer-cent money math behind feature flag.

Rules:
- Do not enable live checkout in this prompt.
- No guaranteed income language.
- Integer cents only.
- Webhooks idempotent.
- Seller payouts require verified payment state.

Verification:
- backend py_compile
- marketplace money math tests
- seller trust tests
```

## Realms prompt

```text
You are the LWA Signal Realms engineer.

Task:
Scaffold XP, quests, badges, and cosmetic relic metadata behind feature flag.

Rules:
- XP cannot be bought.
- Badges are earned.
- Relics are cosmetic only.
- No paid advantage.
- No gambling mechanics.
- No investment framing.

Verification:
- XP curve tests
- quest progress tests
```

## Proof prompt

```text
You are the LWA proof-of-creation engineer.

Task:
Implement off-chain proof records and Merkle batch helpers behind feature flag.

Rules:
- No mainnet publishing.
- No testnet publishing unless a later dedicated prompt enables it.
- No NFT feature unlocks.
- No investment language.
- Proof is about provenance only.

Verification:
- stable hash tests
- Merkle root tests
```

## iOS prompt

```text
Dedicated iOS branch only.

Task:
Add Director Brain response field support to iOS models and views.

Rules:
- Preserve existing preview/share/history flow.
- Do not build the full editor in this prompt.
- Do not build marketplace in this prompt.
- Do not build direct social posting in this prompt.
- Do not touch backend.
- Do not touch lwa-web.

Verification:
- build Debug
- build Release if available
- confirm existing preview/share/history still works
```

## Final build rule

The architecture includes upload, editor, campaign manager, direct posting, marketplace, Signal Realms, proof/blockchain, and iOS rebuild. Implementation must happen in separated, verifiable branches so production clipping remains stable.
