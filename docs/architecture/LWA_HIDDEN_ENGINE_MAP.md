# LWA Hidden Engine Map

LWA should be coded as engines, events, states, missions, proof, and rewards. The visible app can still be web plus backend plus realm, but the product should behave like one connected system.

This map defines the hidden engines LWA needs. The first implementation slice should stay frontend-safe: Experience State, Mission Orchestration, Asset Registry visibility, and Recovery path framing. Backend ownership comes later where money, rights, provider costs, and persistence are involved.

## 1. Experience State Engine

- Purpose: Controls the current product state and makes Lee-Wuh, UI, missions, rewards, and the game layer react together.
- Why LWA needs it: Without a shared state, generate, marketplace, proof, and realm surfaces feel disconnected. With shared state, Lee-Wuh becomes the living interface.
- Frontend responsibility: Hold local state transitions, show guidance, update Lee-Wuh reactions, surface next actions, and keep results readable.
- Backend responsibility later: Emit durable job, proof, render, entitlement, and recovery events that the frontend can trust.
- First safe implementation slice: Add a typed local event/state reducer and demo panel under `/lee-wuh/assets`.
- Launch risk if ignored: Lee-Wuh remains decorative and users do not understand what to do after generation, strategy-only fallback, export, or proof.

## 2. Mission Orchestration Engine

- Purpose: Chooses the next best user action and turns creator work into missions.
- Why LWA needs it: Users need guided progression from source to clips, proof, marketplace, realm, and rewards.
- Frontend responsibility: Show the active mission, complete starter missions from local events, and display reward language without claiming payout automation.
- Backend responsibility later: Persist mission completion, prevent reward abuse, and connect missions to proof, campaigns, marketplace eligibility, and account history.
- First safe implementation slice: Add local starter missions for rendered clips, proof/export, marketplace opening, realm entry, and recovery.
- Launch risk if ignored: The game layer becomes a detached novelty instead of the product's operating system.

## 3. Asset Registry Engine

- Purpose: Tracks Lee-Wuh character, sword, background, aura, GLB, Blender, Spine, and runtime assets.
- Why LWA needs it: Character, world, sword, and aura assets must remain separated so the frontend can animate and compose them independently.
- Frontend responsibility: Display which assets are runtime-safe, source-only, production candidates, fallback assets, or future rigging inputs.
- Backend responsibility later: Validate uploaded/generated asset metadata, store versions, expose asset health, and prevent unsafe runtime usage.
- First safe implementation slice: Keep the current Lee-Wuh visual asset registry and expose it through the hidden engine map panel.
- Launch risk if ignored: The team will ship baked screenshots, duplicate asset paths, or runtime surfaces that cannot animate.

## 4. Recovery Engine

- Purpose: Turns failures, strategy-only results, missing renders, provider errors, and export issues into recoverable user paths.
- Why LWA needs it: LWA must preserve strategy output when rendering or providers fail.
- Frontend responsibility: Explain recovery paths such as export strategy package, retry render, use fallback, save proof idea, or continue to marketplace.
- Backend responsibility later: Provide recovery codes, rerender endpoints, queue retry limits, provider downgrade hints, and export recovery artifacts.
- First safe implementation slice: Add a local `RECOVERY_AVAILABLE` event and mission so Lee-Wuh can guide the user without backend changes.
- Launch risk if ignored: Users see dead errors even when LWA has useful strategy output.

## 5. Reward Ledger Engine

- Purpose: Tracks XP, badges, relics, completed missions, unlocks, and creator progression.
- Why LWA needs it: Rewards must feel real and consistent before any money or crypto layer exists.
- Frontend responsibility: Show safe local/demo rewards and avoid financial or payout claims.
- Backend responsibility later: Persist a ledger, make rewards idempotent, enforce anti-spam rules, and connect rewards to accounts.
- First safe implementation slice: Let missions return local reward payloads only.
- Launch risk if ignored: Users will feel the realm progression is fake or reset-prone.

## 6. Proof / Trust Engine

