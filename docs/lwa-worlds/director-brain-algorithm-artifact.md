# LWA Director Brain Clipping Algorithm

Algorithm version: `LWA_DIRECTOR_BRAIN_V0`

## Purpose

The LWA Director Brain is the decision system that turns a long-form source into a ranked, platform-aware short-form clip pack.

It answers five questions:

1. What moments matter?
2. Which moments should become clips?
3. Which platform should each clip target?
4. What hook, caption, thumbnail, and CTA should be used?
5. Which clip should be posted first?

The algorithm must still produce useful output when rendering fails by returning honest strategy-only results instead of crashing or pretending clips are playable.

## Senior Algorithm Council Review

| Council role | Algorithm responsibility |
|---|---|
| High Director of the Signal | Prioritize commercially valuable clips and launch usefulness |
| Architect of Realms | Keep the payload extensible for marketplace, Realms, social integrations, and dashboards |
| Hand of the Director | Keep implementation safe, additive, and compatible with current backend routes |
| Forgemaster of Signals | Own media intelligence, scoring, renderability, and fallback resilience |
| Loremaster of the Realms | Ensure future XP/quest systems can consume algorithm events |
| Auditor of the Glass Synod | Prevent unsafe income, payment, or marketplace claims |
| Veilwright | Make results explainable and clean in the frontend |
| Sigilbearer | Keep deterministic proof-friendly outputs for future provenance |
| Keeper of the Charter | Block guaranteed viral, guaranteed income, investment, or unsupported platform claims |

## 1. Algorithm Pipeline

```text
SOURCE INPUT
  ↓
SOURCE VALIDATION
  ↓
INGEST + METADATA EXTRACTION
  ↓
TRANSCRIPT / AUDIO / VISUAL SIGNAL EXTRACTION
  ↓
MOMENT CANDIDATE DETECTION
  ↓
PLATFORM FIT SCORING
  ↓
VIRALITY + CLARITY + RENDERABILITY SCORING
  ↓
CLIP WINDOW SELECTION
  ↓
HOOK / CAPTION / THUMBNAIL / CTA PACKAGING
  ↓
RENDER ATTEMPT
  ↓
RANKED OUTPUT SPLIT:
    - Rendered clips lane
    - Raw-only clips lane
    - Strategy-only lane
  ↓
FINAL CLIP PACK
```

## 2. Input Shape

```json
{
  "source_url": "string",
  "target_platform": "auto|tiktok|instagram|youtube|linkedin|facebook|x|twitch|whop",
  "trend_angle": "optional string",
  "user_context": "optional string",
  "max_clips": 12
}
```

## 3. Source Validation

The system checks:

- URL exists
- URL is public or accessible
- source type is supported
- source length is within allowed limit
- source is not blocked
- request is under rate limit

Validation output:

```json
{
  "source_valid": true,
  "source_type": "youtube|tiktok|instagram|twitch|direct_video|upload|prompt|music|campaign|unknown",
  "safe_to_process": true,
  "reason": null,
  "warnings": []
}
```

If validation fails, return a clean user-facing error. Never crash. Never expose extraction internals, cookies, provider keys, or stack traces.

## 4. Metadata Extraction

Extract:

- title
- description
- creator/channel name
- duration
- source platform
- upload date if available
- thumbnail if available
- captions/transcript if available
- audio/video availability

Metadata becomes context for the Director Brain.

## 5. Transcript + Signal Extraction

Transcript segment shape:

```json
{
  "start": 12.4,
  "end": 18.9,
  "text": "This is the part most people miss when they edit clips.",
  "speaker": "optional",
  "confidence": 0.91
}
```

Signals detected per segment:

```json
{
  "emotion": "surprise|anger|joy|authority|curiosity|urgency|neutral",
  "energy": 0,
  "clarity": 0,
  "hook_density": 0,
  "payoff_density": 0,
  "controversy": 0,
  "educational_value": 0,
  "story_value": 0,
  "quote_strength": 0,
  "offer_signal": 0,
  "objection_signal": 0,
  "transformation_signal": 0,
  "dead_air_risk": 0,
  "brand_safety_risk": 0
}
```

All numeric values are scored 0–100.

## 6. Moment Candidate Detection

The algorithm groups transcript segments into possible clips.

| Platform | Ideal length |
|---|---:|
| TikTok | 15–45 seconds |
| Instagram Reels | 12–45 seconds |
| YouTube Shorts | 20–55 seconds |
| LinkedIn | 30–90 seconds |
| Facebook Reels | 20–60 seconds |
| X/Twitter | 15–45 seconds |
| Twitch clips | 10–40 seconds |
| Whop/community | 30–90 seconds |

