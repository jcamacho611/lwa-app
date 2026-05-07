# LWA Public Demo Loop Spec

**Status:** Foundation slice — additive, isolated, no backend dependency.
**Branch:** `claude/public-demo-loop`
**Owner:** Public demo lane (parallel to Brain Panel repair).

---

## 1. Why this exists

A first-time visitor — creator, operator, brand buyer, or investor — must understand LWA in 60 seconds without reading documentation. Today the platform has the engines (event bridge, mission engine, recovery engine, experience state, asset registry, signal sprint runner, clip studio bridge) but no narrated path that pulls them into a single legible loop. The Public Demo Loop is that path.

It is intentionally **frontend-only**, **no auth**, **no backend writes**, **no payments**, **no crypto**. It explains the product. It does not run it.

## 2. The 60-second first session

```
0–10s   landing                Lee-Wuh appears. One sentence. One CTA: "Begin."
10–20s  first_mission          Lee-Wuh issues a single mission: add a source.
20–30s  source_added           Visitor sees the source surface light up.
30–40s  clips_ready            Ranked clips appear: rendered + strategy-only.
40–45s  recovery_available     A strategy-only clip shows its recovery path.
45–50s  proof_saved            One clip is saved as proof.
50–60s  signal_sprint          A 3-choice creator skill prompt appears.
60s+    marketplace_teaser     Marketplace is *named*, not opened.
return  return_loop            Lee-Wuh tells the visitor what to do next.
```

Every stage exposes one Lee-Wuh line, one user-visible surface, one user action, and one named engine connection.

## 3. How Lee-Wuh guides

Lee-Wuh is **not decoration**. Per stage, Lee-Wuh provides:

- a 6–14 word **judgment line** (Lee-Wuh voice, never marketing copy),
- a **next-action hint** the panel renders as a button label,
- a **stage-specific rationale** the visitor can expand if curious.

Lee-Wuh never asks for credentials, payments, or installation. Lee-Wuh is a guide, not a sales agent.

## 4. How the engines connect (named, not coupled)

The Public Demo Loop **names** which production engine each stage will eventually delegate to. It does not import them. This isolation is intentional so the demo cannot be broken by upstream engine changes.

| Stage | Engine connection (future, named only) |
|---|---|
| `landing` | Lee-Wuh asset registry (visual identity surface) |
| `first_mission` | Mission engine (`lwa-mission-engine.ts`) |
| `source_added` | Source contract / upload route (read-only display) |
| `clips_ready` | Clip studio event bridge (`clip-studio-event-bridge.ts`) |
| `recovery_available` | Recovery engine (`lwa-recovery-engine.ts`) |
| `proof_saved` | Proof engine + LWA event bridge |
| `signal_sprint` | Signal Sprint game (decision variant — local only) |
| `marketplace_teaser` | Marketplace engine (named, not opened) |
| `return_loop` | Experience state machine |

When any engine becomes production-ready, the demo panel can subscribe to its events without changing structure.

## 5. What is live now vs. placeholder

| Layer | Status |
|---|---|
| Stage script + Lee-Wuh lines | **live (local data)** |
| Personas (creator_beginner, creator_operator, brand_buyer, investor_demo) | **live (local data)** |
| Signal Sprint decision prompts | **local_demo** (deterministic, no backend) |
| Readiness checklist | **live (local data)** |
| Engine subscriptions | **placeholder** (named, not wired) |
| Real clip generation | **disabled** in demo |
| Proof save (real) | **disabled** in demo |
| Marketplace open | **disabled** (teaser only) |
| Posting / social | **disabled** |
| Payments / crypto / payouts | **disabled — never enabled in this lane** |

## 6. What is intentionally disabled

The Public Demo Loop must never:

- mint, transfer, or display real wallet balances,
- initiate payouts, withdrawals, or marketplace purchases,
- run hidden mining or background compute,
- post to TikTok / Instagram / X / YouTube / LinkedIn / Whop on the visitor's behalf,
- claim marketplace earnings or creator splits,
- mutate backend state (no `POST`, `PUT`, `DELETE`),
- read auth tokens, session cookies, or user PII,
- import from `lib/lwa-brain-engine.ts` while Windsurf is repairing it.

These rules are enforced by the absence of the relevant imports in `lwa-public-demo-loop.ts` and `LwaPublicDemoLoopPanel.tsx`. There are no fetch calls. There are no payment SDKs.

## 7. Persona narratives

Four personas read the same nine stages with different framing:

- **creator_beginner** — emphasis on *first mission* and *clip ready* moments. Lee-Wuh tone is encouraging.
- **creator_operator** — emphasis on *recovery* and *proof saved* moments. Tone is operational.
- **brand_buyer** — emphasis on *marketplace teaser* and *return loop*. Tone is procurement-grade.
- **investor_demo** — emphasis on the full nine-stage arc, with the readiness checklist surfaced. Tone is calm and exact.

The same panel renders all four. The persona switch only changes the rationale and the stage emphasis — never the underlying script.

## 8. Readiness checklist

The panel renders a small readiness grid. Each check is one of:

- `live` — confirmed working in this slice,
- `local_demo` — works locally, no backend,
- `placeholder` — named, not yet wired,
- `disabled` — out of scope for the demo lane,
- `blocking` — must be resolved before public demo ships.

The helper `getBlockingDemoChecks()` returns only `blocking` items. If the array is empty, the demo is ready to share publicly.

## 9. Next slices after this

In rough priority:

1. Wire Lee-Wuh asset registry to the `landing` stage so the visual is brand-correct out of the box.
2. Replace `clips_ready` placeholder with a read-only sample of the Clip Studio event bridge feed (still no backend mutation).
3. Add a second Signal Sprint round (multi-prompt decision sprint, still local only).
4. Add an "investor mode" toggle that sets persona to `investor_demo` and shows the readiness grid first.
5. Add a `?stage=` query param so the team can deep-link to a specific moment for review.
6. After Windsurf finishes Brain Panel: optional read-only pull of a single brain insight per stage. Strictly read-only.

## 10. Out of scope (explicit)

- editing or importing `lwa-web/components/brain/LwaBrainEnginePanel.tsx`,
- editing `lwa-web/app/command-center/page.tsx`,
- editing or importing `lwa-web/lib/lwa-brain-engine.ts`,
- any change to `lwa-ios/`,
- any change to backend routes, models, or `/generate` behavior,
- any change to `.env*` files,
- any payment, payout, marketplace, or crypto integration.
