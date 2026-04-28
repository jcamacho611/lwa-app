# Backend AI Intelligence Layer

## Purpose
The backend intelligence layer ranks clip candidates by short-form retention signals, then packages them into a creator-facing clip pack without making OpenAI mandatory.

## What Is Implemented
- heuristic scoring through `lwa-backend/app/services/attention_compiler.py`
- deterministic rank and `post_rank`
- exactly one `is_best_clip` winner per ranked batch
- explainable `score_breakdown`
- fallback `hook_variants`
- fallback `caption_variants`
- `why_this_matters`
- `retention_reason`
- `first_three_seconds_assessment`
- `frontend_badges`
- category-specific risk flags
- nonfatal OpenAI fallback

## Core Signals
- `hook_first_3s`
- `standalone_coherence`
- `emotional_spike`
- `quotable_line`
- `information_density`
- `tension_payoff_arc`
- `shareability_phrase`
- `curiosity_gap`
- `speaker_authority`
- `visual_anchor`
- `conflict_beat`
- `loopability`

## OpenAI Behavior
- if `OPENAI_API_KEY` is present, the backend can improve packaging fields
- OpenAI is not required for useful output
- provider failure falls back to heuristics
- fallback output still returns ranked clips and packaging fields

## Safe Claims
- helps rank clips
- helps package clips
- helps identify stronger openings
- gives score transparency

## Unsafe Claims
- guaranteed viral
- guaranteed views
- guaranteed revenue

## Current Limits
- no guaranteed 20–40 polished clips every run
- no direct platform posting
- no full editor timeline or caption editor
- no full campaign automation

## Related Files
- `lwa-backend/app/services/attention_compiler.py`
- `lwa-backend/app/services/clip_service.py`
- `lwa-backend/tests/test_attention_compiler.py`
