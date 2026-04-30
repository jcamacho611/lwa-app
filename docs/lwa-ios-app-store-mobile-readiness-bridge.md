# LWA / IWA Mobile Readiness Bridge

## Purpose

This document captures the Chunk 13 App Store / iOS readiness bridge for LWA Worlds and IWA.

It is intentionally a planning and contract document first. Do **not** touch `lwa-ios/` until a specific iOS audit task is run. Do **not** blindly paste mobile backend code that references packages not yet present in the repo.

## Chunk 13 Goal

Add the App Store / iOS readiness bridge without touching `lwa-ios/` yet.

This includes:

1. App Store readiness checklist
2. Apple Sign In planning
3. IAP / Whop compliance boundary
4. Privacy/support/terms URL audit
5. App Store metadata drafts
6. App Review notes
7. Screenshot checklist
8. iOS backend compatibility contract
9. TestFlight checklist
10. Mobile entitlement safety
11. Docs
12. Codex prompts
13. Production tickets

## iOS / App Store Rule

The iOS app must be review-safe, payment-safe, and identity-safe.

The app can:

1. let users sign in
2. let users upload/create content
3. let users use AI clipping features
4. let users view jobs, clips, marketplace state, and account state
5. let users manage generated outputs
6. use backend entitlements from Whop where allowed
7. support Apple Sign In if login is required

The app must not:

1. bypass Apple payment rules
2. sell digital features in-app through non-compliant external links
3. hide paid digital unlocks behind non-compliant flows
4. expose private files
5. claim guaranteed earnings
6. claim guaranteed virality
7. enable real payouts before payout controls are complete
8. allow copyrighted music without rights
9. submit with broken privacy/support/terms URLs
10. submit with demo auth enabled for production

## Backend Mobile Contract Goal

The iOS app should not call many fast-changing early-stage endpoints directly.

Add a stable mobile-safe backend surface when the current backend structure is ready:

- `GET /worlds/mobile/me`
- `GET /worlds/mobile/dashboard`
- `GET /worlds/mobile/launch-safety`
- `GET /worlds/mobile/feature-flags`

These endpoints should aggregate safe mobile state and hide risky/unfinished features by default.

## Required Mobile Feature Flags

- `LWA_MOBILE_CLIPPING_ENABLED`
- `LWA_MOBILE_UPLOADS_ENABLED`
- `LWA_MOBILE_MARKETPLACE_ENABLED`
- `LWA_MOBILE_UGC_ENABLED`
- `LWA_MOBILE_PAYOUTS_VISIBLE`
- `LWA_MOBILE_EXTERNAL_CHECKOUT_VISIBLE`
- `LWA_APPLE_IAP_REQUIRED`
- `LWA_APPLE_IAP_CONFIGURED`
- `LWA_REAL_PAYOUTS_ENABLED`
- `LWA_DEMO_AUTH_ENABLED`

Recommended review-build defaults:

```bash
LWA_MOBILE_CLIPPING_ENABLED=true
LWA_MOBILE_UPLOADS_ENABLED=true
LWA_MOBILE_UGC_ENABLED=false
LWA_MOBILE_MARKETPLACE_ENABLED=false
LWA_MOBILE_PAYOUTS_VISIBLE=false
LWA_MOBILE_EXTERNAL_CHECKOUT_VISIBLE=false
LWA_APPLE_IAP_REQUIRED=true
LWA_APPLE_IAP_CONFIGURED=false
LWA_REAL_PAYOUTS_ENABLED=false
LWA_DEMO_AUTH_ENABLED=false
```

## Mobile Response Contracts

Future implementation should provide these response shapes.

### MobileFeatureFlagsResponse

- `clipping_enabled: bool`
- `uploads_enabled: bool`
- `marketplace_enabled: bool`
- `ugc_enabled: bool`
- `payouts_visible: bool`
- `external_checkout_visible: bool`
- `apple_iap_required: bool`
- `demo_mode: bool`

### MobileLaunchSafetyResponse