Candidate window rules:

1. Start at the strongest sentence or beat.
2. Expand backward until enough context exists.
3. Expand forward until payoff is complete.
4. Trim dead air.
5. Avoid cutting mid-sentence.
6. Prefer a strong opening inside the first 1–3 seconds.

Candidate shape:

```json
{
  "candidate_id": "string",
  "start": 42.1,
  "end": 78.4,
  "duration": 36.3,
  "transcript_text": "string",
  "opening_line": "string",
  "payoff_line": "string",
  "candidate_type": "viral_hook|educational|authority|sales|objection|transformation|story|controversy|community|quote",
  "source_signals": {}
}
```

## 7. Platform Fit Scoring

Each candidate receives platform scores:

```json
{
  "tiktok_fit": 0,
  "instagram_fit": 0,
  "youtube_shorts_fit": 0,
  "linkedin_fit": 0,
  "facebook_fit": 0,
  "x_fit": 0,
  "twitch_fit": 0,
  "whop_fit": 0
}
```

### TikTok

Prioritize:

- fast hook
- emotional shift
- controversy
- surprise
- meme potential
- identity-based language

Penalize:

- slow intro
- corporate tone
- unclear first 3 seconds

### Instagram Reels

Prioritize:

- clean visual/emotional beat
- aspirational angle
- aesthetic clarity
- concise packaging

Penalize:

- visually confusing moments
- too much missing context

### YouTube Shorts

Prioritize:

- curiosity gap
- payoff
- educational value
- story arc

Penalize:

- no payoff
- unclear thesis

### LinkedIn

Prioritize:

- authority
- business lesson
- founder insight
- transformation
- professional clarity

Penalize:

- chaotic meme-only moments
- weak credibility

### Whop / Community

Prioritize:

- tactical advice
- money/business angle
- insider knowledge
- community exclusivity

Penalize:

- vague hype
- no actionable insight

## 8. Final Clip Score

```text
FinalScore =
  (0.18 × HookStrength) +
  (0.14 × PayoffStrength) +
  (0.12 × PlatformFit) +
  (0.10 × Clarity) +
  (0.10 × EmotionalEnergy) +
  (0.08 × Shareability) +
  (0.08 × Novelty) +
  (0.07 × VisualAudioQuality) +
  (0.06 × Captionability) +
  (0.04 × TrendFit) +
  (0.03 × CreatorBrandFit) -
  (0.12 × RiskPenalty)
```

Normalize final output to 0–100.

| Component | Meaning |
|---|---|
| HookStrength | How strong the first 1–3 seconds are |
| PayoffStrength | Whether the clip rewards attention |
| PlatformFit | Fit for selected/recommended platform |
| Clarity | Whether a viewer understands without long context |
| EmotionalEnergy | Surprise, humor, tension, urgency, emotion |
| Shareability | Comment/save/send potential |
| Novelty | Fresh, contrarian, or surprising angle |
| VisualAudioQuality | Whether the media can become a clean short |
| Captionability | Whether captions can strengthen the moment |
| TrendFit | Alignment with trend angle or cultural signal |
| CreatorBrandFit | Fit with creator/business category |
| RiskPenalty | Unsafe, boring, unclear, misleading, dead air, low quality |

## 9. Risk Penalty

```text
RiskPenalty =
  BrandSafetyRisk +
  DeadAirRisk +
  ContextMissingRisk +
  MisleadingEditRisk +
  LowQualityMediaRisk +
  RepetitionRisk
```

Reject or downgrade clips that:

- start too slowly
- require too much missing context
- have unclear audio
- contain too much silence
- cut the speaker unfairly
- are likely misleading when clipped
- repeat a stronger candidate
- are unsafe for brand/local-business use
- contain medical, financial, adult, or income claims needing caution

## 10. Deduplication

Rules:

1. Sort candidates by FinalScore.
2. Keep the highest-scoring candidate first.
3. Remove candidates with time overlap above 60%.
4. Remove candidates with highly similar transcript text.
5. Keep alternates only if they serve a different platform or packaging angle.

## 11. Post Order Ranking

```text
PostRank = weighted order based on:
- FinalScore
- PlatformFit
- HookDiversity
- ContentVariety
- CampaignSequenceValue
```

| Rank | Purpose |
|---|---|
| #1 | strongest immediate hook / lead clip |
| #2 | follow-up context or deeper payoff |
| #3 | contrarian/comment-driving angle |
| #4+ | supporting clips, niche angles, alternate platforms |

