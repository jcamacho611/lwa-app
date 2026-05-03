# LWA Remaining Build Slices — Full Code Execution Pack

_Last updated: 2026-05-03_

This runbook turns the remaining LWA build work into a guarded, slice-by-slice implementation plan for Windsurf/Codex.

It is intentionally **not** permission to rewrite the app. It is a controlled execution pack.

---

## Current status

```text
Slice 1 — Director Brain v0 foundation: DONE
Lee-Wuh Agent shell: DONE
Slice 2 — Clip result intelligence contract: DONE / already exists in lwa-web/lib/types.ts
```

## Remaining execution order

```text
Slice 3  — Rendered / raw-only / strategy-only frontend truth
Slice 4  — HeroClip lead result rebuild
Slice 5  — clip-studio rendered-first layout
Slice 6  — Caption style + quality gate backend
Slice 7  — Campaign Mode backend fields
Slice 8  — Campaign Mode frontend display
Slice 9  — Proof Vault + Style Memory connection to clips
Slice 10 — Event tracking layer
Slice 11 — Whop / entitlement / credit audit and minimal lock
Slice 12 — Public launch hardening
Slice 13 — Upload / Drive ingest upgrade
Slice 14 — Batch workflow upgrade
Slice 15 — Admin/operator observability panel
```

---

## Golden rules for every slice

```text
Preserve /generate.
Do not touch lwa-ios unless explicitly told.
Do not create /backend/ml/engine.py.
Do not add sklearn.
Do not add pickle/model files.
Do not commit secrets, .env files, tokens, keys, or heavy assets.
Do not jump ahead.
One narrow slice at a time.
Commit each clean slice before starting the next one.
Prefer merge/adapt over blind replacement.
Preserve existing props, exports, routes, and API compatibility.
Never show strategy-only results as playable media.
Never invent media URLs.
Never mark a clip as rendered unless a real media URL exists.
```

---

# Windsurf autonomous execution prompt

Paste this into Windsurf when you want it to execute the remaining build safely:

```text
You are the LWA senior engineer implementing the remaining build slices from:

docs/runbooks/LWA_REMAINING_BUILD_CODE_EXECUTION_PACK.md

Current status:
- main must be clean and synced before starting
- Slice 1 Director Brain v0 is done
- Lee-Wuh Agent shell is done
- Slice 2 clip intelligence type fields already exist

Your job:
Execute the remaining slices in exact order, starting with Slice 3.

Before every slice:
1. Run git status --short.
2. Run git branch --show-current.
3. Confirm main is clean.
4. Read the target files before editing.
5. Adapt/merge the code from the slice; do not blindly replace heavily coupled files.

After every slice:
1. Run the validation commands listed for that slice.
2. Run git diff --check.
3. Run safety checks for secrets/heavy files/lwa-ios.
4. Commit only the files for that slice.
5. Push to origin main.
6. Stop and report before continuing to the next slice unless explicitly told to continue.

Universal forbidden actions:
- Do not create /backend/ml/engine.py.
- Do not add sklearn.
- Do not add pickle/model files.
- Do not touch lwa-ios.
- Do not add secrets or env files.
- Do not add heavy binary assets.
- Do not build blockchain, NFTs, direct social posting, full editor, or full Google OAuth in this run.

Code quality boost requirement:
For each slice, improve the provided code before committing by:
- preserving existing props/types and imports
- removing duplicate helper logic where practical
- extracting small helpers only when they reduce risk
- keeping fallbacks honest
- keeping errors nonfatal when the user can continue
- using existing repo styling/classes where possible
- avoiding new dependencies
- keeping TypeScript/Python compile clean

Start with Slice 3 only.
```

---

# Slice 3 — Rendered / raw-only / strategy-only frontend truth

## Goal

Update the clip card UI so LWA clearly separates:

```text
rendered clips
raw-only clips
strategy-only clips
```

Strategy-only results must never look playable.

## Target file

```text
lwa-web/components/VideoCard.tsx
```

Only touch if absolutely required:

```text
lwa-web/lib/types.ts
lwa-web/components/HeroClip.tsx
```

## Implementation requirements

Add/adapt helper logic:

```tsx
export function getClipPreviewUrl(clip: ClipResult) {
  return clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url || null;
}

export function getClipDownloadUrl(clip: ClipResult) {
  return clip.download_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url || null;
}

export function getRenderState(clip: ClipResult) {
  const explicit = String(clip.render_status || clip.rendered_status || "").toLowerCase();

  if (clip.strategy_only || clip.is_strategy_only || explicit === "strategy_only") return "strategy_only";
  if (explicit === "raw_only") return "raw_only";
  if (explicit === "failed" || explicit === "render_failed") return "failed";
  if (explicit === "queued" || explicit === "pending") return "queued";
  if (explicit === "processing" || explicit === "rendering") return "processing";
  if (explicit === "rendered" || explicit === "ready") return getClipPreviewUrl(clip) ? "rendered" : "strategy_only";
  if (getClipPreviewUrl(clip) || getClipDownloadUrl(clip)) return "rendered";
  if (clip.raw_clip_url) return "raw_only";
  return "strategy_only";
}
```

Required UI behavior:

```text
Rendered:
- badge: Rendered / Ready now / Export-ready
- show video/player only when real URL exists
- show post_rank/rank if present
- show score/confidence if present
- show hook, caption, thumbnail text, CTA
- copy buttons for hook, caption, CTA, package

Raw-only:
- badge: Raw clip / Needs polish
- do not pretend edited export exists
- show raw clip action only if raw_clip_url exists
- show recover/edit copy where safe

Strategy-only:
- badge: Strategy only / Not yet rendered
- no video element
- no download/export-ready language
- show why_this_matters
- show hook_variants
- show caption_style
- show thumbnail_text
- show cta_suggestion
- show reason_not_rendered if present
- show copy strategy/package button

Campaign metadata:
- show campaign_role badge if present
- show funnel_stage if present
- use suggested_cta as CTA fallback
```