- Purpose: Records what was generated, copied, exported, saved, submitted, or recovered.
- Why LWA needs it: Marketplace, campaigns, reputation, disputes, and user confidence require a history of actions and artifacts.
- Frontend responsibility: Label proof actions clearly and avoid claiming verified submissions unless the backend confirms them.
- Backend responsibility later: Persist proof events, source references, artifact hashes or manifests, timestamps, and audit trails.
- First safe implementation slice: Keep proof as a mission trigger, not a durable claim.
- Launch risk if ignored: Campaign and marketplace trust will break when users need to prove what happened.

## 7. Cost Governance Engine

- Purpose: Controls provider cost, credits, free fallbacks, render limits, and plan gates.
- Why LWA needs it: AI, render, video, and storage calls can burn money if they are not governed.
- Frontend responsibility: Reflect plan limits, show downgrade or fallback paths, and avoid promising expensive output.
- Backend responsibility later: Make all cost decisions server-side, enforce quotas, route to fallback, and log spend.
- First safe implementation slice: Document the engine and keep frontend language compatible with future credit gates.
- Launch risk if ignored: Users can trigger expensive work without enough business controls.

## 8. Provider Routing Engine

- Purpose: Chooses mock, free, premium, render, video, image, text, or local deterministic providers based on need and cost.
- Why LWA needs it: Director Brain decides what should happen. Provider routing decides what executes it.
- Frontend responsibility: Display provider-neutral statuses such as strategy-only, rendering, rendered, or fallback.
- Backend responsibility later: Route calls by plan, cost, health, reliability, latency, and output type.
- First safe implementation slice: Keep the map explicit without wiring provider decisions into the frontend.
- Launch risk if ignored: Provider failures leak into product UX and the system becomes expensive to operate.

## 9. Quality Scoring Engine

- Purpose: Scores hook strength, platform fit, retention, caption quality, render readiness, marketplace fit, brand safety, posting priority, and confidence.
- Why LWA needs it: LWA must decide what to post first, recover later, export, block, or send to marketplace.
- Frontend responsibility: Show score transparency without overwhelming users or inventing unsupported guarantees.
- Backend responsibility later: Use Attention Compiler output, feedback, proof, and performance logs to calibrate decisions.
- First safe implementation slice: Document the engine and keep score language aligned with existing `score_breakdown`.
- Launch risk if ignored: LWA returns clips without a defensible reason for rank or next action.

## 10. Rights / Safety Engine

- Purpose: Checks source rights, posting safety, campaign eligibility, claims, marketplace risk, and payout safety.
- Why LWA needs it: Money and marketplace workflows need rights safety before scale.
- Frontend responsibility: Avoid claims about bypassing private video, direct posting, payout automation, or guaranteed campaign eligibility.
- Backend responsibility later: Classify source risk, enforce allowed flows, attach warnings, and block unsafe marketplace proof.
- First safe implementation slice: Document the engine and keep claim-safe public copy.
- Launch risk if ignored: The company takes avoidable legal, platform, and marketplace trust risk.

## 11. Game Economy Balancing Engine

- Purpose: Balances XP, missions, relic rarity, realm progression, streaks, anti-spam, and unlock pacing.
- Why LWA needs it: Wallet and credits are not game progression. Game economy keeps the realm useful and paced.
- Frontend responsibility: Display progression and rewards in a way that does not imply monetary value.
- Backend responsibility later: Persist progression, tune XP, prevent farming, and balance unlocks over time.
- First safe implementation slice: Keep starter reward values local and clearly non-monetary.
- Launch risk if ignored: Users progress too fast, get bored, or exploit rewards.

## 12. Personalization / Memory Engine

- Purpose: Learns user style, niche, platform preferences, successful outputs, and Lee-Wuh guidance behavior.
- Why LWA needs it: LWA should stop feeling generic after repeated use.
- Frontend responsibility: Use local preferences only when safe and make personalization transparent.
- Backend responsibility later: Store user preferences, performance patterns, saved styles, and successful hooks under account controls.
- First safe implementation slice: Document the engine and leave persistence for a later backend-backed slice.
- Launch risk if ignored: Every user gets the same guidance regardless of platform, niche, history, or results.

## First Build Order

1. Experience State Engine
2. Mission Orchestration Engine
3. Asset Registry Engine
4. Recovery Engine

These four unlock the site, game, and Lee-Wuh experience without touching payment logic, payout logic, crypto, or backend contracts.
