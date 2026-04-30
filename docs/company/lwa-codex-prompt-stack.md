# LWA Codex Prompt Stack

## Rule

Use one prompt per slice. Do not paste the entire Master Council Report into Codex as one implementation task.

Codex must inspect the actual repo first, preserve existing working code, and adapt paths from planning docs to the real repo structure.

## Prompt order

1. Master repo fusion and status map.
2. Source handling hardening.
3. Free launch mode.
4. Fallback hardening.
5. Director Brain v0.
6. Caption preset contract.
7. Marketplace compatibility audit.
8. Marketplace dark scaffold.
9. Signal Realms static shell.
10. Social integration status shell.
11. Off-chain provenance dry run.
12. Trust and safety review queue.

## Prompt 1 — Master Repo Fusion

Task:

- audit repo
- fuse master docs
- create implementation status map
- correct assumed paths
- select one safest next slice

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

## Prompt 3 — Free Launch Mode

Task:

- backend env flag
- compatible guest behavior
- abuse cap
- frontend banner
- Railway env docs
- tests

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
- structured outputs
- provider fallback
- tests

Do not duplicate existing Claude/OpenAI/Seedance routing if present.

## Prompt 6 — Caption Presets

Task:

- caption preset spec
- renderer contract
- overlay spec output
- no heavy render rewrite unless existing render path supports it

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

## Prompt 9 — Realms Static Shell

Task:

- static pages/content
- class/faction/quest content
- profile shell
- no XP purchases
- no feature unlock relics

## Prompt 10 — Social Integration Status Shell

Task:

- provider status plan
- safe OAuth direction
- no posting until approved
- Polymarket read-only only

## Prompt 11 — Off-Chain Provenance Dry Run

Task:

- deterministic proof records
- JSON export
- no mainnet
- no purchase flow

## Prompt 12 — Trust/Safety Queue

Task:

- pending review queue
- takedown/escalation states
- audit events
- dispute evidence placeholders

## Required final report from Codex

Every run must return branch, starting commit, files inspected, source docs used, protected files detected, files changed, implementation summary, preserved systems, tests run, blockers, commit hash/message, and next chunk prompt.
