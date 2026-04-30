# LWA Remaining Work Checklist

## Rule

Before creating any file, search and fetch first.

If the file exists, update it.

If the file does not exist, create it.

Do not create unnecessary duplicates.

## Completed foundation

- Source-of-truth docs exist.
- Claim safety docs exist.
- Launch checklist exists.
- Smoke test runbook exists.
- Director Brain docs exist.
- Director Brain support modules exist.
- Algorithm database blueprint exists.
- Operations playbook exists.
- Investor and sales artifact exists.
- Hiring artifact exists.
- File creation policy exists.

## Remaining verification

- Run backend compile check.
- Run backend tests.
- Run frontend type check.
- Run frontend build if stable.
- Smoke test live frontend.
- Smoke test live backend.
- Smoke test generation.
- Smoke test upload path if enabled.
- Confirm fallback behavior is clean.

## Remaining implementation

- Confirm Director Brain fields are wired into generation output.
- Confirm frontend displays optional Director Brain fields safely.
- Confirm campaign roles are generated and displayed.
- Add operator metrics after generation events are stable.
- Decide future database migration path.

## Future work

- Marketplace scaffold later.
- Signal Realms shell later.
- Social status shell later.
- Off-chain proof dry run later.

## Do not duplicate

- Do not duplicate docs/company source-of-truth files.
- Do not duplicate docs/lwa-worlds artifacts.
- Do not duplicate backend Director Brain modules.
- Do not merge stale branches with no new commits.

## Done definition

The current stage is done when verification passes, live smoke tests pass, and remaining future work is tracked without duplicate files.
