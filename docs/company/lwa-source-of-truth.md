# LWA / IWA Source Of Truth

## Rule

The existing repository is the source of truth.

This is a continuation mission, not a restart. Do not create replacement apps, parallel backends, duplicate web apps, or generic templates unless a repo audit proves the existing structure is unusable.

## Actual repo direction

Expected working paths in this repo:

- Backend: `lwa-backend`
- Frontend: `lwa-web`
- iOS: `lwa-ios`
- Tools: `tools`
- Company docs: `docs/company`

If any outside prompt says `apps/backend` or `apps/web`, adapt it to the real repo structure instead of creating new folders.

## Product

LWA / IWA is an AI content repurposing product.

Primary promise:

> Drop in one long-form source and get ranked short-form outputs with hooks, captions, timestamps, scores, and workflow-ready assets.

Operational promise:

> Move from generation to queue to campaigns to payout-readiness inside one premium creator workspace.

## Current MVP truth

Treat the app as a real MVP, not a mock. Verify every item in the repo before claiming it as shipped.

Known working or near-current directions may include:

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

## Planned systems

The following remain planned unless repo evidence proves they are implemented:

- Director Brain
- full marketplace
- Stripe Connect payouts
- Whop submerchant marketplace
- Signal Realms RPG
- social posting APIs
- Polymarket trend ingestion
- blockchain/NFT proof layer
- full mobile/App Store system

## Engineering order

Build one safe slice at a time:

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

## Safe customer-facing claim

LWA supports upload-first clipping for common video/audio sources plus strategy generation for prompt, music, campaign, and image-style inputs. Public URLs are best-effort because platforms can block server extraction.

Do not claim guaranteed YouTube, TikTok, Instagram, Twitch, or Instagram extraction.

## Safety rules

Do not claim:

- guaranteed virality
- guaranteed income
- payment verified without server-side webhook verification
- payout ready without KYC/tax/fraud controls
- NFT value appreciation
- investment return
- platform posting approved before API review
