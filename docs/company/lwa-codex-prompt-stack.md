# LWA Codex Prompt Stack

## Rule

Use one prompt per slice.

Do not paste the entire Master Council Report into Codex as an implementation task.

Codex must inspect the actual repo first, preserve existing working code, and adapt paths from planning docs to the actual repo structure.

## Prompt 1 — Master Repo Fusion

Use when the repo needs docs/source-of-truth/status-map fusion.

Task:

- audit repo
- fuse master docs
- create implementation status map
- correct assumed paths
- select one safest next slice

Primary prompt file:

- `docs/company/lwa-github-codex-master-fusion-prompt.md`

## Prompt 2 — Source Handling Hardening

Task:

- central format/source map if missing
- stable source_type values
- clean unsupported errors
- public URL blocked fallback
- POC runner compatibility
- frontend accept list if safe

Expected source_type values:

- `video_upload`
- `audio_upload`
- `image_upload`
- `prompt`
- `music`
- `campaign`
- `url`

## Prompt 3 — FREE_LAUNCH_MODE

Task:

- backend env flag
- free launch guest behavior if compatible
- abuse cap
- frontend banner
- Railway env docs
- tests

Do not remove paid-mode entitlement logic.

## Prompt 4 — Fallback Hardening

Task:

- deterministic fallback helpers
- no raw tool errors
- degraded but usable response
- provider/source failure tests
- no full pipeline rewrite unless proven necessary

## Prompt 5 — Director Brain v0

Task:

- platform prompt pack
- hook/caption/moment scoring
- structured JSON outputs
- provider fallback
- tests

Do not duplicate existing Claude/OpenAI/Seedance routing if present.

## Prompt 6 — Caption Presets

Task:

- caption preset spec
- renderer contract
- overlay spec output
- no heavy render rewrite unless existing render path supports it

Presets:

- `crimson_pulse`
- `clean_op`
- `karaoke_neon`
- `signal_low`
- `bigframe`
- `medspa_safe`
- `dev_brutal`

## Prompt 7 — Marketplace Audit

Task:

- inspect existing architecture
- docs only
- choose persistence strategy
- no live money movement

## Prompt 8 — Marketplace Dark Scaffold

Task:

- marketplace pages/routes if compatible
- product/job/submission statuses
- admin review states
- earnings disclaimers
- no real payouts

## Prompt 9 — Realms Static Shell

Task:

- static pages/content
- class/faction/quest content
- profile shell
- no chain
- no XP purchases
- no feature unlock relics

## Prompt 10 — Social OAuth Shell

Task:

- provider status/OAuth plan
- encrypted tokens if implemented
- no posting until approved
- Polymarket read-only only

## Prompt 11 — Off-Chain Proof Dry Run

Task:

- deterministic proof records
- Merkle JSON export
- no mainnet
- no NFT purchase flow

## Prompt 12 — Trust/Safety Queue

Task:

- pending review queue
- takedown/escalation states
- audit events
- dispute evidence placeholders

## Required final report from Codex

Every run must return:

1. branch and starting commit
2. files inspected
3. source docs used
4. protected files detected
5. files changed
6. what was implemented
7. what was preserved
8. tests run
9. blockers
10. commit hash/message
11. next chunk prompt
