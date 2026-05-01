# Runbook — LWA Auto Editor Brain

## What was added

Two new files and two surgical patches:

1. `lwa-backend/app/services/auto_editor_brain.py` — enrichment service.
2. `lwa-backend/app/prompts/auto_editor_brain.md` — provider-agnostic prompt spec.
3. `lwa-backend/app/models/schemas.py` — five Pydantic models appended; one optional field `auto_editor: Optional[AutoEditorBrain] = None` added to `ClipResult`; `ClipResult.model_rebuild()` called to resolve the forward ref.
4. `lwa-backend/app/services/clip_service.py` — one import line; one `await enrich_clips_with_auto_editor_async(...)` call inserted after `resolve_local_asset_paths` and before `register_clip_batch`.

## Why it is safe

- No new env vars required. Reuses any existing `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`.
- No DB migration. Nothing persisted that wasn't already.
- No ffmpeg call. Export profile is metadata (recommendation only).
- No new external HTTP at import time.
- No new router. Output rides on existing `/generate`, `/v1/generate`, `/v1/jobs/{job_id}`.
- Generation cannot fail because of this layer — the call site is wrapped in `try/except` and the service is internally defensive.

## ClipResult.auto_editor fields

| Field | Type | Notes |
|---|---|---|
| `status` | `"ai" \| "heuristic" \| "skipped"` | Provenance |
| `provider` | `"anthropic" \| "openai" \| "internal" \| "heuristic"` | Which path ran |
| `provider_note` | `str \| null` | Sanitized operator note |
| `scores.viral_score` | `float 0-100` | Higher = better |
| `scores.retention_score` | `float 0-100` | Higher = better |
| `scores.hook_score` | `float 0-100` | Higher = better |
| `scores.clarity_score` | `float 0-100` | Higher = better |
| `scores.focus_score` | `float 0-100` | Higher = better |
| `scores.silence_risk_score` | `float 0-100` | **Higher = worse** |
| `scores.dead_scene_risk_score` | `float 0-100` | **Higher = worse** |
| `scores.pacing_score` | `float 0-100` | Higher = better |
| `recommendations.*` | various | Caption style, font, edit style, filter, music, b-roll, pacing |
| `export_profile_recommendation.*` | `width/height/fps/bitrate/container/label` | Metadata only — not a render |
| `customization.options` | `list[str]` | UI toggle suggestions |
| `next_edit_actions` | `list[str]` | Concrete next steps |
| `risk_flags` | `list[str]` | Risks the editor should know |

## Degradation table

| Condition | Behavior |
|---|---|
| No LLM provider configured | `status="heuristic"`, `provider_note="ai-enrichment-unavailable, returned heuristic"` |
| LLM returns invalid JSON | Heuristic baseline kept, `provider_note="ai-enrichment-error, returned heuristic"` |
| LLM call times out | Heuristic kept |
| Heuristic itself errors | `status="skipped"` with platform-appropriate `export_profile_recommendation` |
| Outer exception in clip_service | `try/except` swallows; generation completes, `auto_editor=null` on that batch |

## TypeScript types (add to api.ts when UI is ready)

```ts
export type AutoEditorStatus = "ai" | "heuristic" | "skipped";

export interface AutoEditorScores {
  viral_score: number;
  retention_score: number;
  hook_score: number;
  clarity_score: number;
  focus_score: number;
  silence_risk_score: number;       // higher == worse
  dead_scene_risk_score: number;    // higher == worse
  pacing_score: number;
}

export interface AutoEditorBrain {
  status: AutoEditorStatus;
  provider: string;
  provider_note?: string | null;
  scores: AutoEditorScores;
  recommendations: {
    caption_style_recommendation?: string | null;
    font_style_recommendation?: string | null;
    edit_style_recommendation?: string | null;
    filter_recommendation?: string | null;
    music_sync_notes?: string | null;
    b_roll_suggestions: string[];
    pacing_notes?: string | null;
  };
  export_profile_recommendation: {
    width: number; height: number; fps: number;
    bitrate: string; container: string; label: string;
  };
  customization: { options: string[] };
  next_edit_actions: string[];
  risk_flags: string[];
}

// Augment existing ClipResult:
// auto_editor?: AutoEditorBrain | null;
```

## What NOT to claim

- ❌ No 4K/8K rendering — export profile is a recommendation only.
- ❌ No blockchain, NFT, or on-chain settlement.
- ❌ No Polymarket integration.
- ❌ No real social posting beyond what already exists.
- ❌ No payout or wallet promises.

## Operating notes

- **Latency budget**: ~18s worst case (8s timeout × 2 retries + 2s slack). Heuristic path is sub-millisecond.
- **To force heuristic-only**: set `LWA_AUTO_EDITOR_LLM_TIMEOUT=0` or remove LLM API keys.
- **Model overrides**: `LWA_AUTO_EDITOR_ANTHROPIC_MODEL`, `LWA_AUTO_EDITOR_OPENAI_MODEL`.
- **Logs**: `lwa.auto_editor_brain` — watch for `ai upgrade failed`, `anthropic call failed`, `openai call failed`.
- Raw provider errors are never emitted to the response. Only `type(exc).__name__` logs at WARNING.

## Rollback

Single revert: `git revert <commit-sha> && git push origin main`

Or surgical: delete `auto_editor_brain.py` and `auto_editor_brain.md`, revert the two hunks in `schemas.py` and `clip_service.py`.
