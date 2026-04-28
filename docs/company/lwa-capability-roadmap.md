# LWA Capability Roadmap

## Purpose
This is the company capability truth table for Issue #21. It keeps product, engineering, sales, and Railway planning aligned on what is live, what is partial, what is only a foundation, and what must not be claimed.

Status labels:

- `LIVE`: implemented enough to claim carefully as part of the product.
- `PARTIAL`: works in some form, but needs hardening, coverage, or UX polish.
- `FOUNDATION`: backend data, docs, or primitives exist, but the full capability is not shipped.
- `PLANNED`: intended near-term product work.
- `FUTURE`: possible later direction, not current roadmap-critical work.
- `INTENTIONALLY UNSUPPORTED`: a permanent boundary.
- `DO NOT CLAIM`: not implemented and not safe to market.

## Claim Safety

Allowed public claims:

- helps prepare clips
- helps rank moments
- returns hooks, captions, timestamps, packaging copy, and score context
- returns rendered clips when rendering succeeds
- keeps a strategy-only fallback when rendering is unavailable
- creates creator-ready clip packages
- supports manual campaign preparation
- supports upgrade/access flows through Whop links or foundations where wired

Forbidden public claims:

- guaranteed viral performance, views, revenue, or payout
- direct TikTok, Instagram, or YouTube posting
- automatic Whop campaign submission
- campaign payout tracking
- private or login-gated video bypass
- complete CapCut/editor replacement
- unlimited clips
- full account/workspace/team system
- Google Drive, Dropbox, Cloudinary/R2, Redis, Postgres, workers, scheduler, or webhooks as live production services unless separately implemented and verified

## Core Clipping

| Capability | Status | Public claim | Current truth | Missing piece | Next step | Owner | Railway impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Public video URL ingestion | PARTIAL | Helps process public video URLs into clip packages. | Backend supports public URL style generation paths and uses source URL fields, but source-specific failures still need hardening. | More validation, clearer source errors, and broader source compatibility. | Harden source error responses and keep fallback output usable. | Backend Systems Lead | Existing backend only. |
| yt-dlp ingestion | PARTIAL | Uses public-source ingest where available. | Backend stack includes yt-dlp as part of video processing assumptions. | Production validation across real platforms and failure cases. | Add source diagnostics without implying private bypass. | Video Processing Lead | Existing backend; `lwa-worker-ingest` only if downloads block API. |
| FFmpeg clip cutting | PARTIAL | Can render clips when local processing succeeds. | FFmpeg is part of backend processing and render readiness, but rendering must remain non-mandatory. | More render profiles, retries, and failure reporting. | Keep FFmpeg failures recoverable and strategy-only output intact. | Video Processing Lead | Existing backend; `lwa-worker-render` later if CPU blocks API. |
| Vertical 9:16 output | PARTIAL | Prepares short-form oriented clips and packaging. | Vertical output is a product target, but profile completeness varies by render path. | Export profile validation and consistent render dimensions. | Define verified vertical export profiles. | Video Processing Lead | Existing backend now; render worker later. |
| Rendered asset serving | PARTIAL | Returns rendered asset links when rendering succeeds. | Backend distinguishes rendered assets from strategy-only output. | Storage lifetime clarity and production volume monitoring. | Keep generated asset retention verified on Railway. | Backend Systems Lead | Existing backend and Railway volume. |
| Strategy-only fallback | LIVE | Keeps useful strategy output when rendering is unavailable. | Fallback clip packages, hooks, timestamps, copy, and recovery states are core product behavior. | Ongoing copy and score quality improvements. | Preserve fallback in every generation and client flow. | AI Intelligence Lead | Existing backend only. |
| Generated asset retention | PARTIAL | Generated assets may be retained temporarily and cleaned up automatically. | Retention path exists, but Railway behavior still needs production verification. | Monitoring and scheduled cleanup if startup cleanup is insufficient. | Verify cleanup logs, protected paths, and volume usage. | Security / Privacy Lead | Existing backend now; `lwa-scheduler` only if timed cleanup is needed. |

## AI / Intelligence

