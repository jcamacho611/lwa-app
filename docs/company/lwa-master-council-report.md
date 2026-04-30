# LWA Worlds Master Council Report

## Source artifact

The full Master Council Report was provided in the project thread and uploaded as `Pasted markdown.md`.

It covers:

1. Phase 1 clipping engine hardening
2. Competitive intelligence
3. Platform signal database
4. Marketplace architecture
5. Signal Realms RPG system
6. Social API integration plan
7. Blockchain/provenance roadmap
8. Hiring plan
9. Codex prompt stack
10. Council executive summary

## Repository rule

The report is a source-of-truth artifact, but implementation must adapt to the real repo paths:

- backend: `lwa-backend`
- frontend: `lwa-web`
- iOS: `lwa-ios`
- company docs: `docs/company`

Do not create `apps/backend` or `apps/web` just because the report uses those as generic examples.

## Current implementation branch

Branch:

- `feat/chunk16-p0-hardening`

PR:

- #28: `backend: add Chunk 16 P0 source and Director Brain foundations`

## Material already converted into runtime files on this branch

### Source handling

- `lwa-backend/app/services/source_contract.py`
- `lwa-backend/app/api/routes/upload.py`
- `lwa-backend/app/api/routes/generate.py`
- `lwa-backend/tests/test_source_contract.py`

### Free launch config foundation

- `lwa-backend/app/core/config.py`

Adds:

- `settings.free_launch_mode`
- `settings.rate_limit_guest_rpm`

### Fallback helpers

- `lwa-backend/app/services/fallbacks.py`
- `lwa-backend/tests/test_fallbacks.py`

### Director Brain artifacts

- `lwa-backend/app/services/hook_formula_library.py`
- `lwa-backend/app/services/caption_presets.py`
- `lwa-backend/app/services/director_brain.py`
- `lwa-backend/tests/test_director_brain_artifacts.py`

## Still to implement from the report

### Phase 1 hardening

- full free-launch guest behavior
- guest request cap wiring
- frontend free launch banner
- full pipeline fallback integration
- README Day 3 polish

### Director Brain

- provider routing between Claude/OpenAI/local fallback
- full platform signal database
- hook rewriter connected to generation output
- caption preset renderer connected to render pipeline
- platform prompt files

### Marketplace

- compatibility audit
- dark scaffold
- listing model or store
- admin review queue
- signed webhook/idempotency plan before live money movement

### Signal Realms

- static shell first
- class/faction content
- quest/badge/relic catalog
- event-based XP later

### Social APIs

- provider status shell
- OAuth shell later
- no direct posting until scopes/review are confirmed

### Provenance/proof

- off-chain dry run first
- no required wallet
- no feature unlocks from proof or cosmetic items

### Hiring/ops

- standalone recruiting docs
- outreach templates
- interview question bank
- build-or-hire matrix

## Implementation rule

Continue converting the report into the repo in reviewable chunks.

Runtime code should be small, tested, and adapted to existing files.

Docs and artifacts should preserve the full plan without claiming unbuilt systems are shipped.
