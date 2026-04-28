# LWA Viral Clipping Intelligence Framework

> Council Knowledge Base — Product Intelligence Layer
> Version 1.0 — April 2026
> Do not share externally.

---

## Product Vision

**One source in. Best clip first. Ranked viral moments. Rendered clips separated from strategy-only ideas.**

LWA processes long-form video and produces:
- A ranked stack of clips, best-first
- Full copy packages per clip (hook, caption, CTA, thumbnail text)
- Rendered clips (READY NOW) separated from strategy-only clips (STRATEGY ONLY)
- Platform-fit scores per clip per platform
- Post order recommendations

---

## Section 1: Viral Clipping Fundamentals

### The 19 Viral Signal Factors

Every clip is evaluated against these signals. The number of signals present and their intensity determines ranking.

| Signal | What It Is | Detection Method | Score Field |
|---|---|---|---|
| **Hook Strength** | Quality of the opening 1–3 seconds | Hook pattern library match on first 15 words | `hook_score` |
| **Interruption Pattern** | Sudden tonal/energy shift that breaks autopilot | Audio energy spike, silence gap, pace change | `audio_energy_delta` |
| **Emotional Spike** | Strong identifiable emotion: anger, surprise, joy | Sentiment analysis, laughter detection, RMS peak | `emotional_spike_score` |
| **Controversy** | A take that divides the audience | Contrarian phrase detection, debate language | `controversy_score` |
| **Curiosity Gap** | Withheld information that forces the viewer to stay | Setup-delay-payoff gap detection | `curiosity_gap_score` |
| **Social Proof** | Results, numbers, credentials that validate the speaker | Number detection, result language extraction | `social_proof_detected` |
| **Transformation Moment** | Before/after pivot — the moment the story changes | Pivot language detection, story arc parsing | `transformation_detected` |
| **Payoff Timing** | Reward lands at the right moment (8–20s optimal) | Hook-to-payoff gap calculation | `payoff_seconds` |
| **Retention Curve** | Even energy throughout; strong final third | Energy distribution across thirds | `retention_score` |
| **Replay Value** | Dense enough to warrant rewatching | Info density, punchline count | `replay_value_score` |
| **Shareability** | Feels like something to forward to a specific person | Universal theme detection, share-length fit | `shareability_score` |
| **Comment Bait** | Invites genuine responses without being manipulative | Question detection, open loop scoring | `comment_bait_detected` |
| **Platform-Native Pacing** | Rhythm matches the target platform's expectation | WPM vs. platform benchmark, cut density | `platform_pace_match_score` |
| **Visual/Audio Energy** | Physical energy: gestures, expressions, voice intensity | Audio RMS variance, face movement detection | `audio_energy_score`, `visual_energy_score` |
| **Personality-Driven** | Speaker's unique voice or humor shines through | Unique vocab detection, humor timing | `personality_signal_score` |
| **Educational Value** | Teaches something specific and actionable | Fact density, instructional phrase count | `educational_score` |
| **Meme Potential** | Quotable, absurd, or relatable at scale | Short phrase detection, absurdist flag | `meme_potential_score` |
| **Quotability** | A sentence that stands alone as memorable | Aphorism detection, cadence analysis | `top_quote`, `quotability_score` |
| **Narrative Tension** | Conflict, stakes, or unresolved problem | Conflict word detection, stakes language | `narrative_tension_score` |

### Scoring Rule

```
VIRALITY_SCORE =
  hook_score × 0.25
  + retention_score × 0.20
  + emotional_spike_score × 0.15
  + clarity_score × 0.10
  + platform_fit_score × 0.10
  + visual_energy_score × 0.05
  + audio_energy_score × 0.05
  + controversy_score × 0.03
  + educational_value_score × 0.03
  + share_comment_score × 0.02
  + render_readiness_score × 0.01
  + commercial_value_score × 0.01
```

**Tiers:**
- ≥ 75: Tier 1 — Lead clip candidate
- 55–74: Tier 2 — Strong clip
- 35–54: Tier 3 — Strategy-only candidate
- < 35: Low priority / archive

---

## Section 2: Platform-by-Platform Rules

| Platform | Ideal Length | WPM | Caption Style | CTA Style | #1 Ranking Signal |
|---|---|---|---|---|---|
| **TikTok** | 7–30s | 130–160 | Bold karaoke | Question | Completion rate + rewatch |
| **Instagram Reels** | 7–30s | 110–140 | Clean aesthetic | Save prompt | Saves + shares |
| **YouTube Shorts** | 15–60s | 100–130 | Standard subtitle | Subscribe/watch full | CTR + watch-through % |
| **Facebook Reels** | 15–60s | 90–110 | Readable bold | Share/tag | Share rate |
| **X Video** | 10–45s | 120–150 | Minimal | Debate prompt | Quote-tweets + replies |
| **LinkedIn Video** | 30–90s | 85–100 | Professional clean | Follow prompt | Dwell time + comments |
| **Whop Community** | 60–480s | 80–90 | Educational structured | Join/book | Completion + conversions |

