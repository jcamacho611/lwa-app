# LWA Implementation Status

This file must be updated after every safe implementation slice.

Use repo evidence only. If unknown, say unknown. If planned, say planned. Never mark a planned system as shipped.

| Area | Status | Evidence in repo | Safe next step |
|---|---|---|---|
| Core generation | In progress / verify before claim | Check `lwa-backend` generation routes and tests | Preserve and harden |
| Upload/source handling | In progress | Check source ingest/upload routes and source matrix tooling | Normalize source contract |
| Public URL support | Best-effort | Public platforms may block server extraction | Clean fallback messages and avoid raw tool errors |
| Source POC Matrix | In progress if `tools/poc` exists | Source matrix runner and related tests | Keep runner passing |
| Revenue intent tracking | Present if `/v1/revenue/events` exists | Revenue event route/logger/tests | Preserve non-authoritative behavior |
| FREE_LAUNCH_MODE | Unknown until audit | Backend env/config and frontend banner | Add if missing after source hardening |
| Fallback hardening | Unknown until audit | Pipeline/source failure behavior | Add deterministic degraded results |
| Director Brain | Planned unless code exists | `director_brain` service/prompts | Build v0 after hardening |
| Caption presets | Planned unless code exists | Caption renderer/preset files | Build after Director Brain |
| Marketplace | Future | Marketplace routes/models/pages if present | Audit before implementation; no live payouts |
| Realms/RPG | Future | Realm routes/pages/models if present | Static shell only first |
| Social APIs | Future | Integration providers/OAuth if present | OAuth shell only; no posting until approved |
| Blockchain/proof | Future | Issuance/proof/Merkle files if present | Off-chain dry run only |
| iOS/mobile | Existing app + planned bridge | `lwa-ios` and mobile docs | Audit only before touching code |
| Investor/data room | Docs/planned | Investor docs/routes if present | Keep internal/admin only |
| Frontend premium UI | In progress | `lwa-web` routes/components | Polish after core flow |
| Railway deployment | In progress | Railway URLs/env docs | Smoke test after each deploy |

## Current priority

P0 is product reliability:

1. source handling hardening
2. FREE_LAUNCH_MODE
3. fallback hardening
4. README/Railway launch polish

## Claim rule

If there is no repo evidence, mark the feature as `planned`, `unknown`, or `not implemented`.

Do not claim marketplace, Realms, social APIs, blockchain, verified payments, or iOS App Store readiness as shipped until code and tests prove it.
