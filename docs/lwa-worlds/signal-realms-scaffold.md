# Signal Realms Scaffold

## Status

This is a non-chain backend scaffold for future Signal Realms progression work.

It is not a live blockchain feature and it does not create purchasable XP, investment assets, or feature unlocks.

## Current files

- `lwa-backend/app/services/signal_realms_core.py`
- `lwa-backend/tests/test_signal_realms_core.py`

## Current rules

- XP cannot be bought.
- Badges are earned and soulbound by default.
- Relics are cosmetic only.
- Relics do not unlock app features.
- Blockchain is not part of this scaffold.
- No investment framing is allowed.

## Current primitives

- 12 classes
- 12 factions
- XP curve helpers
- character creation helper
- XP award helper
- badge helper
- relic helper
- safety disclosure helper

## Future order

1. Persistent character records.
2. XP event ledger.
3. Quest progress records.
4. Badge awards.
5. Relic holdings.
6. Read-only leaderboards.
7. Frontend `/realm` shell.
8. Optional proof layer later, separate from gameplay progression.

## Claim boundary

Do not describe Signal Realms as live until routes, persistence, frontend views, and moderation/safety rules are implemented and verified.
