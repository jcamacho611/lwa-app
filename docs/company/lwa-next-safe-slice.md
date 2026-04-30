# LWA Next Safe Slice

## Selection rule

After every Codex run, choose exactly one next safe slice.

Do not bundle unrelated systems into one run.

## Priority order

### P0 — Product must work

1. source handling hardening
2. free launch mode
3. fallback hardening
4. README/Railway launch polish

### P1 — Product must feel valuable

5. Director Brain v0
6. platform prompt pack
7. hook formula library
8. caption preset renderer
9. better generate result cards

### P2 — Product must convert safely

10. monetization CTA polish
11. webhook audit
12. billing provider decision doc
13. entitlement reconciliation

### P3 — Product moat

14. marketplace compatibility audit
15. marketplace dark scaffold
16. Realms static shell
17. social integration shell
18. off-chain provenance dry run

## Current recommended next slice

Run source handling hardening if source behavior is still not fully normalized.

If source behavior is already normalized, run free launch mode.

If free launch mode is already done, run fallback hardening.

If all three are done, run README/Railway launch polish.

## Decision checklist

Before selecting a slice, verify:

- Does `/v1/uploads` return stable `source_type`?
- Does `/v1/generate` preserve the same source contract?
- Does the source matrix runner still work?
- Does public URL failure return clean fallback copy?
- Does free launch mode exist in backend config?
- Does the frontend free launch banner exist?
- Do provider/source failures degrade instead of crashing?
- Is README aligned with actual repo paths and Railway URLs?

## Later systems

Do not start later systems until P0 is stable.

## Required update

After completing a slice, update:

- `docs/company/lwa-implementation-status.md`
- this file's current recommended next slice
