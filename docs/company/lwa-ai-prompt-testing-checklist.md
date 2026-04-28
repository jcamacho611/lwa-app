# LWA AI Prompt Testing Checklist

## Purpose
This checklist is the verification gate for any new prompt, prompt template, provider route, or AI packaging change.

Prompt work is not complete because it sounds smart.

It is complete only when it remains aligned, typed, safe, and useful.

## 1. Product Alignment

- Does the prompt avoid YouTube-only framing?
- Does the prompt avoid Whop-only framing?
- Does the prompt support video, audio, music, prompt, Twitch, stream, campaign, upload, and unknown source branches?
- Does it preserve the master law: `Any source in. Creator-ready content out.`?

## 2. Schema Validation

- Does output match the required JSON schema?
- Are new fields optional unless fully rolled out?
- Are `score` and `confidence_score` numeric and reasonable?
- Is `post_rank` present?
- Are `hook_variants` present when expected?
- Is `rendered_status` truthful?
- Is `fallback_reason` present when needed?

## 3. Attention Quality

- Is the top-ranked package actually the strongest?
- Does `why_this_matters` explain the ranking?
- Is the caption usable by a creator?
- Is `thumbnail_text` short and practical?
- Is `cta_suggestion` realistic?
- Is `confidence_score` conservative when certainty is weak?

## 4. Fallback Behavior

- Platform blocked -> clear plain-English fallback?
- Render failed -> strategy-only package returned?
- Audio only -> no fake video claim?
- Prompt only -> useful script/package instead of empty output?
- Provider failed -> deterministic fallback path used?

## 5. Claim Safety

- No guaranteed viral claims?
- No guaranteed views?
- No guaranteed revenue or payout?
- No fake auto-posting?
- No fake campaign submission?
- No hidden compute, mining, or training language?
- No private-content bypass language?

## 6. Render Truth

- Rendered clips have real media URLs?
- Thumbnail-only results are not treated as playable media?
- Strategy-only packages omit fake export actions?
- Render-limited states remain clearly labeled?

## 7. Source-Type Coverage

Test at least one example for:

- `video`
- `audio`
- `music`
- `prompt`
- `twitch`
- `stream`
- `campaign`
- `upload`
- `unknown`

## 8. Provider Routing

- Anthropic path used for deep reasoning when needed?
- OpenAI path used for structured JSON when needed?
- Local fallback path available?
- Visual engine path limited to visual prompt generation?
- No provider allowed to override claim safety or render truth?

## 9. Client Readiness

- Can the web app display every field safely?
- Can iOS decode new fields as optional?
- Can strategy-only outputs be clearly shown?
- Can rendered outputs show open/export actions only when URLs exist?

## 10. Regression Gate

Before merging prompt-related changes:

- verify output contract stability
- verify fallback behavior
- verify no forbidden claim text leaked into user copy
- verify older clients still handle missing fields
- verify docs and schema stay aligned

