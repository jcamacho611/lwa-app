# LWA Chunk 16 Review Artifact

## Branch

`feat/chunk16-p0-hardening`

## Purpose

This branch begins converting the Master Council / Director Brain / Chunk 16 direction into real repo files.

It is not a full completion of every future system. It is the first runtime-safe implementation batch that touches the actual backend paths instead of creating duplicate architecture.

## Runtime files added or updated

### Source handling hardening

- `lwa-backend/app/services/source_contract.py`
- `lwa-backend/app/api/routes/upload.py`
- `lwa-backend/app/api/routes/generate.py`
- `lwa-backend/tests/test_source_contract.py`

Adds:

- shared source type contract
- stable upload source type classifier
- upload allow-list helper
- source_ref helper
- generate/upload source type normalization
- tests for expected source behavior

### Free launch settings foundation

- `lwa-backend/app/core/config.py`

Adds:

- `settings.free_launch_mode`
- `settings.rate_limit_guest_rpm`

This does not yet fully wire free-launch auth/rate limiting into every dependency. That should happen in the next small runtime pass after source tests are reviewed.

### Deterministic fallback helpers

- `lwa-backend/app/services/fallbacks.py`
- `lwa-backend/tests/test_fallbacks.py`

Adds:

- `FallbackClipResult`
- transcript fallback windows
- moment fallback windows
- caption fallback
- hook fallback
- degraded fallback clip result helper

This helper is available for pipeline integration in the next pass.

### Director Brain artifacts

- `lwa-backend/app/services/hook_formula_library.py`
- `lwa-backend/app/services/caption_presets.py`
- `lwa-backend/app/services/director_brain.py`
- `lwa-backend/tests/test_director_brain_artifacts.py`

Adds:

- 20 hook formula records
- caption preset code registry
- Director Brain v0 runtime shell
- structured package output
- tests for hook formulas, caption presets, and Director Brain payload shape

## Things intentionally not completed in this batch

- full Claude provider runtime wiring
- Seedance provider runtime wiring
- full free-launch guest/auth behavior
- full rate-limit middleware change
- full pipeline fallback integration
- marketplace runtime
- Signal Realms runtime
- social OAuth runtime
- proof/provenance runtime
- iOS work

## Connector limitations encountered

Some larger doc/data writes were blocked by the GitHub connector safety layer, especially when a single file combined future proof, trading, payout, or regulated-vertical wording. The branch still includes the core runtime artifacts in smaller backend files.

## Review checklist

Before merge:

1. Run backend compile.
2. Run backend tests.
3. Confirm `/v1/uploads` still returns the expected upload response shape.
4. Confirm `/v1/generate` still handles upload-file source references.
5. Confirm new source contract tests pass.
6. Confirm fallback helper tests pass.
7. Confirm Director Brain artifact tests pass.

## Suggested next pass

After this branch is reviewed:

1. wire `FREE_LAUNCH_MODE` into auth/entitlement/rate limit behavior
2. wire fallback helpers into the media pipeline error path
3. expand caption preset metadata if connector allows
4. add frontend free launch banner
5. expose Director Brain v0 through the existing generation output only after tests prove no response contract break