| Capability | Status | Public claim | Current truth | Missing piece | Next step | Owner | Railway impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Clip scoring | PARTIAL | Ranks clips by predicted retention behavior. | Attention scoring exists and must avoid flat fallback scores. | More real performance feedback and score calibration. | Keep score distribution varied and explainable. | AI Intelligence Lead | Existing backend only. |
| Confidence score | PARTIAL | Shows confidence/score context where surfaced. | Backend has score fields, but client transparency is still evolving. | Consistent UI display and definitions. | Align score labels across web/iOS. | Frontend Lead | Existing frontend/backend. |
| Hook generation | LIVE | Returns hook options for clips. | Hook variants are part of generation output and fallback strategy. | Stronger platform/category tuning. | Keep three hook variants where Attention Compiler touches output. | AI Intelligence Lead | Existing backend only. |
| Caption generation | PARTIAL | Returns captions or caption-ready copy. | Caption packaging exists; advanced burn-in styles are not complete. | Style presets, burn-in validation, and export profiles. | Connect caption presets to rendered outputs. | Video Processing Lead | Existing backend now; render worker later. |
| Thumbnail text suggestions | PARTIAL | Suggests thumbnail text and packaging angles. | Strategy output can include thumbnail text suggestions. | Preview rendering and design validation. | Add thumbnail preview only when render/export path supports it. | Muse-01 Creative Systems Director | Existing frontend/backend; render worker later for generated thumbnails. |
| CTA suggestions | PARTIAL | Suggests posting CTA copy. | Packaging guidance includes CTA-style output. | Platform-specific rules and claim-safe review. | Keep CTA copy inside claim-safe language. | Sales Enablement Lead | Existing backend only. |
| Why-this-matters reasoning | FOUNDATION | Explains why a clip may work when score transparency is surfaced. | Score breakdown/intelligence foundations exist, but UI explanation is not fully shipped everywhere. | Web/iOS score panels and copy polish. | Surface concise score reasons in the web flow first. | AI Intelligence Lead | Existing frontend/backend. |
| Attention Compiler / viral signal scoring | PARTIAL | Ranks moments using retention signals, not topic keywords alone. | Viral signal rules and Attention Compiler are connected in backend intelligence work. | Wider verification against real clips and frontend transparency. | Keep compiler loaded, nonfatal, and connected to generation results. | AI Intelligence Lead | Existing backend only. |
| Fallback heuristics | LIVE | Provides useful local fallback when providers are unavailable. | Fallback behavior is a protected product law. | Better quality and clearer operator telemetry. | Improve fallback quality without making AI providers mandatory. | AI Intelligence Lead | Existing backend only. |
| Score transparency | FOUNDATION | Score transparency is being built into ranked packages. | Backend fields exist; frontend/iOS display is not complete everywhere. | User-facing score panels and safe language. | Show signal breakdowns in the web result UI. | Frontend Lead | Existing frontend/backend. |

## Output / Export

| Capability | Status | Public claim | Current truth | Missing piece | Next step | Owner | Railway impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Raw clip assets | PARTIAL | Provides clip assets when rendering succeeds. | Asset links can be returned for rendered outputs. | Retention policy clarity and more robust asset indexing. | Keep links honest and mark missing assets as strategy-only. | Video Processing Lead | Existing backend volume. |
| Edited clip assets | PARTIAL | Creates edited/rendered clips when processing succeeds. | Rendered output is supported but not guaranteed. | More reliable render jobs, retries, and profile control. | Add recoverable render status everywhere. | Video Processing Lead | Existing backend now; `lwa-worker-render` later. |
| Export bundle metadata | PARTIAL | Provides structured export/package metadata. | Export bundle contract exists in docs and backend work. | Full client surfacing and broader test coverage. | Keep metadata aligned with generated clip fields. | Backend Systems Lead | Existing backend only. |
| Package copy | LIVE | Returns creator-ready package copy. | Hooks, captions, CTAs, and packaging guidance are central fallback outputs. | More brand/platform tuning. | Keep package copy claim-safe. | Sales Enablement Lead | Existing backend only. |
| Thumbnails | FOUNDATION | Suggests thumbnail direction; generated thumbnails are not fully shipped. | Thumbnail text/rules may exist; full rendered thumbnail pipeline is not proven. | Thumbnail rendering and storage. | Treat thumbnails as suggestions until generated files are verified. | Muse-01 Creative Systems Director | `lwa-worker-render` later if generated at scale. |
| Burned-in captions | PLANNED | Advanced burned-in caption styles are evolving. | Caption artifacts may exist, but complete styled burn-in is not done. | FFmpeg caption style presets and export profile selection. | Build after render stability and retention are verified. | Video Processing Lead | `lwa-worker-render` when heavy. |
| Caption style presets | FOUNDATION | Caption style guidance may be used for packaging. | Viral intelligence seed data can define presets; full UI/render connection is incomplete. | Web selector and render implementation. | Connect preset choice to export output. | Frontend Lead | Existing frontend/backend; render worker later. |
| Export profiles | PLANNED | Export profile controls are future work. | No claim-safe full profile system yet. | Platform profile definitions and render validation. | Define MVP profiles after vertical render path is stable. | Video Processing Lead | Existing backend now; render worker later. |
| ZIP export | FOUNDATION | Export bundle foundation exists; ZIP export should be claimed only if verified in the target flow. | Docs/backend foundation exists, but public UX must not imply universal ZIP export unless surfaced and tested. | UI wiring, asset inclusion rules, and retention-safe links. | Verify export bundle flow before public claim. | Backend Systems Lead | Existing backend only unless large bundles require worker. |

