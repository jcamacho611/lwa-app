# LWA Implementation Status

This file must be updated after every Codex slice.

Use repo evidence only. If there is no repo evidence, mark the area as `planned`, `unknown`, or `not implemented`. Never mark a planned system as shipped.

## Chunk 15 status map

| Area | Status | Evidence in repo | Safe next step |
|---|---|---|---|
| Core generation | In progress / present | GitHub search finds `lwa-backend/app/api/routes/generate.py`, `lwa-backend/app/api/routes/generation.py`, `lwa-backend/app/services/clip_service.py`, `lwa-backend/app/generation.py`, `lwa-backend/app/processor.py` | Preserve and harden; do not rewrite generation flow |
| Upload/source handling | In progress / present | GitHub search finds `lwa-backend/app/services/source_ingest.py`, `lwa-backend/tests/test_any_source_engine.py`, upload/source typing references | Normalize source contract; keep source matrix tooling passing |
| Public URL support | Best-effort / present | Generation/source ingest files exist; source docs mention public URL/source protocols | Clean fallback messages; no guaranteed platform extraction claims |
| Source POC Matrix | In progress / protected | Fusion guardrails protect `tools/poc/source_matrix_runner.py` and related tests | Keep runner compatible before/after source changes |
| Revenue intent tracking | Unknown / verify locally | Uploaded Codex ledger reports revenue event foundation; GitHub search did not find `revenue_events`, `RevenueEvent`, `revenue_event_log`, or `authoritative` in the queried branch/main snapshot | Audit locally before claiming installed; reinstall only if missing and selected as a slice |
| FREE_LAUNCH_MODE | Unknown / likely missing | No confirmed repo evidence from Chunk 15 search | Add after source handling if missing and compatible |
| Fallback hardening | Partial / unknown | Source error and clip strategy files exist, but deterministic full fallback layer must be audited | Add deterministic fallbacks after free launch/source hardening if needed |
| Director Brain | Planned | Master Council Report and prompt stack define it; no confirmed `director_brain` service evidence yet | Build v0 after P0 hardening |
| Caption presets | Planned | Master Council Report defines 7 presets; no confirmed renderer evidence yet | Build structured overlay spec after Director Brain |
| Marketplace | Future / docs planned | Master Council Report and future plan define it; do not assume runtime implementation | Run marketplace compatibility audit before code |
| Realms/RPG | Future / docs planned | Master Council Report and doctrine define Signal Realms | Build static shell first; no blockchain, no purchasable XP |
| Social APIs | Future / docs planned | Master Council Report defines provider plan | OAuth/status shell only later; no posting until approval |
| Blockchain/proof | Future / docs planned | Master Council Report defines optional proof roadmap | Off-chain proof dry run only later |
| iOS/mobile | Existing app + planned bridge | `lwa-ios` exists in project history; mobile readiness bridge doc exists/expected | Do not touch without explicit iOS approval |
| Investor/data room | Docs/planned | Investor/company docs may exist or be added later | Keep internal/admin; do not expose claims as shipped |
| Frontend premium UI | In progress | `lwa-web` exists; prior work includes app routes/components and premium direction | Polish after core generate/upload flow is stable |
| Railway deployment | In progress | Live backend/frontend URLs documented in Master Council Report | Smoke test after runtime merges/deploys |

## Update rule

Every task must update this file if it changes status.

## Claim rule

If there is no repo evidence, mark status as `planned`, `unknown`, or `not implemented`.

Never mark a planned system as shipped.