## Validation

```bash
cd lwa-web
npm run type-check || npm run typecheck || true
npm run build
cd ..
git diff --check
git status --short
```

## Commit

```bash
git add lwa-web/components/VideoCard.tsx
git commit -m "feat(web): separate rendered and strategy clip cards"
git push origin main
```

---

# Slice 4 — HeroClip lead result rebuild

## Goal

Make the best clip appear first and feel like the obvious next action.

## Target file

```text
lwa-web/components/HeroClip.tsx
```

Only touch if required:

```text
lwa-web/lib/types.ts
lwa-web/components/VideoCard.tsx
```

## Implementation requirements

HeroClip must support either a single `clip` prop or a `clips` array if practical.

Lead selection should prefer rendered clips, then rank/score:

```tsx
export function chooseLeadClip(clips: ClipResult[]) {
  if (!clips.length) return null;

  const withState = clips.map((clip) => ({ clip, state: getRenderState(clip) }));
  const rendered = withState.filter((entry) => entry.state === "rendered").map((entry) => entry.clip);
  const candidates = rendered.length ? rendered : clips;

  return [...candidates].sort((a, b) => {
    const aRank = a.post_rank || a.rank || a.suggested_post_order || 999;
    const bRank = b.post_rank || b.rank || b.suggested_post_order || 999;
    const aScore = a.score || a.confidence_score || a.confidence || a.virality_score || 0;
    const bScore = b.score || b.confidence_score || b.confidence || b.virality_score || 0;
    return aRank - bRank || bScore - aScore;
  })[0];
}
```

HeroClip must show:

```text
best clip / lead result
post order #1 when present
score/confidence when present
preview only if rendered URL exists
render state badge
recommended platform when present
why_this_matters when present
thumbnail_text when present
cta_suggestion or suggested_cta when present
caption_style when present
campaign_role / funnel_stage when present
copy package button
export only when real media URL exists
recover button only when safe/nonfatal
```

Critical rules:

```text
No fake download/export URL.
No video element for strategy-only.
No claim that strategy-only is ready now.
```

## Validation

```bash
cd lwa-web
npm run type-check || npm run typecheck || true
npm run build
cd ..
git diff --check
git status --short
```

## Commit

```bash
git add lwa-web/components/HeroClip.tsx
git commit -m "feat(web): rebuild lead clip result card"
git push origin main
```

---

# Slice 5 — clip-studio rendered-first layout

## Goal

Make the main generate/results surface feel like a real clipping product.

## Target file

```text
lwa-web/components/clip-studio.tsx
```

Only touch if required:

```text
lwa-web/components/HeroClip.tsx
lwa-web/components/VideoCard.tsx
lwa-web/lib/types.ts
```

## Implementation requirements

Add/adapt a rendered-first result grouping component around the existing generate state.

```tsx
function groupClips(clips: ClipResult[]) {
  return {
    rendered: clips.filter((clip) => getRenderState(clip) === "rendered"),
    rawOnly: clips.filter((clip) => getRenderState(clip) === "raw_only"),
    strategyOnly: clips.filter((clip) => getRenderState(clip) === "strategy_only"),
    failed: clips.filter((clip) => getRenderState(clip) === "failed"),
  };
}
```

Required layout:

```text
1. Source intake
2. LWA recommendation rail
3. Processing phase tracker
4. Lead best clip
5. Rendered clips lane
6. Raw-only clips lane
7. Strategy-only lane
8. Packaging/export rail
```

Result behavior:

```text
source input remains first
generate button remains obvious
platform override is secondary
recommendations display if present
lead result appears before grid
rendered clips are visually highest priority
strategy-only lane is secondary
raw-only lane is clearly labeled
export rail collects hook/caption/thumbnail/CTA/post order
mobile layout stacks cleanly
```

Use existing result variable name. If current state is `result`, render:

```tsx
{result ? <RenderedFirstResults response={result} /> : null}
```

If the state variable is named differently, use the existing state name. Do not alter generation logic unless required.

## Validation

```bash
cd lwa-web
npm run type-check || npm run typecheck || true
npm run build
cd ..
git diff --check
git status --short
```

## Commit

```bash
git add lwa-web/components/clip-studio.tsx lwa-web/components/HeroClip.tsx lwa-web/components/VideoCard.tsx
git commit -m "feat(web): upgrade clip studio rendered-first flow"
git push origin main
```

---

# Slice 6 — Caption style + quality gate backend

## Goal

Backend output should honestly describe whether a clip is ready, risky, failed, raw-only, or strategy-only.

## Target file

```text
lwa-backend/app/services/clip_service.py
```

## Implementation helpers

Add/adapt deterministic helpers near other clip enrichment helpers:

