# LWA Experience State Engine

LWA should be event/state-driven instead of page-driven. Pages are surfaces. Events are the product truth. The same event should be able to update the UI, Lee-Wuh, missions, rewards, recovery paths, proof surfaces, and later backend persistence.

The frontend foundation is intentionally local-first. It does not change backend contracts, payment logic, payout logic, crypto/blockchain systems, secrets, or the existing `/generate` route.

## Why Event/State-Driven

The user loop is:

```text
User action
-> product event
-> experience state
-> Lee-Wuh reaction
-> mission or reward update
-> next best action
```

This lets LWA behave like one machine instead of disconnected screens. A generate result, a strategy-only fallback, an export action, proof saved, marketplace opened, or realm entered can all use the same language and mission model.

## States

- `idle`
- `source_added`
- `analyzing`
- `rendering`
- `clips_ready`
- `strategy_only`
- `export_ready`
- `proof_saved`
- `mission_complete`
- `reward_unlocked`
- `marketplace_ready`
- `realm_open`
- `error`

## Events

- `SOURCE_ADDED`
- `GENERATION_STARTED`
- `RENDERING_STARTED`
- `CLIPS_RENDERED`
- `STRATEGY_ONLY_RETURNED`
- `EXPORT_READY`
- `EXPORT_PACKAGE_COPIED`
- `PROOF_SAVED`
- `MARKETPLACE_OPENED`
- `REALM_ENTERED`
- `MISSION_COMPLETED`
- `REWARD_UNLOCKED`
- `ERROR_OCCURRED`
- `RECOVERY_AVAILABLE`
- `RESET`

## Lee-Wuh Reaction Mapping

The reaction map lives in `lwa-web/lib/lee-wuh-reactions.ts`.

- `idle`: hover, calm, "Drop in a source and I'll find the strongest move."
- `source_added`: point_right, focused, "Good. Now generate the clip pack."
- `analyzing`: thinking, focused, "I'm reading the signal."
- `rendering`: rendering, powered, "The realm is cutting this into proof."
- `clips_ready`: victory, confident, "Best clip is ready. Post this one first."
- `strategy_only`: judgment, tactical, "This is strategy only. Useful, but not export-ready yet."
- `export_ready`: point_right, confident, "Package is ready. Copy it, export it, or save proof."
- `proof_saved`: victory, proud, "Proof saved. That strengthens your creator record."
- `mission_complete`: victory, excited, "Mission complete. You moved the realm forward."
- `reward_unlocked`: realmOpen, powered, "Reward unlocked."
- `marketplace_ready`: marketplaceGuide, focused, "Money lane is open. Choose the right opportunity."
- `realm_open`: realmOpen, mystical, "The realm is open."
- `error`: error, concerned, "Something failed, but we can recover the run."

## Mission Connection

The mission engine remains local in `lwa-web/lib/lwa-mission-engine.ts`.

Starter missions:

- First Signal: completed by `CLIPS_RENDERED`
- Proof Builder: completed by `EXPORT_PACKAGE_COPIED` or `PROOF_SAVED`
- Money Gate: completed by `MARKETPLACE_OPENED`
- Realm Entry: completed by `REALM_ENTERED`
- Recovery Operator: completed by `RECOVERY_AVAILABLE`

The controller displays active mission, completed mission count, XP earned, and safe local rewards. These are progression signals only. They are not money, payouts, crypto, or marketplace eligibility.

## Future Backend Integrations

Later backend work can add durable records for:

- product events
- request and clip proof history
- mission completion
- reward ledger entries
- recovery decisions
- cost governance decisions
- provider routing decisions
- rights and safety flags

Backend integration should be additive and non-breaking. The frontend event vocabulary should remain stable enough that the real `/generate` flow can emit events without changing the existing generate response contract.

## Intentionally Not Included Yet

- no real payouts
- no blockchain
- no hidden mining
- no payment changes
- no backend schema migration
- no direct posting claims
- no campaign submission automation
- no iOS changes

