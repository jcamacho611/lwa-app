# Seven Agents Customization Foundation

## Purpose

The Seven Agents are the base model foundation for future LWA creator identity, progression, and customization. They are not just decorative characters, and they are not live autonomous operators.

Each agent can become a future starting model that a creator customizes into their own LWA identity while the Clip Engine remains the core product surface.

## Current shipping state

- Agent metadata exists in `lwa-web/lib/lwa-agents.ts`.
- `/realm` displays the Seven Agents as AI guides and future base models.
- The metadata is future-ready only.
- No avatar editor is live.
- No playable 3D avatar is live.
- No wallet, NFT, token, payout, or game economy is live.
- No income or performance outcome is guaranteed.

## Supported future slots

The current foundation reserves these customization slots:

- name
- realm
- armor
- aura
- sigil
- hair
- mask
- palette
- creatorClass

Future product work can expand this into creator handles, factions, marketplace roles, unlocked cosmetics, and companion behavior only after the account, entitlement, asset, moderation, and claim-safety systems are ready.

## Asset conventions

Future agent assets should live under:

```text
lwa-web/public/brand/agents/{agent-id}/
```

Reserved file names:

- `portrait.png`
- `model-sheet.png`
- `symbol.png`
- `rig.glb`

These paths are declared as metadata only. Frontend surfaces should not render them until the files exist and image/CSP behavior has been smoke-tested.

## Claim-safety boundaries

Do not claim any of the following until implemented, verified, and legally reviewed where needed:

- full avatar editor
- playable 3D avatars
- NFT or token economy
- wallet collection
- paid game economy
- marketplace payouts
- social posting automation
- investment returns
- guaranteed income
- guaranteed virality

Allowed language:

- future base models
- creator identity foundation
- planned customization slots
- roadmap-only avatar customization
- cosmetic/progression foundation
- human review required

## Next implementation gate

The next real slice is not a 3D editor. It is a schema-safe profile draft:

- creator display name
- selected base agent
- selected realm
- selected palette
- selected creator class
- local preview only
- no wallet, payment, payout, or NFT fields
- clear "future customization preview" label