## Source Ingestion

| Capability | Status | Public claim | Current truth | Missing piece | Next step | Owner | Railway impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Public URL input | LIVE | Users can start from a public URL where supported. | Source URL flow is core to current generation paths. | More source validation and clearer unsupported-source messages. | Harden error handling. | Backend Systems Lead | Existing backend. |
| Upload endpoint | PARTIAL | Upload-first workflow is a core direction. | Upload support exists or is being connected across clients, but should stay honest per surface. | Production validation, file size handling, and retention rules. | Keep upload flow protected and fallback-safe. | Backend Systems Lead | Existing backend; ingest worker later if volume requires. |
| Local uploaded file generation | PARTIAL | Uses user-provided media where supported. | Upload-first/local fallback is a core product law. | More UX polish and source-type coverage. | Preserve upload-first path before adding external imports. | Chief Product Architect | Existing backend/frontend. |
| Google Drive import | DO NOT CLAIM | Not supported today. | No verified Drive import capability. | OAuth/import integration, permissions, and storage rules. | Defer until upload-first flow is stable. | Chief Product Architect | No service now; ingest worker/Postgres later if built. |
| Dropbox import | DO NOT CLAIM | Not supported today. | No verified Dropbox import capability. | OAuth/import integration, permissions, and storage rules. | Defer until upload-first flow is stable. | Chief Product Architect | No service now; ingest worker/Postgres later if built. |
| Social platform import | FOUNDATION | Public URL workflows may work where supported; account imports are not live. | yt-dlp/public source processing is not the same as authorized platform import. | OAuth, compliance, and connector-specific handling. | Keep public URL wording distinct from account import. | Security / Privacy Lead | Existing backend now; ingest worker later. |
| Private/login-gated videos | INTENTIONALLY UNSUPPORTED | Use public sources or your own uploaded media. Private bypass is not supported. | LWA must not bypass login-gated or private platforms. | Authorized import flows only. | Expand compliant upload/import paths, not bypasses. | Security / Privacy Lead | No service for bypass; ingest worker only for authorized imports. |

## Monetization / Whop

| Capability | Status | Public claim | Current truth | Missing piece | Next step | Owner | Railway impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Whop storefront | FOUNDATION | Users may be pointed to Whop for purchase/access where configured. | Whop direction exists, but native verification is not live by default. | Final storefront links, plan mapping, and verification. | Keep copy as purchase/access, not automation. | Monetization / Whop Lead | Existing frontend/backend. |
| Upgrade link | PARTIAL | Upgrade paths can point users to configured purchase flow. | Frontend/product may expose upgrade CTAs, but entitlement truth stays backend-owned. | Consistent plan copy and safe fallback when not configured. | Keep upgrade links configurable. | Monetization / Whop Lead | Existing frontend/backend. |
| Free/pro/scale plans | FOUNDATION | Usage tiers are being structured. | Server-side plan foundations exist, but production plan enforcement needs validation. | Plan copy, entitlement persistence, and abuse hardening. | Verify quota behavior in production. | Monetization / Whop Lead | Existing backend; Postgres later. |
| API-key plan unlock | PARTIAL | API-key based access can unlock higher plan behavior where configured. | API-key plan unlock foundation exists. | Production key rotation, logging safety, and Whop mapping. | Harden secret handling and operator docs. | Backend Systems Lead | Existing backend. |
| Daily quotas | PARTIAL | Usage limits protect the service. | Server-side quota tracking exists in foundation form. | Abuse hardening, durable shared state, and user-facing errors. | Validate quota-exceeded response shape. | Monetization / Whop Lead | Existing backend; Redis/Postgres later if multi-instance. |
| Feature flags | FOUNDATION | Some features may be gated by plan or config. | Feature access foundations exist, but not a full product flag platform. | Admin tooling and durable flag state. | Keep feature checks backend-owned. | Chief Product Architect | Existing backend; Postgres later. |
| Whop membership verification | FOUNDATION | Whop verification is a foundation, not a live guarantee. | Disabled-by-default verification status exists in docs/backend direction. | Live token verification and end-to-end tests. | Build only after config and failure states are safe. | Monetization / Whop Lead | Existing backend now; webhooks/Postgres later. |
| Whop webhooks | DO NOT CLAIM | Not live. | No claim-safe webhook automation yet. | Signature verification, replay handling, event store, and entitlement sync. | Add only with real Whop webhook requirements. | Monetization / Whop Lead | `lwa-webhooks` later. |
| Campaign payout tracking | DO NOT CLAIM | Not supported. | No payout tracking implementation. | Whop campaign APIs, payout model, audit logs, and user states. | Do not build until campaign workflow is real and compliant. | Monetization / Whop Lead | Postgres/webhooks later only if justified. |

