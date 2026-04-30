# LWA PR And Merge Control

## Rule
The council wants execution, but not destructive chaos.

## Merge order
1. Docs/source-of-truth PRs first.
2. Feature PRs into their correct feature base.
3. Feature base into main only after tests.
4. Never force-merge draft runtime PRs directly into main.

## Current known PR handling

### PR #71
- Director Brain v0 recommendation rail.
- Currently draft.
- Base is feat/source-poc-matrix.
- Do not force directly into main while draft.
- Finish this feature branch first, then promote cleanly.

## Required verification

Backend:
```bash
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend && python3 -m unittest discover -s tests && cd ..
```

Frontend:
```bash
cd lwa-web
npm run type-check
npm run build
cd ..
```

Final:
```bash
git diff --check
git status --short --branch
```
