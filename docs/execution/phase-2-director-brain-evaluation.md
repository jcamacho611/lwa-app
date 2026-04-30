# Phase 2 — Director Brain Evaluation Runbook

Updated: 2026-04-30

## Purpose

This runbook turns the existing Director Brain implementation into an evaluation-driven enhancement lane. It does not replace the current service. It gives the AI / Media Pipeline Council a proof standard for improving score quality, hook selection, caption presets, safety, and frontend explanation clarity.

## Council lane

Lead council: AI / Media Pipeline Council

Supporting councils:
- Product / UX / Creative Council
- Principal Engineering Council

GitHub phase issue: #52

## Current implementation evidence

The current repo already includes:

- `lwa-backend/app/services/director_brain_algorithm.py`
- platform normalization and platform goals
- hook strength scoring
- platform fit scoring
- captionability scoring
- specificity scoring
- unsafe-claim detection
- hook formula selection
- caption preset normalization
- improvement notes
- `lwa-backend/tests/test_director_brain_support_modules.py`
- frontend Director Brain package/display support

## Evaluation goals

Director Brain should answer four questions for every clip package:

```text
1. Why this clip?
2. Where should it be posted?
3. What hook/caption package should lead?
4. What risk or improvement note matters before publishing?
```

## Eval case matrix

Use the following cases as the minimum evaluation set before changing scoring weights.

| Case | Input pattern | Target platform | Expected signal |
|---|---|---|---|
| Strong number hook | "I made 47 clips from one podcast in 24 hours" | TikTok | high hook_strength and specificity |
| Educational framework | "Here are the 3 rules creators miss when clipping podcasts" | YouTube Shorts | framework/education hook |
| Offer moment | "Book a demo if your team spends hours editing clips" | Whop community | offer/sales relevance |
| LinkedIn lesson | "The mistake operators make is treating every platform the same" | LinkedIn | dwell/lesson framing |
| Unsafe claim | "Guaranteed income from this viral system" | Any | safe_claim false and safety note |
| Weak intro | "Hey guys welcome back today I wanted to talk about..." | TikTok | lower hook_strength with improvement note |
| Caption-heavy text | long complex sentence with many clauses | Reels | captionability warning |
| Strategy-only package | no rendered asset, strong packaging | Auto | UI must not show fake player |

## Scoring proof gates

Before merging a Director Brain scoring change, verify:

```text
- platform normalization preserves current aliases
- unsafe guarantees reduce safety score
- score output remains JSON-safe
- optional fields do not break frontend rendering
- improvement_notes are actionable and human-readable
- no single global virality score replaces per-platform reasoning
```

## Frontend proof gates

Before merging frontend display changes, verify:

```text
- DirectorBrainPackagePanel handles missing optional fields
- strategy-only clips do not show a fake video player
- rendered clips require a playable/downloadable URL
- score explanation is concise and creator-native
- no roadmap feature is displayed as live unless implemented
```

## Suggested tests

Backend tests to add or extend:

```text
test_director_brain_scores_specific_number_hook
test_director_brain_flags_unsafe_guarantee_claim
test_director_brain_platform_aliases_are_stable
test_director_brain_captionability_warns_on_dense_text
test_director_brain_output_is_json_safe
```

Frontend tests/manual checks:

```text
- rendered clip shows playable card
- raw-only clip shows raw asset action only
- strategy-only clip shows package panel and copy actions only
- missing Director Brain fields degrade gracefully
```

## Non-goals

Do not include these in the Phase 2 enhancement PR:

```text
- marketplace checkout
- direct social posting
- full editor
- blockchain minting
- iOS rebuild
- replacing current generation flow
```

## Definition of done

Phase 2 enhancement is ready when:

```text
- eval cases are represented in tests or documented examples
- Director Brain explains why, where, and how to post
- safety/claim notes are present where needed
- frontend respects render status
- current generation response compatibility is preserved
```

## Next action

Use this runbook to create the next Director Brain enhancement PR and post the verification result back to issue #52.