```python
from typing import Any, Dict, Optional


def _clip_media_url(clip: Dict[str, Any]) -> Optional[str]:
    return (
        clip.get("preview_url")
        or clip.get("edited_clip_url")
        or clip.get("download_url")
        or clip.get("clip_url")
    )


def _clip_raw_url(clip: Dict[str, Any]) -> Optional[str]:
    return clip.get("raw_clip_url")


def classify_render_state(clip: Dict[str, Any]) -> Dict[str, Any]:
    media_url = _clip_media_url(clip)
    raw_url = _clip_raw_url(clip)
    warnings = list(clip.get("quality_gate_warnings") or [])

    if clip.get("strategy_only") or clip.get("is_strategy_only"):
        status = "strategy_only"
        readiness = 0.25
        warnings.append("This result is strategy-only and does not include playable media.")
    elif media_url:
        status = "rendered"
        readiness = 0.9
    elif raw_url:
        status = "raw_only"
        readiness = 0.62
        warnings.append("Raw clip exists, but edited/export-ready media is not available yet.")
    else:
        status = "strategy_only"
        readiness = 0.25
        warnings.append("No playable media URL is available for this clip.")

    start = clip.get("start") or clip.get("start_time") or clip.get("start_seconds") or clip.get("timestamp_start")
    end = clip.get("end") or clip.get("end_time") or clip.get("end_seconds") or clip.get("timestamp_end")
    if start is not None and end is not None:
        try:
            if float(end) <= float(start):
                warnings.append("Clip timestamps are invalid or reversed.")
                readiness = min(readiness, 0.35)
        except (TypeError, ValueError):
            pass

    quality_gate_status = "pass" if readiness >= 0.8 else "warning" if readiness >= 0.5 else "fail"

    return {
        **clip,
        "render_status": status,
        "strategy_only": status == "strategy_only",
        "quality_gate_status": quality_gate_status,
        "quality_gate_warnings": list(dict.fromkeys(warnings)),
        "render_readiness_score": round(readiness, 2),
        "reason_not_rendered": clip.get("reason_not_rendered") or (warnings[0] if warnings and status != "rendered" else None),
    }


def recommend_caption_style(clip: Dict[str, Any], platform: Optional[str] = None) -> Dict[str, Any]:
    text = " ".join(
        str(value or "")
        for value in [clip.get("title"), clip.get("hook"), clip.get("caption"), clip.get("transcript")]
    ).lower()

    if any(word in text for word in ["stop", "wrong", "mistake", "truth"]):
        style = "bold_interrupt"
        reason = "The clip has tension language that benefits from bold interruption captions."
    elif any(word in text for word in ["how", "step", "learn", "because", "why"]):
        style = "educational_clean"
        reason = "The clip teaches or explains, so readable educational captions fit best."
    elif platform and platform.lower() in {"tiktok", "instagram", "instagram reels", "reels"}:
        style = "fast_punchy"
        reason = "Short-form platform fit favors quick, punchy caption beats."
    else:
        style = "clean_standard"
        reason = "Default clean caption style is safest for this clip."

    emphasis_words = [word for word in ["stop", "truth", "mistake", "money", "proof", "watch", "system"] if word in text]

    return {
        "caption_style": clip.get("caption_style") or style,
        "caption_style_reason": clip.get("caption_style_reason") or reason,
        "emphasis_words": clip.get("emphasis_words") or emphasis_words[:4],
        "suggested_caption_position": clip.get("suggested_caption_position") or "lower_middle",
    }


def enrich_clip_quality_metadata(clip: Dict[str, Any], platform: Optional[str] = None) -> Dict[str, Any]:
    enriched = classify_render_state(clip)
    return {**enriched, **recommend_caption_style(enriched, platform)}
```

Apply helper to final clip list before response return:

```python
clips = [enrich_clip_quality_metadata(clip, platform=target_platform) for clip in clips]
```

If the variable is not `clips`, adapt to the final list variable.

## Validation

```bash
python3 -m compileall lwa-backend/app
pytest lwa-backend/tests -q || true
git diff --check
git status --short
```

## Commit

```bash
git add lwa-backend/app/services/clip_service.py
git commit -m "feat(api): add clip quality gates and caption style"
git push origin main
```

---

# Slice 7 — Campaign Mode backend fields

## Goal

Turn one source into a campaign stack, not just a list of clips.

## Target file

```text
lwa-backend/app/services/clip_service.py
```

## Implementation helpers

```python
from typing import Any, Dict, Optional


def default_cta_for_role(role: str) -> str:
    return {
        "lead_clip": "Comment if you want the full breakdown.",
        "trust_clip": "Save this before you plan your next post.",
        "sales_clip": "Start with LWA and turn one source into a campaign.",
        "educational_clip": "Save this and use it on your next clip.",
        "controversy_clip": "Drop your take in the comments.",
        "retargeting_clip": "Come back and export the full campaign pack.",
        "community_clip": "Tag someone who needs this system.",
    }.get(role, "Follow for the next part.")


def assign_campaign_role(clip: Dict[str, Any], index: int, platform: Optional[str] = None) -> Dict[str, Any]:
    text = " ".join(str(value or "") for value in [clip.get("title"), clip.get("hook"), clip.get("caption")]).lower()

    if index == 0 or any(word in text for word in ["stop", "watch", "truth", "nobody", "first"]):
        role = "lead_clip"
        stage = "awareness"
        reason = "Strong opener suited to start the posting sequence."
    elif any(word in text for word in ["proof", "result", "case", "why", "because"]):
        role = "trust_clip"
        stage = "consideration"
        reason = "Builds credibility after the lead clip."
    elif any(word in text for word in ["buy", "book", "join", "offer", "client", "pay", "revenue"]):
        role = "sales_clip"
        stage = "conversion"
        reason = "Contains action or offer language."
    elif any(word in text for word in ["how", "learn", "step", "teach"]):
        role = "educational_clip"
        stage = "consideration"
        reason = "Explains or teaches a useful idea."
    elif any(word in text for word in ["wrong", "mistake", "controversial", "unpopular"]):
        role = "controversy_clip"
        stage = "awareness"
        reason = "Likely to trigger debate or comments."
    else:
        role = "community_clip"
        stage = "engagement"
        reason = "Best used to keep the audience interacting."

    post_order = clip.get("post_rank") or clip.get("rank") or index + 1

    return {
        **clip,
        "campaign_role": clip.get("campaign_role") or role,
        "campaign_reason": clip.get("campaign_reason") or reason,
        "funnel_stage": clip.get("funnel_stage") or stage,
        "suggested_post_order": clip.get("suggested_post_order") or post_order,
        "suggested_platform": clip.get("suggested_platform") or clip.get("recommended_platform") or platform or clip.get("platform") or "tiktok",
        "suggested_caption_style": clip.get("suggested_caption_style") or clip.get("caption_style") or "fast_punchy",
        "suggested_cta": clip.get("suggested_cta") or clip.get("cta_suggestion") or default_cta_for_role(role),
    }


def enrich_campaign_metadata(clips: list[Dict[str, Any]], platform: Optional[str] = None) -> list[Dict[str, Any]]:
    ranked = sorted(
        clips,
        key=lambda clip: (clip.get("post_rank") or clip.get("rank") or 999, -(clip.get("score") or clip.get("confidence_score") or 0)),
    )
    by_id = {id(clip): index for index, clip in enumerate(ranked)}
    return [assign_campaign_role(clip, by_id.get(id(clip), index), platform=platform) for index, clip in enumerate(clips)]
```