- `mobile_safe: bool`
- `demo_auth_enabled: bool`
- `real_payouts_enabled: bool`
- `external_checkout_enabled: bool`
- `apple_iap_configured: bool`
- `warnings: list[str]`
- `blockers: list[str]`

### MobileMeResponse

- `user_id: str`
- `display_name: str`
- `roles: list[str]`
- `is_demo: bool`
- `plan: str`
- `entitlement_status: str`

### MobileDashboardResponse

- `me: MobileMeResponse`
- `features: MobileFeatureFlagsResponse`
- `launch_safety: MobileLaunchSafetyResponse`
- `quick_actions: list[str]`
- `status_cards: list[dict]`

## App Store Compliance Boundary

Whop can remain the web sales/access layer, but the iOS app must not expose non-compliant purchase instructions or external checkout links if Apple requires IAP.

Safe MVP options:

1. **Companion app** — Existing users sign in and use features available to their account, with no external purchase links.
2. **Free limited app** — Limited free functionality with no paid unlock messaging.
3. **IAP-enabled app** — Digital subscriptions/features sold through Apple IAP and mapped to backend entitlements.

Do not include in the App Store review build:

- Buy-on-Whop buttons
- external payment links
- payout promises
- guaranteed earnings claims
- guaranteed virality claims
- unlicensed music features
- crypto/NFT purchasing
- prediction-market trading
- unsupported marketplace payout claims

## Apple Sign In Plan

If the iOS app offers third-party/social login, Sign in with Apple may be required.

Backend identity should map all identity providers to one internal user ID:

- Apple user ID
- Whop user ID
- web auth provider ID
- Stripe customer ID
- internal LWA user ID

MVP flow:

1. iOS gets Apple identity token.
2. iOS sends token to backend.
3. Backend verifies token with Apple.
4. Backend finds or creates internal user profile.
5. Backend returns session/user actor.
6. Backend checks entitlement source: Apple IAP, Whop, or admin grant.
7. iOS shows feature flags from `/worlds/mobile/feature-flags`.

Do not trust a frontend-provided Apple user ID without server-side token verification.

## App Store Metadata Draft

App name: **IWA**

Subtitle options:

- AI clips from long videos
- Create short-form clips faster
- AI video repurposing studio

Description direction:

IWA helps creators and teams repurpose long-form content into short-form video ideas and clip packages. Users can upload or connect source content, generate clip ideas, review suggested hooks and captions, and organize outputs for platforms like TikTok, Instagram, YouTube Shorts, and more.

Required disclaimer:

IWA does not guarantee views, virality, followers, revenue, or earnings. Users are responsible for ensuring they have the rights to upload, edit, and publish their content.

Category:

- Primary: Photo & Video
- Secondary: Productivity or Business

## Screenshot Checklist

Screenshots should show:

1. Home / creator dashboard
2. Upload or source library
3. AI clip suggestions
4. Hook and caption review
5. Clip workflow / job progress
6. Final organized clip pack

Safe screenshot copy:

- Find strong moments faster
- Review AI clip suggestions
- Organize hooks and captions
- Track clip creation
- Package content for short-form platforms

Avoid:

- Go viral guaranteed
- Earn money instantly
- Get paid from your clips
- Buy subscription on Whop
- Trade / NFT / crypto
- Use copyrighted music

## TestFlight Checklist

Before upload:

- Bundle ID confirmed
- Version number set
- Build number increased
- API base URL points to production or staging backend
- Demo auth disabled for production review build
- Apple Sign In configured if required
- Push notifications disabled unless implemented
- External checkout hidden
- Payout features hidden
- Marketplace hidden unless fully compliant
- UGC moderation/reporting ready if UGC visible
- Privacy policy URL live
- Support URL live
- Terms URL live if used

Backend smoke targets after mobile routes exist:

```bash
curl https://YOUR_BACKEND_URL/worlds/mobile/feature-flags
curl https://YOUR_BACKEND_URL/worlds/mobile/launch-safety
curl https://YOUR_BACKEND_URL/worlds/mobile/dashboard
```

