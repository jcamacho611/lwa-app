# LWA / IWA Source Of Truth

## Rule

The existing repo is the source of truth.

This project is a continuation mission, not a restart.

Do not create parallel apps, duplicate backend structures, or replacement frontends unless an audit proves the existing structure is unusable.

## Actual repo paths

Use the actual repo paths discovered by audit.

Expected current paths:

- backend: `lwa-backend`
- frontend: `lwa-web`
- iOS: `lwa-ios`
- tooling: `tools`
- company docs: `docs/company`

If a master prompt says `apps/backend` or `apps/web`, adapt it to the real repo structure instead of creating new folders.

## Product

LWA / IWA is an AI content repurposing product.

Primary promise:

Drop in one long-form source and get ranked short-form outputs with hooks, captions, timestamps, scores, and workflow-ready assets.

## Current MVP truth

The app should be treated as a real MVP, not a mock.

Known current or near-current capabilities may include:

- public video URL generation
- target platform selection
- optional angle/trend input
- ranked clip pack output
- hooks
- captions
- timestamps
- scores
- asset links
- source upload work
- prompt/music/campaign strategy lanes
- source matrix tooling
- revenue intent event tracking

Codex must verify every item in the repo before claiming it as shipped.

## Repo evidence observed during Chunk 15 preparation

GitHub search on `main` shows current evidence for:

- `lwa-backend/app/api/routes/generate.py`
- `lwa-backend/app/api/routes/generation.py`
- `lwa-backend/app/api/routes/me.py`
- `lwa-backend/app/services/source_ingest.py`
- `lwa-backend/app/services/video_service.py`
- `lwa-backend/app/services/clip_service.py`
- `lwa-backend/app/services/platform_store.py`
- `lwa-backend/app/models/schemas.py`
- `lwa-backend/tests/test_any_source_engine.py`
- `lwa-backend/tests/test_platform_store.py`
- `lwa-backend/tests/test_clip_strategy.py`
- `lwa-web/lib/types.ts`
- `docs/company/lwa-any-source-engine-spec.md`
- `docs/company/lwa-ai-output-schema-map.md`
- `docs/company/lwa-source-output-event-protocols.md`
- `docs/company/lwa-connector-protocol-map.md`
- `docs/company/lwa-master-prompt-library.md`

GitHub search did not find revenue event route/logger files by the queried terms `revenue_events`, `RevenueEvent`, `revenue_event_log`, or `authoritative` during this preparation pass. Codex must verify locally before marking revenue tracking as installed.

## Planned systems

The following are strategic plans unless repo evidence proves they are implemented:

- Director Brain
- full marketplace
- Stripe Connect payouts
- Whop submerchant marketplace
- Signal Realms RPG
- social posting APIs
- Polymarket trend ingestion
- blockchain/NFT proof layer
- full mobile/iOS App Store system

## Safe customer claim

Use:

LWA supports upload-first clipping for common video/audio sources plus strategy generation for prompt, music, campaign, and image-style inputs. Public URLs are best-effort because platforms can block server extraction.

Do not claim guaranteed YouTube, TikTok, Instagram, or Twitch extraction.

## Safety rules

Do not claim:

- guaranteed virality
- guaranteed income
- payment verified without webhook verification
- payout ready without KYC/tax/fraud controls
- NFT value appreciation
- investment return
- platform posting approved before API review

## Engineering rule

One safe implementation slice at a time.

Preferred order:

1. source handling hardening
2. free launch mode
3. fallback hardening
4. README/Railway launch polish
5. Director Brain v0
6. caption preset renderer
7. frontend generate flow polish
8. marketplace audit/docs
9. marketplace dark scaffold without live payouts
10. Realms static shell
11. social API OAuth shell
12. off-chain proof dry run