Apply after quality metadata if Slice 6 exists:

```python
clips = [enrich_clip_quality_metadata(clip, platform=target_platform) for clip in clips]
clips = enrich_campaign_metadata(clips, platform=target_platform)
```

## Validation

```bash
python3 -m compileall lwa-backend/app
pytest lwa-backend/tests -q || true
git diff --check
git status --short
```

## Commit

```bash
git add lwa-backend/app/services/clip_service.py
git commit -m "feat(api): add campaign mode clip metadata"
git push origin main
```

---

# Slice 8 — Campaign Mode frontend display

## Goal

Make campaign role and posting order visible in the clipping UI.

## Target files

```text
lwa-web/components/VideoCard.tsx
lwa-web/components/HeroClip.tsx
```

## Implementation requirements

If not already covered by Slices 3 and 4, add a reusable campaign meta block:

```tsx
function campaignLabel(role?: string | null) {
  const labels: Record<string, string> = {
    lead_clip: "Lead",
    trust_clip: "Trust",
    sales_clip: "Sales",
    educational_clip: "Teach",
    controversy_clip: "Debate",
    retargeting_clip: "Retarget",
    community_clip: "Community",
  };
  return role ? labels[role] || role.replaceAll("_", " ") : null;
}

function CampaignMeta({ clip }: { clip: ClipResult }) {
  const role = campaignLabel(clip.campaign_role);
  if (!role && !clip.funnel_stage && !clip.campaign_reason && !clip.suggested_post_order && !clip.suggested_cta) return null;

  return (
    <div className="rounded-2xl border border-violet-300/20 bg-violet-300/[0.06] p-4">
      <div className="flex flex-wrap gap-2">
        {role && <span className="rounded-full bg-violet-300/15 px-3 py-1 text-xs font-bold text-violet-100">{role}</span>}
        {clip.funnel_stage && <span className="rounded-full bg-white/[0.06] px-3 py-1 text-xs text-white/70">{clip.funnel_stage}</span>}
        {clip.suggested_post_order && <span className="rounded-full bg-[#C9A24A]/15 px-3 py-1 text-xs font-bold text-[#E9C77B]">Post #{clip.suggested_post_order}</span>}
      </div>
      {clip.campaign_reason && <p className="mt-3 text-sm leading-6 text-white/70">{clip.campaign_reason}</p>}
      {clip.suggested_cta && <p className="mt-3 text-sm font-semibold leading-6 text-white/80">CTA: {clip.suggested_cta}</p>}
    </div>
  );
}
```

Place below `why_this_matters` or campaign explanation:

```tsx
<CampaignMeta clip={clip} />
```

For HeroClip:

```tsx
<CampaignMeta clip={lead} />
```

## Validation

```bash
cd lwa-web
npm run type-check || npm run typecheck || true
npm run build
cd ..
git diff --check
git status --short
```

## Commit

```bash
git add lwa-web/components/VideoCard.tsx lwa-web/components/HeroClip.tsx
git commit -m "feat(web): display campaign mode metadata"
git push origin main
```

---

# Slice 9 — Proof Vault + Style Memory connection to clips

## Goal

Let users save wins/rejections from generated clips so LWA starts learning.

## Target files

```text
lwa-web/lib/api.ts
lwa-web/components/VideoCard.tsx
lwa-web/components/HeroClip.tsx
```

## API helpers

Add or adapt in `lwa-web/lib/api.ts`:

```ts
export type ProofAssetPayload = {
  asset_type: "clip" | "hook" | "caption" | "thumbnail" | "full_video" | "campaign";
  source_url?: string | null;
  clip_url?: string | null;
  hook_text?: string | null;
  caption_text?: string | null;
  platform?: string | null;
  duration_seconds?: number | null;
  ai_score?: number | null;
  style_tags?: string[];
  project_id?: string | null;
};

export async function saveProofAsset(payload: ProofAssetPayload, token?: string | null) {
  return jsonRequest<{ success: boolean; asset: unknown; message: string }>("/api/v1/proof-vault/assets", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateProofAssetStatus(
  proofId: string,
  payload: {
    status?: "winning" | "rejected" | "pending" | "archived";
    performance_notes?: Record<string, unknown>;
    style_tags?: string[];
    rejected_reason?: string;
    approved_by?: string;
  },
  token?: string | null,
) {
  return jsonRequest<{ success: boolean; asset: unknown; message: string }>(
    `/api/v1/proof-vault/assets/${encodeURIComponent(proofId)}`,
    {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    },
  );
}

export async function submitClipStyleFeedback(
  payload: {
    clip_id: string;
    approved: boolean;
    feedback_notes?: string;
    style_tags?: string[];
  },
  token?: string | null,
) {
  const params = new URLSearchParams({ clip_id: payload.clip_id, approved: String(payload.approved) });
  if (payload.feedback_notes) params.set("feedback_notes", payload.feedback_notes);
  for (const tag of payload.style_tags || []) params.append("style_tags", tag);

  return jsonRequest<{ success: boolean; message: string; learnings?: string[] }>(
    `/api/v1/style-memory/learn/clip-feedback?${params.toString()}`,
    {
      method: "POST",
      headers: authHeaders(token, false),
    },
  );
}
```

UI actions must be nonfatal and should show success/error messages.

Rules:

```text
Strategy-only clips can save hook/strategy but not fake rendered proof.
Rendered clips can save clip_url only if a real URL exists.
Learning failures must not crash the UI.
```

