# LWA Attention Compiler Rubric

## Purpose
This rubric defines how LWA should score clips and strategy packages.

The core rule is:

> rank by retention behavior, not by topic alone.

This keeps the AI layer aligned with the founder-approved clipping engine direction.

## Core Signals

| Signal | Meaning | Weight |
| --- | --- | ---: |
| Hook strength | Does the first line stop scrolling? | 15 |
| First 3 seconds | Does it create attention immediately? | 12 |
| Emotional spike | Is there surprise, emotion, conflict, awe, humor, anger, or tension? | 10 |
| Curiosity gap | Does the viewer need to keep watching? | 10 |
| Clarity | Can the idea stand alone without full source context? | 9 |
| Payoff | Is there a satisfying reveal, answer, or point? | 9 |
| Shareability | Is it worth sending, saving, clipping, or commenting on? | 8 |
| Platform fit | Does it fit TikTok, Reels, Shorts, or stream culture? | 8 |
| Visual/audio strength | Is the source media usable or at least packaging-friendly? | 7 |
| Caption usefulness | Does the caption package reduce creator work? | 5 |
| Campaign fit | Does it match the stated objective when one exists? | 4 |
| Render readiness | Can it become a real output asset now? | 3 |

## Ranking Rules

### Score
`score` is the raw attention potential.

### Post rank
`post_rank` is the recommended creator posting order.

### Confidence score
`confidence_score` reflects how trustworthy the recommendation is based on:

- source quality
- transcript quality
- render certainty
- context completeness
- fallback depth

## Render Truth Rules

A clip can score well and still be strategy-only.

Rules:

- a strong strategy-only package is allowed
- a strong strategy-only package must still be labeled strategy-only
- render readiness cannot erase lack of real media
- rendered status must not be inferred from thumbnail-only assets

## Fallback Scoring Rules

Fallback output must not collapse into meaningless flat scores.

Expected behavior:

- a batch of fallback clips should normally produce distinct scores
- `55` for every fallback clip is a bug unless the clips are truly identical
- confidence should drop when the system had less source certainty

## Campaign Rules

When campaign context exists:

- `campaign_fit` should influence scoring
- campaign fit must not override all attention signals
- clips should still be ranked by creator usefulness
- manual review remains required

## Current Repo Alignment

Current repo direction already includes:

- backend Attention Compiler foundation
- signal-based ranking
- score breakdown fields
- why-this-matters fields
- render readiness discussion
- frontend score transparency direction

Still needed:

- full any-source scoring validation
- audio/music/prompt-specific rubric tuning
- Twitch/stream-specific modifiers
- broader fallback scoring tests

## Testing Expectations

Each scoring change should verify:

- strongest clip wins for understandable reasons
- `post_rank` stays stable
- `confidence_score` is conservative when source quality is weak
- strategy-only packages remain clearly labeled
- fallback batches do not flatten into one score
- campaign context adds relevance without becoming fake automation

