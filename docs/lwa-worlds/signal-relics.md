# Signal Relics

> **Original LWA mechanic.** Inspired by the *vastness and variety* of large character-power systems, but built from scratch around creator workflow primitives. Not a copy of *Devil Fruits* or any other protected mechanic from third-party IP.

## Status

This document is a future-facing design reference. It is **not a live feature**, **not a token**, and **not a financial instrument**. Treat every section below as scaffolding for later product, art, and game-system work.

For the broader scaffolding rules, see [`signal-realms-scaffold.md`](./signal-realms-scaffold.md). Signal Relics live inside the Signal Realms framework and inherit its safety boundaries.

## Hard rules (do not violate)

- Signal Relics are **cosmetic / progression / identity / ability-flavor** objects.
- Relics **do not unlock paid advantage**. They do not gate features behind payment.
- Relics are **not NFTs or tokens** by default.
- Relics are **not gambling**. There are no loot boxes, randomized purchases, or pay-to-pull mechanics implied here.
- Relics are **not investment instruments**. Owning a relic does not imply revenue share, equity, or guaranteed income.
- Any future tradeable, paid, or chain-bound version requires explicit legal/compliance review before implementation.

## What a Signal Relic is

A Signal Relic is an in-world artifact tied to a primitive of the LWA creator workflow — clip, hook, caption, timing, signal, memory, voice, remix, packaging, audience, archive. Each relic has:

- **Name** — original LWA naming, no third-party IP echoes.
- **Realm of origin** — which Signal Realm produced it (see existing 12 realms / 12 factions in the scaffold).
- **Domain** — the workflow primitive it expresses (clip, hook, etc.).
- **Flavor ability** — narrative description of what the relic *represents*. This is lore; product surfaces will not grant real powers from it.
- **Cosmetic effects** — future avatar / UI / badge flavor only.
- **Limits / weaknesses** — every relic has narrative trade-offs to keep the system balanced and non-pay-to-win.

## Categories

1. **Hook Relics** — relate to opening lines, attention-capture, pattern interrupts.
2. **Source Relics** — relate to ingest, transcript, raw long-form material.
3. **Caption Relics** — relate to subtitles, on-screen typography, readability.
4. **Timing Relics** — relate to pacing, retention curve, when-to-cut.
5. **Memory Relics** — relate to history, vault, pattern recall across runs.
6. **Voice Relics** — relate to cadence, narration, audio direction.
7. **Remix Relics** — relate to repurposing, variants, alternate angles.
8. **Packaging Relics** — relate to thumbnails, descriptions, CTA, posting order.
9. **Audience Relics** — relate to platform fit, niche resonance, comment energy.
10. **Archive Relics** — relate to lore, knowledge base, doc-grade scribing.

## Example relics (30)

> Each entry is `Name — Domain — Flavor ability — Limit`. Names are deliberately abstract to avoid third-party IP overlap.

### Hook
1. **Threshold Sigil** — Hook — Marks the first three seconds as a covenant. — Loses charge if the hook restates itself.
2. **Quiet Spark** — Hook — Powers low-volume openers that pull the ear in. — Useless if the source already opens loud.
3. **Mirror Question** — Hook — Reflects the viewer's own question back at them. — Cannot be used twice on the same audience.

### Source
4. **Long-Form Lantern** — Source — Reveals the strongest seam in long material. — Dim against unstructured rambles under 90 seconds.
5. **Transcript Compass** — Source — Points to the highest-energy passage. — Misreads sarcasm.
6. **Raw Anvil** — Source — Stabilizes a chaotic source for clean cuts. — Cannot fix corrupted audio.

### Caption
7. **Glyph Veil** — Caption — Renders dense lines into mobile-readable rhythm. — Drains on long monologues.
8. **Loud-Word Crown** — Caption — Highlights the one word that carries the line. — Misfires if every word is shouted.
9. **Safe-Speech Shawl** — Caption — Softens unsafe terms into broadcast-clean alternates. — Needs review before publish.

### Timing
10. **Heartbeat Coil** — Timing — Aligns cuts to the speaker's natural breath. — Fails on dubbed audio.
11. **Patience Lens** — Timing — Lets a moment land before the cut. — Costs initial attention.
12. **Storm Edge** — Timing — Ends the clip on the apex, not the resolution. — Reduces shareable closure.