## Validation

```bash
cd lwa-web
npm run type-check || npm run typecheck || true
npm run build
cd ..
git diff --check
git status --short
```

## Commit

```bash
git add lwa-web/lib/api.ts lwa-web/components/VideoCard.tsx lwa-web/components/HeroClip.tsx
git commit -m "feat(web): connect clip results to proof and style memory"
git push origin main
```

---

# Slice 10 — Event tracking layer

## Goal

Add lightweight metadata-only telemetry without third-party dependencies.

## Backend file: `lwa-backend/app/services/event_tracking.py`

```python
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

ALLOWED_EVENTS = {
    "generate_clicked",
    "source_added",
    "clip_generated",
    "clip_saved",
    "clip_rejected",
    "hook_approved",
    "hook_rejected",
    "export_clicked",
    "payment_started",
    "payment_completed",
    "opportunity_opened",
    "campaign_packaged",
    "style_memory_updated",
    "lee_wuh_action_triggered",
    "director_brain_scored",
    "director_brain_ranked",
}

EVENTS: List[Dict[str, Any]] = []


def track_event(event_name: str, user_id: str = "guest", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if event_name not in ALLOWED_EVENTS:
        raise ValueError(f"Unsupported event: {event_name}")

    event = {
        "id": f"evt_{uuid4().hex[:12]}",
        "event_name": event_name,
        "user_id": user_id or "guest",
        "metadata": metadata or {},
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    EVENTS.append(event)
    return event


def list_events(limit: int = 100) -> List[Dict[str, Any]]:
    return EVENTS[-max(1, min(limit, 500)):]


def event_stats() -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for event in EVENTS:
        counts[event["event_name"]] = counts.get(event["event_name"], 0) + 1
    return counts


def get_status() -> Dict[str, Any]:
    return {
        "success": True,
        "mode": "metadata_only_v0",
        "event_count": len(EVENTS),
        "allowed_events": sorted(ALLOWED_EVENTS),
    }
```

## Backend file: `lwa-backend/app/api/routes/events.py`

```python
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...services.event_tracking import event_stats, get_status, list_events, track_event

router = APIRouter(prefix="/api/v1/events", tags=["events"])


class TrackEventRequest(BaseModel):
    event_name: str
    user_id: Optional[str] = "guest"
    metadata: Optional[Dict[str, Any]] = None


@router.post("/track", response_model=Dict[str, Any])
async def track_lwa_event(request: TrackEventRequest):
    try:
        event = track_event(request.event_name, user_id=request.user_id or "guest", metadata=request.metadata)
        return {"success": True, "event": event}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/recent", response_model=Dict[str, Any])
async def get_recent_events(limit: int = Query(100, ge=1, le=500)):
    return {"success": True, "events": list_events(limit), "count": len(list_events(limit))}


@router.get("/stats", response_model=Dict[str, Any])
async def get_event_stats():
    return {"success": True, "stats": event_stats()}


@router.get("/status", response_model=Dict[str, Any])
async def get_event_tracking_status():
    return get_status()
```

Register in `lwa-backend/app/main.py`:

```python
from .api.routes.events import router as events_router
```

```python
app.include_router(events_router)
```

## Frontend file: `lwa-web/lib/events-api.ts`

```ts
export type LwaEventName =
  | "generate_clicked"
  | "source_added"
  | "clip_generated"
  | "clip_saved"
  | "clip_rejected"
  | "hook_approved"
  | "hook_rejected"
  | "export_clicked"
  | "payment_started"
  | "payment_completed"
  | "opportunity_opened"
  | "campaign_packaged"
  | "style_memory_updated"
  | "lee_wuh_action_triggered"
  | "director_brain_scored"
  | "director_brain_ranked";

async function eventRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};
  if (!response.ok) throw new Error(data?.detail || data?.message || "Event request failed");
  return data as T;
}

export async function trackLwaEvent(event_name: LwaEventName, metadata?: Record<string, unknown>, user_id = "guest") {
  try {
    return await eventRequest<{ success: boolean; event: Record<string, unknown> }>("/api/v1/events/track", {
      method: "POST",
      body: JSON.stringify({ event_name, user_id, metadata: metadata || {} }),
    });
  } catch (error) {
    console.warn("[LWA_EVENT_TRACKING_FAILED]", error);
    return null;
  }
}

export function getRecentLwaEvents(limit = 100) {
  return eventRequest<{ success: boolean; events: Array<Record<string, unknown>>; count: number }>(`/api/v1/events/recent?limit=${limit}`);
}

export function getLwaEventStats() {
  return eventRequest<{ success: boolean; stats: Record<string, number> }>("/api/v1/events/stats");
}
```

## Validation

```bash
python3 -m compileall lwa-backend/app
cd lwa-web
npm run type-check || npm run typecheck || true
npm run build
cd ..
git diff --check
git status --short
```

## Commit

```bash
git add lwa-backend/app/services/event_tracking.py lwa-backend/app/api/routes/events.py lwa-backend/app/main.py lwa-web/lib/events-api.ts
git commit -m "feat: add metadata event tracking layer"
git push origin main
```

---

# Slice 11 — Whop / entitlement / credit audit and minimal lock

## Phase A — audit only

```bash
grep -R "WHOP\|whop\|entitlement\|credits\|plan\|checkout\|FREE_LAUNCH_MODE" -n lwa-backend lwa-web
```

Return what exists, what is missing, exact files found, files likely involved, smallest safe implementation plan, and validation checklist.

## Phase B — minimal frontend lock helper

Only after audit, add/adapt:

`lwa-web/lib/entitlement-api.ts`