The #1 clip should not always be the longest or most informative. It should be the strongest opener.

## 12. Packaging Generation

For each selected clip, generate:

- title
- primary hook
- 3 hook variants
- caption
- caption style
- thumbnail text
- CTA
- platform recommendation
- why this matters
- posting note

Clip package shape:

```json
{
  "title": "The mistake most creators make",
  "hook": "Most creators are posting this part in the wrong order.",
  "hook_variants": [
    "This is why your clips are not hitting.",
    "The clip is good — the order is wrong.",
    "Post this moment first if you want attention."
  ],
  "caption": "The edit matters, but the order matters more. Start with the moment that creates tension, then use the explanation second.",
  "caption_style": "tension-led",
  "thumbnail_text": "Wrong Clip Order",
  "cta_suggestion": "Comment ‘CLIP’ if you want the full breakdown.",
  "why_this_matters": "This moment creates immediate tension and gives viewers a reason to keep watching.",
  "recommended_platform": "TikTok",
  "post_rank": 1
}
```

## 13. Render Attempt

For each selected clip:

1. Cut source window.
2. Convert to vertical 9:16 if appropriate.
3. Normalize audio.
4. Add captions if enabled.
5. Export raw and edited versions if possible.
6. Store asset URLs.
7. Mark render status.

Render statuses:

- `rendered`
- `raw_only`
- `strategy_only`
- `failed`

## 14. Honest Output Split

A rendered clip has at least one playable/downloadable asset:

```text
clip_url OR raw_clip_url OR edited_clip_url OR preview_url OR download_url
```

A strategy-only clip has packaging and timestamps but no playable asset.

It must be labeled clearly:

```json
{
  "render_status": "strategy_only",
  "strategy_only": true,
  "reason_not_rendered": "Rendering failed, but the moment is still strategically useful."
}
```

## 15. Final Response Shape

```json
{
  "request_id": "string",
  "status": "success|partial|fallback|failed",
  "source_url": "string",
  "algorithm_version": "LWA_DIRECTOR_BRAIN_V0",
  "processing_summary": {
    "recommended_platform": "TikTok",
    "recommended_content_type": "reaction/commentary",
    "recommended_output_style": "tension-led short-form",
    "platform_recommendation_reason": "The source has fast interruption moments and strong curiosity hooks.",
    "rendered_clip_count": 3,
    "strategy_only_clip_count": 2,
    "recommended_next_step": "Export the lead rendered clip first."
  },
  "clips": [
    {
      "id": "clip_001",
      "rank": 1,
      "post_rank": 1,
      "start": 42.1,
      "end": 78.4,
      "duration": 36.3,
      "title": "The interruption moment",
      "hook": "This is the moment that changes the whole clip.",
      "caption": "Start here because this beat creates instant tension.",
      "score": 92,
      "confidence_score": 88,
      "recommended_platform": "TikTok",
      "caption_style": "tension-led",
      "thumbnail_text": "The Moment It Changed",
      "cta_suggestion": "Comment if you want the full breakdown.",
      "why_this_matters": "The first three seconds create an immediate curiosity gap.",
      "render_status": "rendered",
      "strategy_only": false,
      "preview_url": "string|null",
      "edited_clip_url": "string|null"
    }
  ]
}
```

## 16. Fallback Algorithm

If transcript, AI provider, or renderer fails, return fallback output.

Fallback rules:

- Do not crash.
- Do not claim clips are rendered if they are not.
- Return strategy-only results with useful packaging.
- Use metadata/title/description if transcript is unavailable.
- Use deterministic generic clip windows if duration is known.
- Explain limitation clearly.

Fallback window generator:

```text
If duration < 90 sec:
  create 1 candidate from 10% to 80% of video

If duration 90 sec–10 min:
  create 3 candidates:
    10%–20%
    40%–50%
    70%–80%

If duration > 10 min:
  create 5 candidates:
    5%–8%
    15%–18%
    35%–38%
    55%–58%
    75%–78%
```

Each fallback candidate must be marked:

```json
{
  "render_status": "strategy_only",
  "strategy_only": true,
  "fallback": true
}
```

## 17. Implementation Pseudocode