### Platform-Specific Don'ts
- **TikTok**: Never watermarks from other platforms. Never slow intros.
- **Instagram**: TikTok watermarks are suppressed by the algorithm.
- **YouTube Shorts**: No hashtag stuffing. Title must be searchable.
- **LinkedIn**: No casual slang. Content must deliver professional value.
- **X**: No long captions. Authenticity > production value.

---

## Section 3: Hook Formula Library

16 hook types the backend should detect and generate:

| Hook Type | Template | Detection Signal |
|---|---|---|
| **Curiosity** | `[Subject] changes everything — but not the way you think.` | curiosity_gap_score > 60 |
| **Confrontation** | `Stop doing [X]. You're wasting your time.` | controversy_score > 50 |
| **Mistake** | `The biggest mistake [audience] makes with [topic].` | mistake_language_detected |
| **Transformation** | `I went from [A] to [B] in [time].` | transformation_detected |
| **Secret/Process** | `The [X]-step system I use to [result] — nobody talks about this.` | process_language_detected |
| **Contrarian** | `Unpopular opinion: [topic] is actually [opposite].` | contrarian_phrase_detected |
| **Social Proof** | `[Number] [audience] achieved [result] using this.` | social_proof_detected |
| **Speed** | `[X] ways to [result] in under [time]. Let's go.` | number + time compression |
| **Emotional** | `The day I [event] changed how I see [topic] forever.` | sentiment_intensity > 70 |
| **Tutorial** | `Here's exactly how to [task] in [time]. No theory.` | instructional_language |
| **List** | `[X] [topic] rules that changed everything.` | list_structure_detected |
| **Watch Until** | `Watch until the end — what [person] says at [time] will surprise you.` | late_clip_revelation |
| **Before/After** | `Before: [negative]. After: [positive]. The difference: [insight].` | temporal_contrast |
| **Nobody Tells You** | `Nobody tells you that [insight]. Until now.` | hidden_knowledge_phrase |
| **I Tested** | `I tested [X] for [time]. Here's the honest truth.` | testing_language_detected |
| **This Changed Everything** | `One [thing] changed everything I knew about [topic].` | pivot_language_detected |

---

## Section 4: Caption and Subtitle Rules

### Core Rules
- **Max line length**: 32 characters on mobile
- **Words per segment**: 2–5 words per bubble
- **Font minimum**: 36px at 1080p
- **Contrast**: White text + black stroke (2–4px) or inverted
- **Placement**: Lower-center safe zone (bottom 35%)
- **Emphasis**: Highlight 1 key word per segment — not every word
- **Emoji**: 0–1 per caption line. Never in burned-in subtitles.

### Caption Style Presets

| Preset | Style | Auto-Apply Condition | Platform |
|---|---|---|---|
| `bold_karaoke` | Bold white, word-by-word highlight, black stroke | energy_score > 65 AND duration < 45s | TikTok, Reels, YT Shorts |
| `clean_professional` | Clean white, phrase-level, Arial | authority_score > 70 AND wpm < 110 | LinkedIn, YT Shorts (edu) |
| `aesthetic_minimal` | Thin sans-serif, no stroke, fade-in | aesthetic_score > 70 AND tone = calm | Instagram aesthetic |
| `impact_pop` | Large uppercase, color highlight | category IN (coaching, fitness, motivation) | TikTok, Instagram |
| `standard_subtitle` | Standard, high contrast, sentence-level | duration > 60s OR wpm < 90 | YouTube, LinkedIn, Facebook |

---

## Section 5: Thumbnail / First-Frame Rules

| Rule | Detection | Generation |
|---|---|---|
| **Facial Expression** | Face emotion detection — score peak expression frames | Select highest-scoring expression frame |
| **Proof Frame** | OCR scan for numbers/results on screen | Auto-select if stat visible; pair with thumbnail text |
| **Text Overlay** | Extract `top_quote` or `hook_text` | Max 6 words, white bold text, black stroke |
| **Mobile Readability** | Simulate at 40×40px; score text readability | Flag if unreadable at small size; enforce larger font |
| **Visual Contrast** | Calculate luminance contrast score | Boost contrast +15–20% for low-contrast frames |
| **Before/After** | Detect transformation language; temporal clip structure | Side-by-side: first frame vs. peak energy frame |

---

## Section 6: Rendered vs. Strategy-Only Separation

### The Core Contract