```ts
export type EntitlementStatus = {
  entitled: boolean;
  hasActiveSubscription?: boolean;
  creditsRemaining?: number;
  tier?: string;
  reason?: string;
  upgradeUrl?: string;
  checkoutUrl?: string;
  freeLaunchMode?: boolean;
};

async function entitlementRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};
  if (!response.ok) throw new Error(data?.detail || data?.message || "Entitlement request failed");
  return data as T;
}

export async function checkExportEntitlement(requestId?: string): Promise<EntitlementStatus> {
  try {
    return await entitlementRequest<EntitlementStatus>("/api/entitlement", {
      method: "POST",
      body: JSON.stringify({ action: "export", requestId }),
    });
  } catch (error) {
    console.warn("[LWA_ENTITLEMENT_FAILED]", error);
    return {
      entitled: false,
      reason: "Could not verify export access.",
      upgradeUrl: "https://whop.com/lwa/",
      checkoutUrl: "https://whop.com/lwa/",
    };
  }
}
```

`lwa-web/app/api/entitlement/route.ts`

```ts
import { NextRequest, NextResponse } from "next/server";

const CHECKOUT_URL = process.env.NEXT_PUBLIC_WHOP_CHECKOUT_URL || process.env.WHOP_CHECKOUT_URL || "https://whop.com/lwa/";
const FREE_LAUNCH_MODE = process.env.FREE_LAUNCH_MODE === "true" || process.env.NEXT_PUBLIC_FREE_LAUNCH_MODE === "true";

export async function GET() {
  return NextResponse.json({
    entitled: FREE_LAUNCH_MODE,
    hasActiveSubscription: false,
    creditsRemaining: FREE_LAUNCH_MODE ? 999 : 0,
    tier: FREE_LAUNCH_MODE ? "free_launch" : "free",
    checkoutUrl: CHECKOUT_URL,
    upgradeUrl: CHECKOUT_URL,
    freeLaunchMode: FREE_LAUNCH_MODE,
  });
}

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));
  const action = String(body.action || "export");

  if (FREE_LAUNCH_MODE) {
    return NextResponse.json({
      entitled: true,
      action,
      tier: "free_launch",
      creditsRemaining: 999,
      freeLaunchMode: true,
      message: "Free launch mode enabled.",
    });
  }

  if (action === "preview" || action === "generate") {
    return NextResponse.json({
      entitled: true,
      action,
      tier: "free",
      creditsRemaining: 1,
      checkoutUrl: CHECKOUT_URL,
      upgradeUrl: CHECKOUT_URL,
    });
  }

  return NextResponse.json({
    entitled: false,
    action,
    reason: "Export requires an active LWA plan.",
    currentTier: "free",
    tier: "free",
    creditsRemaining: 0,
    checkoutUrl: CHECKOUT_URL,
    upgradeUrl: CHECKOUT_URL,
    freeLaunchMode: false,
  });
}
```

## Validation

```bash
cd lwa-web
npm run type-check || npm run typecheck || true
npm run build
cd ..
git diff --check
git status --short
```

## Commit

```bash
git add lwa-web/lib/entitlement-api.ts lwa-web/app/api/entitlement/route.ts
git commit -m "feat: add minimal export entitlement lock"
git push origin main
```

---

# Slice 12 — Public launch hardening

## Goal

The app should not embarrass the company when a buyer, investor, or first user tries it.

## Backend fallback helper

Add to a safe backend service, preferably a new helper if cleaner:

```python
from typing import Any, Dict, List, Optional
from uuid import uuid4


def build_strategy_only_fallback(source_url: Optional[str], reason: str, target_platform: str = "tiktok") -> Dict[str, Any]:
    request_id = f"fallback_{uuid4().hex[:10]}"
    clips: List[Dict[str, Any]] = [
        {
            "id": f"{request_id}_strategy_1",
            "request_id": request_id,
            "title": "Best available strategy angle",
            "hook": "Turn the strongest moment into a clear first-post hook.",
            "caption": "Use this as a strategy fallback until the source can be processed.",
            "score": 0.62,
            "rank": 1,
            "post_rank": 1,
            "target_platform": target_platform,
            "recommended_platform": target_platform,
            "render_status": "strategy_only",
            "strategy_only": True,
            "reason_not_rendered": reason,
            "quality_gate_status": "fail",
            "quality_gate_warnings": [reason, "No rendered media was created for this fallback result."],
            "render_readiness_score": 0.2,
            "why_this_matters": "This keeps the user moving with honest packaging guidance instead of crashing.",
            "thumbnail_text": "Strategy fallback",
            "cta_suggestion": "Upload the file directly or try another public source.",
            "caption_style": "clean_standard",
        }
    ]
    return {
        "request_id": request_id,
        "video_url": source_url or "",
        "status": "fallback_strategy_only",
        "status_reason": reason,
        "processing_summary": {
            "target_platform": target_platform,
            "recommended_platform": target_platform,
            "rendered_clip_count": 0,
            "strategy_only_clip_count": len(clips),
            "fallback_reason": reason,
            "recommended_next_step": "Upload the source file directly or try another public source.",
        },
        "clips": clips,
    }
```

Frontend safe error helper:

```ts
export function userSafeGenerateError(error: unknown) {
  const message = error instanceof Error ? error.message : String(error || "Generation failed.");
  const lower = message.toLowerCase();
  if (lower.includes("cookies") || lower.includes("bot") || lower.includes("yt-dlp") || lower.includes("platform")) {
    return "This platform blocked server access. Upload the video/audio file directly, try another public source, or use prompt mode.";
  }
  return message || "Generation failed. Try another source or upload the file directly.";
}
```

Add launch checklist at:

```text
docs/runbooks/LWA_PUBLIC_LAUNCH_CHECKLIST.md
```

Checklist content:

```md
# LWA Public Launch Checklist

## Required Railway env vars

- NEXT_PUBLIC_API_BASE_URL
- FREE_LAUNCH_MODE=true for public demo launch
- NEXT_PUBLIC_WHOP_CHECKOUT_URL
- WHOP_WEBHOOK_SECRET when Whop webhooks are live
- ALLOWED_ORIGINS

## Smoke tests

1. Open `/first-mission`.
2. Choose Content Mission.
3. Generate with a public source.
4. Confirm rendered clips show only when URLs exist.
5. Confirm strategy-only fallback is honest.
6. Confirm export lock shows checkout when not entitled.
7. Confirm `/command-center` loads.
```