```text
function generate_lwa_clip_pack(request):
    metadata = extract_metadata(request.source_url)

    try:
        transcript = get_transcript_or_transcribe(metadata)
    except:
        transcript = null

    if transcript exists:
        segments = segment_transcript(transcript)
        segment_signals = analyze_segments(segments)
        candidates = detect_candidate_windows(segments, segment_signals)
    else:
        candidates = generate_fallback_windows(metadata.duration)

    scored_candidates = []

    for candidate in candidates:
        platform_scores = score_platform_fit(candidate, request.target_platform)
        core_score = calculate_final_score(candidate, platform_scores, request.trend_angle)
        risk_penalty = calculate_risk_penalty(candidate)
        final_score = normalize(core_score - risk_penalty)

        scored_candidates.append({
            candidate,
            platform_scores,
            final_score,
            risk_penalty
        })

    deduped = remove_overlapping_candidates(scored_candidates)
    ranked = sort_by_score(deduped)
    selected = choose_top_candidates(ranked, max_clips=request.max_clips)

    packaged = []

    for candidate in selected:
        package = generate_clip_package(candidate)
        package.post_rank = assign_post_rank(candidate, selected)
        packaged.append(package)

    rendered_results = []

    for package in packaged:
        try:
            render = attempt_render(package)
            rendered_results.append(merge(package, render, render_status="rendered"))
        except:
            rendered_results.append(mark_strategy_only(package))

    summary = build_processing_summary(rendered_results)

    return RankedClipPack(
        status=determine_status(rendered_results),
        algorithm_version="LWA_DIRECTOR_BRAIN_V0",
        processing_summary=summary,
        clips=rendered_results
    )
```

## 18. MVP Build Order

1. Candidate clip windows from transcript
2. Basic scoring formula
3. Platform fit scoring
4. Deduplication
5. Post rank assignment
6. Hook/caption generation
7. Render status split
8. Fallback strategy-only results
9. Frontend rendered lane vs strategy-only lane
10. Tests

## 19. Minimum Test Cases

### Strong hook wins

Given two candidates:

- Candidate A has a strong first sentence and average payoff.
- Candidate B has weak opening and strong payoff.

Expected: Candidate A ranks higher for TikTok/Reels.

### LinkedIn prefers authority

Given a business lesson clip and a chaotic meme clip:

Expected: LinkedIn fit ranks the business lesson higher.

### Strategy-only is honest

Given render failure:

Expected:

- clip remains in output
- `strategy_only=true`
- no playable URL is invented
- frontend can label it correctly

### Deduplication removes overlap

Given two candidates with 80% overlapping timestamps:

Expected: only higher-scoring candidate remains.

### Fallback never crashes

Given missing transcript and render failure:

Expected:

- system returns fallback strategy-only clips
- no backend 500
- frontend displays useful message

## 20. Codex Prompt — Build The Algorithm

```text
Role: AI/media pipeline engineer for LWA.

Task:
Implement LWA_DIRECTOR_BRAIN_V0, the ranking algorithm that turns a source transcript into a ranked clip pack with platform fit, virality scoring, hook/caption packaging, render status, and fallback strategy-only results.

Algorithm requirements:
1. Validate source request.
2. Extract metadata.
3. Use transcript segments if available.
4. Detect candidate clip windows.
5. Score each candidate using:
   - HookStrength
   - PayoffStrength
   - PlatformFit
   - Clarity
   - EmotionalEnergy
   - Shareability
   - Novelty
   - Visual/Audio Quality
   - Captionability
   - TrendFit
   - Creator/Brand Fit
   - RiskPenalty
6. Normalize final score to 0–100.
7. Score platform fit for TikTok, Instagram Reels, YouTube Shorts, LinkedIn, Facebook Reels, X/Twitter, Twitch, and Whop/community.
8. Deduplicate overlapping candidates.
9. Assign post rank.
10. Generate title, hook, hook variants, caption, thumbnail text, CTA, caption style, why_this_matters.
11. Attempt render if render pipeline exists.
12. If render fails, return strategy-only result honestly.
13. Never invent playable URLs.
14. Return processing_summary with rendered and strategy-only counts.

Files likely involved:
- backend generation service
- backend schemas/models
- new director_brain module/service
- fallback result model
- tests for scoring, deduplication, fallback, and render status

Constraints:
- Preserve existing generation route compatibility.
- Add optional fields instead of removing existing fields.
- Do not touch lwa-ios.
- Do not redesign frontend in this prompt.
- Do not require real social API integrations.
- Do not claim direct posting exists.
- Fallback must never cause frontend 500 crashes.

Verification commands:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant backend tests
- run one sample generation request if local dev supports it

Expected output:
1. Files changed
2. Algorithm module created/updated
3. Scoring fields added
4. Fallback behavior explained
5. Tests added/updated
6. Verification results
7. Commit message
```