**Rendered clip** = `render_readiness_score >= 65` AND render pipeline succeeded.
Label: `READY NOW` (gold)

**Strategy-only clip** = `render_readiness_score < 65` OR pipeline failed.
Label: `STRATEGY ONLY` (muted)

Strategy-only clips still receive:
- Full hook generation
- Full caption + CTA
- Virality score
- Post order recommendation
- `strategy_only_reason` field
- `recovery_recommendation` field

They are never discarded. They are packaged and surfaced with a "Recover render" action.

### `strategy_only_reason` examples
- "Audio quality too low to render (SNR < 15dB)"
- "Video resolution below minimum threshold"
- "Source download failed — use upload instead"
- "Transcript confidence too low for accurate clip selection"

### `recovery_recommendation` examples
- "Upload higher-quality source file"
- "Re-download source from a higher-resolution URL"
- "Manually trim and re-upload this segment"

---

## Section 7: Post Order Ranking Logic

```
1. Sort by virality_score DESC (Tier 1 first)
2. Rendered clips always rank above strategy-only at equal score
3. Apply diversity_score — no two consecutive clips: same speaker + same topic
4. Platform-fit tiebreaker — best platform match surfaces first per platform filter
5. confidence_score >= 80 → no caveat
   confidence_score < 60 → "Confidence: moderate" badge
```

**Post order labels:**
- Rank 1 → `POST FIRST`
- Rank 2 → `POST SECOND`
- Rank 3 → `TEST THIRD`
- Rank 4+ → `MOVE LATER`

---

## Section 8: Backend Fields

Key fields every clip should carry (see full schema in council data roadmap):

```
clip_id, source_id, timestamp_start, timestamp_end
transcript_excerpt, visual_summary
hook, title, caption, cta
hook_variants[], caption_variants[]
thumbnail_text, top_quote
platform_fit{}, output_style, packaging_angle
virality_score, confidence_score
render_status, rendered_url, rendered_thumbnail_url
strategy_only_reason, recovery_recommendation
recommended_post_order, recommended_platform[]
creator_tags[], risk_flags[]
monetization_potential, reuse_potential
```

---

## Section 9: Frontend Product Rules

### What the user sees first
The **best clip** (highest virality_score, rendered) is visible above the fold. No scrolling required.

### Badge system
| Badge | Color | Condition |
|---|---|---|
| BEST CLIP | Gold | Rank #1, rendered |
| READY NOW | Gold | Rendered, score ≥ 55 |
| STRATEGY ONLY | Muted white | Not rendered or render failed |
| RECOVER RENDER | Blue | strategy_only_reason + recovery possible |
| HIGH CONFIDENCE | Blue | confidence_score ≥ 80 |
| REVIEW NEEDED | Red | risk_flags present |
| EVERGREEN | Purple | reuse_potential ≥ 70 |

### Required elements per card
**Best clip card**: video player, hook (large), virality score, BEST CLIP badge, top 2 platform badges, Copy Package, Queue Post, Post First, caption preview, thumbnail preview.

**Rendered clip card**: video player, READY NOW badge, virality score, post order badge, hook, caption (collapsed), CTA, Export button.

**Strategy-only card**: STRATEGY ONLY badge, RECOVER RENDER button, strategy reason, hook, caption, CTA, virality score + note, recovery recommendation.

### Product copy vocabulary
Use these exact terms, consistently:
- "Best clip first" — not "top result"
- "Ready now" — not "processed" or "available"
- "Strategy only" — not "ideas only" or "preview unavailable"
- "Recover render" — not "retry" or "regenerate"
- "Copy package" — not "copy all"
- "Queue post" — not "add to queue" or "schedule"
- "Post first" / "Test next" — not "recommended" or "suggested"
- "Export-ready" — not "download available"

---

## LWA Architecture Alignment

```
SOURCE IN
    │
    ▼
[Download / Ingest]
    │
    ▼
[Transcribe + Visual Analysis]
    │
    ▼
[Clip Detection + Scoring]
    ├── virality_score
    ├── hook_score
    ├── platform_fit
    └── confidence_score
    │
    ▼
[Render Readiness Check]
    ├── render_readiness_score >= 65 → Render pipeline → READY NOW
    └── render_readiness_score < 65 → strategy_only_reason + recovery_recommendation → STRATEGY ONLY
    │
    ▼
[Post Order Ranking]
    ├── Best clip (Rank 1) — above the fold
    ├── Rendered clips — READY NOW stack
    └── Strategy-only clips — STRATEGY ONLY rail
    │
    ▼
[Copy Package / Export / Queue Post]
```

---

*This document is the frontend/UX intelligence layer. For backend schema, roadmap, and sales positioning, see `lwa-council-data-roadmap.md`.*
