# LWA Worlds Master Council Audit

**Audit purpose:** make the LWA Worlds report safe to keep in the repo without confusing it with executable scope.

**Repo:** `jcamacho611/lwa-app`  
**Source report:** `docs/lwa-worlds-master-council-report.md`  
**Audit date:** April 30, 2026

---

## 1. Repo Placement Audit

The report belongs under `docs/`, not `README.md`, not app code, and not deployment config.

Reason:

- It is a roadmap and strategy document.
- It contains speculative future features.
- It includes legal, market, pricing, API, and compensation claims that need verification before external use.
- It should not change runtime behavior.

Result:

- Added repo-safe strategy document at `docs/lwa-worlds-master-council-report.md`.
- Added this audit file at `docs/lwa-worlds-master-council-audit.md`.
- No backend code changed.
- No frontend code changed.
- No iOS code changed.

---

## 2. Critical Path Audit

The report contains many future systems, but the implementation order must stay narrow.

### Immediate Phase 1 Scope

Only these should be treated as immediate engineering work:

1. `FREE_LAUNCH_MODE`
2. fallback hardening
3. README polish
4. Director Brain v0 only after hardening passes
5. webhook idempotency and rate limiting

### Not Phase 1

These must not be mixed into the first hardening PR:

- marketplace schema and Stripe Connect
- Whop seller rails
- RPG / Signal Realms implementation
- blockchain / NFT / Merkle anchoring
- social posting APIs
- TikTok / Instagram publishing
- operator multi-account dashboard
- trust and safety admin queues

---

## 3. Existing Repo Alignment Notes

The current repo README describes this layout:

```text
LWA/
├── README.md
├── docs/
├── lwa-backend/
├── lwa-web/
└── lwa-ios/
```

The report originally used `apps/backend` and `apps/web` in some prompts. That does not match the visible repo README layout.

### Required correction for Codex prompts

Use:

```text
lwa-backend/
lwa-web/
lwa-ios/
```

Do not use:

```text
apps/backend
apps/web
```

unless the repo is later reorganized.

---

## 4. Codex Safety Rule

Do not paste the whole Master Council Report into Codex.

Use one scoped prompt per PR.

### First safe Codex prompt

```text
ROLE: You are a senior backend/frontend engineer on the lwa-app repo.
TASK: Implement the Day 3 hardening sprint only.

Scope:
- allowed backend path: lwa-backend/
- allowed web path: lwa-web/
- forbidden path: lwa-ios/
- do not build marketplace
- do not build Signal Realms
- do not build blockchain
- do not build social posting
- do not add new external services

Work:
1. Add FREE_LAUNCH_MODE config support.
2. Add public-launch guest behavior only when the flag is true.
3. Add anonymous IP rate limiting at RATE_LIMIT_GUEST_RPM.
4. Add NEXT_PUBLIC_FREE_LAUNCH_MODE web banner.
5. Harden the clip pipeline so download/transcribe/detect/render failures return degraded structured output instead of 500.
6. Update README only if needed to document the flag and fallback behavior.

Verification:
cd lwa-backend && python3 -m py_compile $(git ls-files '*.py')
cd lwa-backend && python3 -m unittest discover
cd lwa-web && npm run type-check
cd lwa-web && npm run lint

Output:
- files changed
- what was preserved
- verification results
- commit message
```

---

## 5. Claims Requiring Fresh Verification Before Public Use

Before this report is used with investors, public marketing, hiring, or legal/compliance discussions, verify these categories with live sources:

1. Competitor pricing and plan limits
2. OpusClip user count, clips generated, funding, and valuation
3. Stripe Connect pricing, payout fees, and 1099 handling
4. Whop fees, API capabilities, payout territories, and KYC details
5. TikTok developer review rules and posting caps
6. Instagram Graph API app review requirements and rate limits
7. YouTube API quota, upload scopes, and audit rules
8. Reddit API pricing and commercial restrictions
9. Apple NFT / IAP rule posture
10. SEC/CFTC digital-asset statements and NFT/security treatment
11. Compensation bands for hiring roles
12. Social ranking-signal claims such as LinkedIn dwell, Reels sends, and Shorts engaged views

Until verified, these should be labeled as strategic assumptions, not facts.

---

## 6. Product Scope Audit

### Strong product direction

The strongest direction in the report is:

> LWA should become the operator layer around AI clipping.

That means the clipper remains the wedge, while the defensible platform becomes:

- rendered-first clipping workflow
- Director Brain explanation layer
- per-platform packaging intelligence
- marketplace later
- Realms progression later
- operator dashboard later

### Risky product direction

The riskiest direction is trying to build too much at once:

- marketplace
- RPG
- crypto
- social APIs
- payouts
- admin queues
- public launch

These systems compound complexity and should be staged behind the working clipping core.

---

## 7. Backend Audit Notes

The report’s backend architecture is directionally strong, but implementation must follow the actual repo.

### Must preserve

- existing routes
- existing Railway deploy spine
- existing fallback/strategy-only behavior
- existing frontend/backend contract
- existing iOS folder untouched

### Must add carefully

- `FREE_LAUNCH_MODE`
- rate limit env support
- typed degraded results
- structured logging
- tests around bad URL / provider outage behavior

### Must not add in the first PR

- new database schemas for marketplace
- Stripe Connect
- Whop Connect
- OAuth providers
- NFT proof jobs
- multi-account dashboard models

---

## 8. Frontend Audit Notes

### Safe first frontend addition

Only the free-launch banner belongs in the first hardening PR.

### Later frontend additions

- marketplace pages
- `/realm` pages
- `/dashboard` operator view
- wallet display
- proof tabs

These should be separate PRs.

---

## 9. Legal / Compliance Audit Notes

This report includes helpful guardrails, but none of it is legal advice.

Before shipping marketplace, payouts, crypto, or earnings claims, get human legal review for:

- Terms of Service
- Privacy Policy
- Refund Policy
- DMCA policy
- FTC earnings / endorsement disclosures
- Stripe / Whop seller obligations
- NFT/relic copy and restrictions
- Apple App Store implications if iOS is ever reintroduced

---

## 10. Decision

The report is useful and should stay in the repo as a strategic reference.

The implementation path should be:

1. Hardening sprint
2. Director Brain v0
3. webhook/rate-limit foundation
4. marketplace schema only after core stability
5. Signal Realms after marketplace events exist
6. blockchain only after product-market signal and legal approval

---

## Final Audit Summary

**Approved for docs:** yes.  
**Approved for direct Codex execution as a whole:** no.  
**Approved first engineering scope:** Day 3 hardening only.  
**Paths touched by this docs addition:** `docs/` only.  
**Runtime behavior changed:** no.
