# LWA Director Brain Algorithm Artifact

## Purpose

This artifact defines the first reviewable LWA algorithm layer.

It turns the Master Council thread into an engineering-ready scoring system for clip selection, hook packaging, caption preset selection, and platform-specific recommendations.

## Senior Algorithm Council

### High Director of the Signal

Goal: rank clips that make the product feel commercially valuable.

Decision rule: prioritize source moments that produce a clear hook, platform fit, and actionable package.

### Architect of Realms

Goal: make the algorithm extensible for marketplace, Realms, social integrations, and operator dashboard later.

Decision rule: keep the scoring payload structured and explainable.

### Hand of the Director

Goal: keep the algorithm safe for the existing backend.

Decision rule: pure deterministic helpers first; no heavy provider dependency required for v0.

### Forgemaster of Signals

Goal: score by media usefulness, hook strength, captionability, and fallback resilience.

Decision rule: every clip can degrade into a usable package.

### Loremaster of the Realms

Goal: let future XP and quests consume algorithm outcomes.

Decision rule: output event-friendly fields like platform, formula, caption preset, and score components.

### Auditor of the Glass Synod

Goal: avoid unsafe claims and future marketplace problems.

Decision rule: separate product scores from income claims; never promise results.

### Veilwright

Goal: make the score explainable in UI.

Decision rule: return concise rationale and user-facing improvement notes.

### Sigilbearer

Goal: keep future provenance/export compatibility.

Decision rule: deterministic payloads should be hashable later.

### Keeper of the Charter

Goal: keep algorithm copy safe.

Decision rule: no guaranteed viral, guaranteed income, or investment language.

## Algorithm v0 Inputs

- transcript text
- target platform
- content category
- source type
- clip duration
- optional requested caption preset

## Algorithm v0 Outputs

- overall score
- component scores
- selected hook formula
- selected caption preset
- platform goal
- recommended duration range
- rationale
- improvement notes
- safe claim flag

## Component Scores

| Component | Weight | Meaning |
|---|---:|---|
| hook_strength | 30 | first words create curiosity or action |
| platform_fit | 25 | source fits platform length and signal style |
| captionability | 15 | text can become clear captions |
| specificity | 15 | contains concrete terms, numbers, names, or direct claims |
| safety | 15 | avoids unsafe overclaims and unsupported promises |

## Platform Goals

- TikTok: completion and replay
- Instagram Reels: shares and saves
- YouTube Shorts: engaged views and rewatches
- LinkedIn: dwell time and thoughtful comments
- Twitch Clips: clip velocity and context
- Whop/community: completion and member discussion

## Safety Rules

The algorithm must not output claims like:

- guaranteed viral
- guaranteed income
- guaranteed payment
- investment value
- platform approval if not verified

## Implementation Rule

v0 must be deterministic and testable. Provider-powered ranking can enhance it later, but the base algorithm must work without external API calls.

## Runtime Target

- `lwa-backend/app/services/director_brain_algorithm.py`
- tests in `lwa-backend/tests/test_director_brain_algorithm.py`

## Review Checklist

- deterministic output
- no external network calls
- no unsafe claims
- clear component score breakdown
- stable enough for frontend UI display
- future-compatible with Realms XP and marketplace analytics