## Campaign Workflow

| Capability | Status | Public claim | Current truth | Missing piece | Next step | Owner | Railway impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Campaign packaging | FOUNDATION | Helps prepare campaign-style clip packages manually. | Campaign packaging foundations exist, but native campaign automation is not live. | UI clarity, requirement validation, and real campaign data. | Keep campaign mode manual and claim-safe. | Monetization / Whop Lead | Existing backend/frontend. |
| Manual campaign checklist | FOUNDATION | Provides manual review guidance where surfaced. | Campaign readiness rules exist as a foundation. | Frontend checklist display and rule validation. | Surface manual checklist before automation. | Frontend Lead | Existing frontend/backend. |
| Allowed platform notes | FOUNDATION | Can include platform-fit notes. | Platform intelligence exists in seed/registry layers. | More client display and compliance review. | Keep platform notes advisory. | AI Intelligence Lead | Existing backend. |
| Campaign fit score | FOUNDATION | Can evaluate campaign readiness as guidance, not payout prediction. | Campaign fit foundations exist but should not imply submission or payout. | More rules, UI, and real campaign input. | Use fit score for manual review only. | AI Intelligence Lead | Existing backend. |
| Whop campaign browsing | DO NOT CLAIM | Native Whop campaign browsing is future work. | Not implemented as a live product capability. | Whop API integration, verification, access mapping. | Build after Whop verification foundation. | Monetization / Whop Lead | `lwa-webhooks`/Postgres later. |
| Campaign submission automation | DO NOT CLAIM | Submission stays manual. | No automatic submission workflow. | Submission API, review state, audit trails. | Do not build until campaign import and review are stable. | Monetization / Whop Lead | `lwa-webhooks`, Postgres, Redis later. |
| Payout status tracking | DO NOT CLAIM | Not supported. | No payout state source or ledger. | Whop payout API, durable records, reconciliation. | Keep out of public copy. | Monetization / Whop Lead | Postgres/webhooks later if built. |

## Frontend / Web

