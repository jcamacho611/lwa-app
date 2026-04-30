# START HERE — LWA Codex Terminal Handoff

This folder was added so Codex Terminal can read the LWA artifact bundle directly from GitHub.

## Read order

1. `CODEX_HANDOFF_FULL.md`
2. `01_MASTER_CODEX_TERMINAL_PROMPT.txt`
3. `03_FRONTEND_REBUILD_TRACK.txt`
4. `04_BACKEND_FREE_LAUNCH_AND_FALLBACKS.txt`
5. `08_EMERGENCY_STOP.txt`

## Core rule

Codex must inspect the repo first, preserve the working MVP, avoid `lwa-ios/`, and continue from the real repo state.

## Suggested terminal command

```bash
cat docs/codex-terminal-handoff/CODEX_HANDOFF_FULL.md
```

Then paste the Master Prompt section into Codex Terminal.