## App Store Readiness QA

1. Confirm privacy policy URL is live.
2. Confirm support URL is live.
3. Confirm terms URL is live if used.
4. Confirm no in-app external checkout appears in iOS review build.
5. Confirm no payout feature appears in iOS review build.
6. Confirm no guaranteed earnings copy appears.
7. Confirm no guaranteed virality copy appears.
8. Confirm copyrighted music features are disabled or rights-gated.
9. Confirm demo auth is disabled for production review build.
10. Confirm Apple Sign In is configured if login rules require it.
11. Confirm TestFlight build points to correct backend.
12. Confirm backend launch-safety endpoint has no critical blockers.

## Repo Safety Note

The uploaded Chunk 13 implementation references modules like `app.worlds.auth.roles`, `app.worlds.auth.service`, and `app.worlds.dependencies`. Current repo search did not find those modules on `feat/source-poc-matrix` at the time this doc was added.

Therefore, implementation must adapt the mobile contract to the repo's real auth/session/dependency structure instead of pasting the sample code blindly.

## Next Safe Codex Prompt

```text
You are working in repo jcamacho611/lwa-app on branch feat/source-poc-matrix.

Read:
- docs/lwa-worlds-integrated-architecture.md
- docs/lwa-ios-app-store-mobile-readiness-bridge.md

Task:
Implement the iOS/mobile backend compatibility contract only if it can be adapted safely to the existing backend structure.

Rules:
- Additive edits only.
- Do not touch lwa-ios.
- Do not paste code that references missing app.worlds modules.
- Preserve existing routes.
- Preserve existing clipping/generation flow.
- Payouts hidden by default.
- External checkout hidden by default.
- Marketplace hidden by default unless compliant.
- Demo auth should block production mobile safety.
- Do not bypass Apple payment rules.

First inspect:
- lwa-backend/app/main.py or backend app init
- existing auth/dependency modules
- existing config/settings pattern
- existing tests pattern

Then add adapted mobile-safe routes:
- GET /worlds/mobile/me
- GET /worlds/mobile/feature-flags
- GET /worlds/mobile/launch-safety
- GET /worlds/mobile/dashboard

Feature env vars:
- LWA_MOBILE_CLIPPING_ENABLED
- LWA_MOBILE_UPLOADS_ENABLED
- LWA_MOBILE_MARKETPLACE_ENABLED
- LWA_MOBILE_UGC_ENABLED
- LWA_MOBILE_PAYOUTS_VISIBLE
- LWA_MOBILE_EXTERNAL_CHECKOUT_VISIBLE
- LWA_APPLE_IAP_REQUIRED
- LWA_APPLE_IAP_CONFIGURED
- LWA_REAL_PAYOUTS_ENABLED
- LWA_DEMO_AUTH_ENABLED

Add tests:
- mobile schema/contract tests
- mobile route smoke tests

Run:
- python3 -m compileall lwa-backend/app lwa-backend/scripts
- python3 -m unittest discover -s tests
- git diff --check
- git status --short --branch

Return:
1. files inspected
2. files changed
3. routes added
4. env vars added
5. tests added
6. App Store safety notes
7. manual QA
8. commit message
```

## Definition Of Done

Chunk 13 is done when:

- Mobile backend package/endpoints exist or are adapted to the current backend structure.
- Mobile feature flags endpoint exists.
- Mobile launch safety endpoint exists.
- Mobile dashboard endpoint exists.
- Mobile me endpoint exists.
- Mobile route/contract tests pass.
- App Store compliance docs exist.
- Apple Sign In plan exists.
- App Store metadata draft exists.
- Screenshot checklist exists.
- TestFlight checklist exists.

Still not done in this chunk:

- iOS app code changes
- Apple Sign In implementation
- IAP implementation
- Whop/iOS entitlement linking
- App Store screenshots
- App Store Connect submission