## Validation

```bash
python3 -m compileall lwa-backend/app
pytest lwa-backend/tests -q || true
cd lwa-web
npm run type-check || npm run typecheck || true
npm run build
cd ..
git diff --check
git status --short
```

## Commit

```bash
git add docs/runbooks/LWA_PUBLIC_LAUNCH_CHECKLIST.md lwa-backend/app lwa-web
git commit -m "chore: harden public launch flow"
git push origin main
```

---

# Slice 13 — Upload / Drive ingest upgrade

## Goal

Move beyond public URLs while preserving current URL flow.

## Target file

```text
lwa-web/components/clip-studio.tsx
```

Only touch backend upload route if the existing endpoint shape is broken.

## Frontend behavior

Add upload progress state if missing:

```tsx
const [uploading, setUploading] = useState(false);
const [uploadError, setUploadError] = useState<string | null>(null);
const [uploadedSourceId, setUploadedSourceId] = useState<string | null>(null);

async function handleSourceUpload(file: File) {
  setUploading(true);
  setUploadError(null);
  try {
    const uploaded = await uploadSource(file, token);
    const id = uploaded.file_id || uploaded.id || uploaded.source_ref?.upload_id || null;
    setUploadedSourceId(id);
    if (uploaded.public_url) setVideoUrl(uploaded.public_url);
  } catch (error) {
    setUploadError(error instanceof Error ? error.message : "Upload failed.");
  } finally {
    setUploading(false);
  }
}
```

Add file input:

```tsx
<label className="inline-flex cursor-pointer items-center justify-center rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white/75 transition hover:bg-white/[0.06]">
  {uploading ? "Uploading..." : "Upload source"}
  <input
    type="file"
    accept="video/*,audio/*"
    className="hidden"
    disabled={uploading}
    onChange={(event) => {
      const file = event.target.files?.[0];
      if (file) void handleSourceUpload(file);
    }}
  />
</label>
{uploadError && <p className="text-sm text-red-300">{uploadError}</p>}
{uploadedSourceId && <p className="text-sm text-emerald-300">Upload ready: {uploadedSourceId}</p>}
```

Add Drive placeholder only, unless OAuth is already env-gated and complete:

```tsx
<button
  type="button"
  disabled
  title="Google Drive import will be enabled after OAuth is configured."
  className="rounded-full border border-white/10 px-5 py-3 text-sm font-semibold text-white/35"
>
  Drive import soon
</button>
```

## Validation

```bash
cd lwa-web
npm run type-check || npm run typecheck || true
npm run build
cd ..
git diff --check
git status --short
```

## Commit

```bash
git add lwa-web/components/clip-studio.tsx
git commit -m "feat(web): improve source upload ingest flow"
git push origin main
```

---

# Slice 14 — Batch workflow upgrade

## Goal

Let operators approve, reject, regenerate, save, and bulk-copy packages.

## Target file

```text
lwa-web/components/command-center/BatchReviewPanel.tsx
```

Only touch `lwa-web/lib/api.ts` if helper imports are needed.

## Implementation requirements

Add selection state:

```tsx
const [selectedClipIds, setSelectedClipIds] = useState<string[]>([]);
const [batchMessage, setBatchMessage] = useState<string | null>(null);

function toggleClipSelection(clipId: string) {
  setSelectedClipIds((current) =>
    current.includes(clipId) ? current.filter((id) => id !== clipId) : [...current, clipId],
  );
}
```

Add bulk copy and save actions:

```tsx
async function bulkCopyPackage(clips: ClipResult[]) {
  const selected = clips.filter((clip) => selectedClipIds.includes(clip.id));
  const text = selected
    .map((clip, index) => [
      `#${index + 1} ${clip.title}`,
      `Hook: ${clip.hook}`,
      `Caption: ${clip.caption}`,
      clip.thumbnail_text ? `Thumbnail: ${clip.thumbnail_text}` : null,
      clip.cta_suggestion || clip.suggested_cta ? `CTA: ${clip.cta_suggestion || clip.suggested_cta}` : null,
    ].filter(Boolean).join("\n"))
    .join("\n\n---\n\n");
  await navigator.clipboard.writeText(text);
  setBatchMessage(`Copied ${selected.length} clip packages.`);
}
```

Action bar:

```tsx
{selectedClipIds.length > 0 && (
  <div className="sticky top-4 z-20 rounded-2xl border border-[#C9A24A]/25 bg-[#15110a] p-4 text-white shadow-xl">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <p className="text-sm font-bold">{selectedClipIds.length} selected</p>
      <div className="flex flex-wrap gap-2">
        <button onClick={() => bulkCopyPackage(clips)} className="rounded-full border border-white/12 px-4 py-2 text-xs font-bold">Copy packages</button>
        <button onClick={() => setSelectedClipIds([])} className="rounded-full border border-white/12 px-4 py-2 text-xs font-bold">Clear</button>
      </div>
    </div>
  </div>
)}
{batchMessage && <p className="rounded-2xl border border-emerald-300/25 bg-emerald-300/10 p-3 text-sm text-emerald-100">{batchMessage}</p>}
```

## Validation

```bash
cd lwa-web
npm run type-check || npm run typecheck || true
npm run build
cd ..
git diff --check
git status --short
```

## Commit

```bash
git add lwa-web/components/command-center/BatchReviewPanel.tsx lwa-web/lib/api.ts
git commit -m "feat: improve batch clip review workflow"
git push origin main
```

---

# Slice 15 — Admin/operator observability panel

## Goal

Founder/operator should see what is happening without exposing secrets.

## Backend service: `lwa-backend/app/services/operator_status.py`

```python
from typing import Any, Dict