| Capability | Status | Public claim | Current truth | Missing piece | Next step | Owner | Railway impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Source input | LIVE | Users can start a clip run from the web app. | Web source input is a core surface. | More validation and upload polish. | Keep first-use generate flow simple. | Frontend Lead | Current frontend. |
| Rendered lane | PARTIAL | Rendered clips are separated when available. | Rendered-vs-strategy distinction is protected. | Consistency across every result state. | Keep rendered labels tied to backend truth. | Muse-01 Creative Systems Director | Current frontend/backend. |
| Strategy lane | PARTIAL | Strategy-only outputs remain visible when rendering is unavailable. | Strategy fallback is a core lane. | UX polish and clearer recovery actions. | Avoid hiding fallback behind render failures. | Frontend Lead | Current frontend/backend. |
| Lead best clip | PARTIAL | Best clip first ranking is supported. | Ranking fields exist; UI should keep rank 1 obvious. | Score explanation and tie handling. | Display best clip with backend rank truth. | Frontend Lead | Current frontend/backend. |
| Packaging rail | FOUNDATION | Packaging copy can be shown alongside clips. | Packaging output exists; rail polish may vary. | Feature-complete UI and mobile layout. | Connect package copy consistently. | Muse-01 Creative Systems Director | Current frontend. |
| History/recent runs | FOUNDATION | Recent run/history foundation exists where surfaced. | Durable cloud history is not fully implemented. | Persistence, auth, and user scoping. | Keep history local/foundation until Postgres exists. | Frontend Lead | Current frontend/backend; Postgres later. |
| Source selector | PLANNED | Source selection is evolving. | Multiple source modes should not imply unsupported imports. | UI gating and capability-aware labels. | Show only supported source types. | Frontend Lead | Current frontend. |
| Upload UI | PARTIAL | Upload-first workflow is a primary direction. | Upload UI may exist, but must match backend capability. | File states, errors, and retention copy. | Polish upload UX without claiming unsupported imports. | Frontend Lead | Current frontend/backend. |
| Caption style selector | PLANNED | Advanced caption style controls are future work. | Presets are not fully connected end-to-end. | Selector UI and render binding. | Build after caption presets are connected. | Muse-01 Creative Systems Director | Current frontend; render worker later. |
| Thumbnail preview | PLANNED | Thumbnail preview is future/polish unless verified. | Thumbnail text suggestions are safer than generated previews today. | Rendered preview generation and asset storage. | Ship only when generated preview path is real. | Muse-01 Creative Systems Director | Render worker later if generated. |
| Export profile controls | PLANNED | Export profile controls are future work. | Full profile system is not yet public. | Backend profile support and UI controls. | Add after render/export profile validation. | Frontend Lead | Current frontend/backend; render worker later. |
| Agency mode | FUTURE | Not supported as full agency/team mode today. | Full workspace/team/account model is not implemented. | Accounts, workspaces, roles, billing, shared history. | Defer until core clipping and entitlements are stable. | Chief Product Architect | Postgres later. |

## iOS

| Capability | Status | Public claim | Current truth | Missing piece | Next step | Owner | Railway impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Paste URL | PARTIAL | iOS can connect to backend URL generation where implemented. | iOS exists, but this docs track did not verify current app behavior. | Client verification and safe decoding. | Do not change iOS in this issue. | iOS Lead | Existing backend only. |
| Generate/poll | PARTIAL | iOS generation/polling depends on backend contracts. | Backend job endpoints are protected; iOS behavior needs separate verification. | Error states and schema-safe decoding. | Preserve API contracts. | iOS Lead | Existing backend. |
| Preview/open/share clips | FOUNDATION | iOS clip preview/share is product direction. | Must not be overclaimed without app verification. | Rendered asset handling and share sheet validation. | Verify in iOS track only. | iOS Lead | Existing backend. |
| Local history | FOUNDATION | Local history may exist or be planned, not cloud team history. | Cloud history requires auth/persistence. | Persistence policy and sync model. | Keep local vs cloud history language clear. | iOS Lead | No new service now. |
| Settings/API URL | FOUNDATION | Settings can support backend configuration where present. | Needs separate iOS verification. | UX polish and environment safety. | Leave iOS untouched for Issue #21. | iOS Lead | Existing backend. |
| Upload from Photos/Files | PLANNED | Upload from device is planned/future unless verified. | This docs task did not validate iOS upload. | File picker, upload endpoint, progress, and errors. | Build/verify in iOS track only. | iOS Lead | Existing backend; ingest worker later. |
| In-app purchase | DO NOT CLAIM | Not supported as live. | App Store-safe monetization is not implemented here. | IAP products, entitlement sync, policy review. | Defer until product and compliance plan are ready. | Monetization / iOS Lead | Postgres/webhooks later if built. |
| App Store-safe monetization copy | FOUNDATION | Copy must avoid fake guarantees and unsupported automation. | Claim-safety rules exist in this roadmap. | Store listing review and implementation verification. | Keep copy aligned with actual iOS feature set. | Sales Enablement Lead | No new service. |

## Infrastructure / Ops