### Memory
13. **Vault Echo** — Memory — Surfaces a past clip that earned attention. — Echoes weaken across months.
14. **Pattern Mantle** — Memory — Recognizes a repeated structure across runs. — Will recommend the same shape too often if unchecked.
15. **Quiet Ledger** — Memory — Holds rejected clips for second-look review. — Holds nothing for accounts that purge history.

### Voice
16. **Cadence Drum** — Voice — Marks the natural pulse the speaker is on. — Confuses overlapping speakers.
17. **Whisper Crown** — Voice — Powers low-register intimate hooks. — Will not project in noisy rooms.
18. **Ember Tongue** — Voice — Strengthens emphasis on transformation language. — Burns out on monotone delivery.

### Remix
19. **Prism Sigil** — Remix — Refracts one source into multiple angle variants. — Variants weaken if the source is thin.
20. **Counter-Echo** — Remix — Generates an opposite-angle variant for testing. — Cannot be used on closed-niche topics safely.
21. **Twin Path** — Remix — Pairs a rendered clip with a strategy-only sibling. — Both must be reviewed before posting.

### Packaging
22. **Thumb-Frame Carver** — Packaging — Marks the strongest still for thumbnails. — Misreads frames with motion blur.
23. **CTA Anvil** — Packaging — Forges a clean, single-action call to act. — Refuses dishonest CTAs.
24. **Order Compass** — Packaging — Suggests a posting order across platforms. — Stale without recent platform data.

### Audience
25. **Platform Lens** — Audience — Reveals which platform a clip fits best. — Cannot rescue a clip with no platform fit.
26. **Niche Sigil** — Audience — Tunes the hook for a defined niche. — Drowns in fully general topics.
27. **Comment Spark** — Audience — Plants a seed line that invites replies. — Works only when it is not bait.

### Archive
28. **Scribe's Quill** — Archive — Writes long-form summaries from clip packs. — Verbose without editor review.
29. **Adinkra Mark** — Archive — Tags clips with reusable lore symbols. — Symbols must be approved to avoid misuse.
30. **Silent Glass** — Archive — Stores rejected hooks for future revival. — Brittle without periodic curation.

## How relics map onto the existing system

- Relics live inside the existing **12 Signal Realms / 12 factions** of `signal-realms-scaffold.md`.
- Each relic should declare a `realm` and a `domain` once the data model is built.
- The **Seven Agents** (`lwa-web/lib/lwa-agents.ts`) act as the canonical relic stewards — Veil Oracle stewards Hook/Memory relics, Iron Seraph stewards Packaging/Remix, etc. Stewardship is lore-only until quest/agent systems exist.
- Future progression should cap relic counts per creator and require narrative quests rather than payment to unlock new ones.

## Future implementation phases (do not start any of these without sign-off)

1. **Lore phase (current).** This document. No code, no economy.
2. **Read-only phase.** A static catalog of relics on `/realm` for narrative reference.
3. **Cosmetic phase.** Visual badge / aura flavor on customized agents — earned only, no purchase.
4. **Quest phase.** Relics earned by completing creator-workflow milestones (publish N rendered clips, recover N strategy-only clips, etc.). Earned, not purchased.
5. **Trade phase (gated).** Any cross-creator visibility or tradeability requires explicit legal/compliance review and is deliberately out of scope here.

## What this doc is **not**

- Not a roadmap for a tradable token.
- Not an investment pitch.
- Not a copy of any existing protected mechanic — Devil Fruits, Stands, Personas, Quirks, Nen, Haki, etc.
- Not a guarantee of game features, virality, or revenue.

## Source-of-truth footer

- Pronunciation: **LWA** is pronounced *lee-wuh*.
- Visual identity: African / Black anime / Afro-futurist mythic sci-fi.
- Companion docs: [`signal-realms-scaffold.md`](./signal-realms-scaffold.md), [`seven-agents-customization-foundation.md`](./seven-agents-customization-foundation.md), [`master-build-bible.md`](./master-build-bible.md).