def get_operator_status() -> Dict[str, Any]:
    return {
        "success": True,
        "mode": "metadata_only_v0",
        "provider_status": {
            "paid_providers_enabled": False,
            "render_provider": "env_gated",
            "ai_provider": "env_gated",
        },
        "mock_live_flags": {
            "free_launch_mode": "env_controlled",
            "whop_webhooks": "registered_if_configured",
            "direct_posting": "disabled",
        },
        "health": {
            "backend": "ok",
            "generated_assets_mount": "/generated",
            "uploads_mount": "/uploads",
        },
        "warnings": [
            "Verify Railway environment variables before public launch.",
            "Keep paid providers disabled unless explicitly configured.",
            "Strategy-only clips must not be presented as rendered exports.",
        ],
    }
```

## Backend route: `lwa-backend/app/api/routes/admin_ops.py`

```python
from typing import Any, Dict

from fastapi import APIRouter

from ...services.operator_status import get_operator_status

router = APIRouter(prefix="/api/v1/admin-ops", tags=["admin_ops"])


@router.get("/status", response_model=Dict[str, Any])
async def get_admin_ops_status():
    return get_operator_status()
```

Register in main.py:

```python
from .api.routes.admin_ops import router as admin_ops_router
```

```python
app.include_router(admin_ops_router)
```

## Frontend helper: `lwa-web/lib/admin-ops-api.ts`

```ts
export type AdminOpsStatus = {
  success: boolean;
  mode: string;
  provider_status: Record<string, unknown>;
  mock_live_flags: Record<string, unknown>;
  health: Record<string, unknown>;
  warnings: string[];
};

export async function getAdminOpsStatus() {
  const response = await fetch("/api/v1/admin-ops/status");
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};
  if (!response.ok) throw new Error(data?.detail || "Admin ops status failed");
  return data as AdminOpsStatus;
}
```

## Frontend panel: `lwa-web/components/command-center/AdminOpsPanel.tsx`

```tsx
"use client";

import { useEffect, useState } from "react";
import { AdminOpsStatus, getAdminOpsStatus } from "../../lib/admin-ops-api";

export function AdminOpsPanel() {
  const [status, setStatus] = useState<AdminOpsStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAdminOpsStatus().then(setStatus).catch((err) => setError(err instanceof Error ? err.message : "Failed to load admin ops."));
  }, []);

  if (error) return <div className="rounded-2xl border border-red-300/25 bg-red-300/10 p-4 text-red-100">{error}</div>;
  if (!status) return <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-white/60">Loading operator status...</div>;

  return (
    <div className="space-y-6">
      <section className="glass-panel rounded-[28px] p-6">
        <p className="section-kicker">Admin / Ops</p>
        <h3 className="mt-3 text-2xl font-semibold text-ink">Operator observability</h3>
        <p className="mt-2 text-sm leading-7 text-ink/62">Safe metadata-only visibility into provider flags, launch health, and warnings.</p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <StatusCard title="Mode" value={status.mode} />
        <StatusCard title="Backend" value={String(status.health.backend || "unknown")} />
        <StatusCard title="Paid providers" value={String(status.provider_status.paid_providers_enabled)} />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <JsonPanel title="Provider status" value={status.provider_status} />
        <JsonPanel title="Mock/live flags" value={status.mock_live_flags} />
      </section>

      <section className="glass-panel rounded-[28px] p-6">
        <p className="section-kicker">Warnings</p>
        <ul className="mt-4 space-y-2 text-sm leading-6 text-ink/70">
          {status.warnings.map((warning) => <li key={warning}>• {warning}</li>)}
        </ul>
      </section>
    </div>
  );
}

function StatusCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="metric-tile rounded-[24px] p-5">
      <p className="text-sm text-ink/46">{title}</p>
      <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
    </div>
  );
}

function JsonPanel({ title, value }: { title: string; value: Record<string, unknown> }) {
  return (
    <div className="glass-panel rounded-[24px] p-5">
      <p className="section-kicker">{title}</p>
      <pre className="mt-4 overflow-auto rounded-2xl bg-black/80 p-4 text-xs leading-6 text-white/80">{JSON.stringify(value, null, 2)}</pre>
    </div>
  );
}
```

Wire into `CommandCenter.tsx`:

```tsx
import { AdminOpsPanel } from "../command-center/AdminOpsPanel";
```

Add tab:

```tsx
{ id: "adminops", label: "Admin/Ops", icon: "🛰️" }
```

Add switch case:

```tsx
case "adminops":
  return <AdminOpsPanel />;
```

## Validation

```bash
python3 -m compileall lwa-backend/app
cd lwa-web
npm run type-check || npm run typecheck || true
npm run build
cd ..
git diff --check
git status --short
```

## Commit

```bash
git add lwa-backend/app/services/operator_status.py lwa-backend/app/api/routes/admin_ops.py lwa-backend/app/main.py lwa-web/lib/admin-ops-api.ts lwa-web/components/command-center/AdminOpsPanel.tsx lwa-web/components/worlds/CommandCenter.tsx
git commit -m "feat: add operator observability panel"
git push origin main
```

---

# Safety checks before every commit

```bash
git status --short | grep -Ei "\.env|secret|token|key|credential|pem|p12|mobileprovision|provisionprofile" || true
git status --short | grep -Ei "\.pkl|\.joblib|\.onnx|\.pt|\.pth|\.blend|\.glb|\.gltf|\.mp4|\.mov|\.zip|\.psd|\.wav|\.aiff|\.obj|\.fbx" || true
git status --short | grep "lwa-ios" || true
```

If any line appears in these safety checks, stop and inspect before committing.

---

# Final execution command

```text
Complete Slice 3.
Commit it.
Then Slice 4.
Commit it.
Then Slice 5.
Commit it.
Then continue in exact order.
```

Do **not** jump to Whop, upload, admin, or campaign mode before finishing Slices 3–5. The customer-facing clip result UI needs to become honest and premium first.