| Capability | Status | Public claim | Current truth | Missing piece | Next step | Owner | Railway impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Railway backend | LIVE | Backend is deployed as a Railway FastAPI service. | README documents backend Railway setup. | Production env verification remains operational. | Keep `/health`, `/generate`, and `/v1/jobs` protected. | Backend Systems Lead | Current backend service. |
| Railway frontend | PARTIAL | Web frontend can be deployed separately. | README documents frontend service setup. | Current production linkage and env verification. | Keep frontend service free of backend secrets. | Frontend Lead | Current frontend service. |
| Generated asset cleanup | PARTIAL | Generated assets can be cleaned up by retention policy. | Cleanup path exists and should run nonfatally. | Railway production verification and monitoring. | Watch volume usage and cleanup logs. | Security / Privacy Lead | Existing backend; scheduler later if needed. |
| Upload retention | FOUNDATION | Uploaded source retention needs clear policy. | Generated retention is clearer than upload retention. | Upload cleanup rules and user-facing policy. | Define upload retention separately from generated assets. | Security / Privacy Lead | Existing backend; scheduler later. |
| Event logs | FOUNDATION | Internal event logs can inform operations. | JSONL event-log foundation exists in backend work. | Rollups, dashboards, and privacy review. | Use logs internally before public analytics claims. | Data / Analytics Lead | Existing backend; scheduler/Postgres later. |
| Postgres | PLANNED | Not live. | No current claim-safe Postgres account platform. | Durable users, workspaces, jobs, entitlements, campaigns. | Add only when capabilities require shared durable data. | Chief Product Architect | Future service only. |
| Redis | PLANNED | Not live. | No current claim-safe Redis queue/cache. | Queue broker, rate limits, locks, worker coordination. | Add only when workers or multi-instance rate limits require it. | Backend Systems Lead | Future service only. |
| Render worker | PLANNED | Not live. | Rendering currently belongs to backend flow/foundation. | Queue, worker runtime, retry model, asset handoff. | Add only when render work blocks API responsiveness. | Video Processing Lead | Future `lwa-worker-render`. |
| Ingest worker | PLANNED | Not live. | Ingest currently belongs to backend flow/foundation. | Queue, source validation jobs, retry model. | Add only when ingest blocks API or connectors grow complex. | Backend Systems Lead | Future `lwa-worker-ingest`. |
| Scheduler | PLANNED | Not live. | Startup cleanup covers current retention path unless production proves otherwise. | Timed jobs, health checks, logs, and ownership. | Add only when recurring jobs need predictable cadence. | Backend Systems Lead | Future `lwa-scheduler`. |
| Webhooks service | PLANNED | Not live. | Whop/Stripe-style webhook isolation is future work. | Signature verification, replay safety, event persistence. | Add only with real webhook sync requirements. | Monetization / Whop Lead | Future `lwa-webhooks`. |
| Cloudinary/R2 | FUTURE | Not live. | No verified external media storage offload. | Provider choice, signed URLs, lifecycle policy, migration. | Keep Railway volume safe first; revisit when asset scale requires. | Security / Privacy Lead | Future storage dependency, not current Railway service. |
| Monitoring/Sentry | FUTURE | Not live unless separately configured. | Monitoring should not be claimed without verification. | Sentry/project setup, alerts, PII policy. | Add after launch blockers are stable. | Backend Systems Lead | Future env/dependency. |

## Sales / Claim Safety

| Capability | Status | Public claim | Current truth | Missing piece | Next step | Owner | Railway impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Safe sales copy | LIVE | LWA helps prepare ranked clip packages and strategy output. | Claim-safe language is required across web, docs, App Store, and Whop. | Ongoing review as features ship. | Review new copy against this roadmap. | Sales Enablement Lead | No new service. |
| No guaranteed views/revenue | INTENTIONALLY UNSUPPORTED | LWA does not guarantee views, revenue, payouts, or virality. | Permanent boundary. | None. | Keep forbidden claims out of all copy. | Sales Enablement Lead | No service. |
| No fake auto-posting | INTENTIONALLY UNSUPPORTED | Publishing stays manual unless real integrations ship. | Direct posting is not live. | Platform auth/compliance if ever built. | Keep manual posting language. | Chief Product Architect | Webhooks/Redis/Postgres only if built. |
| No fake Whop automation | INTENTIONALLY UNSUPPORTED | Whop automation must not be claimed before verification/submission systems exist. | Whop foundation is not campaign automation. | Verified membership/webhook/campaign APIs. | Keep Whop claims limited to access/purchase/foundation. | Monetization / Whop Lead | Webhooks/Postgres later. |
| Rendered vs strategy-only distinction | LIVE | Rendered clips and strategy-only packages are clearly separate. | This distinction is a protected product flow. | Consistent client labels. | Preserve separation in every surface. | Frontend Lead | Current frontend/backend. |
