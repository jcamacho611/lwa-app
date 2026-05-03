# LWA Director Brain ML Repo Build Spec

## Purpose

This document turns the Director Brain machine-learning idea into a safe, repo-aligned implementation plan for LWA.

The goal is not to drop random ML files into the repo. The goal is to add a learning layer that scores hooks, captions, clips, opportunities, and outcomes so Lee-Wuh can guide users with improving intelligence.

The earlier example used paths like:

```text
/backend/ml/engine.py
/backend/api/ml.py
```

The real LWA backend should be inspected first and, if the current structure is still `lwa-backend/app/`, implemented as:

```text
lwa-backend/app/services/director_brain_ml.py
lwa-backend/app/api/routes/director_brain_ml.py
```

This system should connect to:

- Lee-Wuh Brain
- Proof Vault + Style Memory
- Feedback Learning Loop
- Generate results
- Campaign Export
- Command Center

---

## Definition of Good Content

LWA should define good content as all of the following combined:

```text
Good content = engagement potential + conversion potential + viral hook strength + user preference + proof/history outcome.
```

Default weights:

```text
viral_hook_strength: 0.25
retention_engagement: 0.25
conversion_offer_fit: 0.20
user_style_preference: 0.20
proof_history_signal: 0.10
```

Human-readable definition:

```text
A clip is good if it makes someone stop, watch, understand, trust, act, save, share, buy, or follow.
```

---

## Implementation Philosophy

Do not start with fragile ML dependencies unless the repo already supports them.

Start with:

```text
Explainable heuristic scoring v0
→ stored learning events
→ Proof Vault / Style Memory signals
→ optional sklearn adapter later
→ embeddings/vector search later
→ deep personalization later
```

Why this path is safest:

- works immediately
- explainable to users
- no binary model files
- no deployment risk
- no paid provider calls
- easy to connect to feedback
- can be upgraded later

---

## Safety Rules

Do not:

```text
commit model.pkl
commit vectorizer.pkl
commit .joblib
commit .onnx
commit .pt or .pth
commit secrets
commit .env
add live paid providers
break /generate
touch lwa-ios
```

Do:

```text
keep v0 deterministic
keep outputs explainable
use metadata-only learning events
return stable JSON
validate inputs
register FastAPI routes safely
add frontend helpers
add Command Center panel
```

---

## Backend Files

Create:

```text
lwa-backend/app/services/director_brain_ml.py
lwa-backend/app/api/routes/director_brain_ml.py
```

Register in:

```text
lwa-backend/app/main.py
```

---

## Backend Service Requirements

The service should expose:

```text
score_text(request)
rank_candidates(request)
learn_event(request)
get_status()
```

Supported content types:

```text
hook
caption
title
offer
description
clip_summary
opportunity
campaign_angle
```

Supported goals:

```text
engagement
conversion
viral
personal
balanced
```

Score output should include:

```text
score
component_scores
reasons
lee_wuh_recommendation
suggested_improvement
confidence
mode
```

Learning events should be metadata-only for v0:

```text
id
text
label: winning | rejected | neutral
signal_type: save | share | click | export | purchase | manual_feedback
weight
metadata
created_at
```

---

## Backend Route Requirements

Create route group:

```text
/api/v1/director-brain
```

Routes:

```text
POST /api/v1/director-brain/score
POST /api/v1/director-brain/rank
POST /api/v1/director-brain/learn
GET  /api/v1/director-brain/status
```

---

## Frontend Requirements

Add helpers in the existing API helper location, likely:

```text
lwa-web/lib/api.ts
```

or, if cleaner:

```text
lwa-web/lib/director-brain-api.ts
```

Add panel:

```text
lwa-web/components/command-center/DirectorBrainPanel.tsx
```

Wire the panel into Command Center navigation.

Frontend helpers:

```text
scoreDirectorBrainText
rankDirectorBrainCandidates
submitDirectorBrainLearningEvent
getDirectorBrainStatus
```

The Director Brain panel should include:

- text input for hook/caption/title
- content type selector
- platform selector
- goal selector
- Score button
- displayed overall score
- component scores
- reasons
- Lee-Wuh recommendation
- suggested improvement
- rank candidate hooks section
- learning status section

---

## Integration Requirements

### Proof Vault + Style Memory

If those systems exist:

- use approved hook patterns
- use rejected hook patterns
- use winning clip patterns
- use brand voice notes
- use audience notes

If they do not exist yet:

- keep optional fields
- return safe default scoring

### Feedback Learning Loop

Learning events should be compatible with feedback signals:

```text
save
reject
export
share
purchase
manual_feedback
```

### Generate Flow

If easy and safe, add an optional Director Brain score badge to hook/clip cards.

Do not break `/generate`.

Do not change the existing generate API contract unless backward compatible.

---

## Example API Shapes

### Score Request

```json
{
  "text": "Nobody is doing this yet",
  "content_type": "hook",
  "platform": "tiktok",
  "goal": "balanced",
  "style_memory": {
    "approved_hook_patterns": ["nobody is talking about", "watch this before"],
    "rejected_hook_patterns": ["you won't believe"]
  },
  "proof_signals": {
    "winning_keywords": ["early", "money", "system"],
    "rejected_keywords": ["generic", "boring"]
  }
}
```

### Score Response

```json
{
  "success": true,
  "text": "Nobody is doing this yet",
  "score": 0.87,
  "component_scores": {
    "viral_hook_strength": 0.92,
    "retention_engagement": 0.84,
    "conversion_offer_fit": 0.76,
    "user_style_preference": 0.88,
    "proof_history_signal": 0.81
  },
  "reasons": [
    "Strong curiosity gap",
    "Short enough for a hook",
    "Matches approved style memory"
  ],
  "lee_wuh_recommendation": "Boss-level hook. Use this first, then pair it with a direct caption.",
  "suggested_improvement": "Add a clearer outcome or money angle if this is for conversion.",
  "mode": "heuristic_v0"
}
```

---

## Validation

If backend touched:

```bash
python3 -m compileall lwa-backend/app
```

If frontend touched:

```bash
cd lwa-web
npm run type-check
npm run build
cd ..
```

Always:

```bash
git diff --check
git status --short
```

Safety checks:

```bash
git status --short | grep -Ei "\.env|secret|token|key|credential|pem|p12|mobileprovision|provisionprofile" || true
git status --short | grep -Ei "\.pkl|\.joblib|\.onnx|\.pt|\.pth|\.blend|\.glb|\.gltf|\.mp4|\.mov|\.zip|\.psd|\.wav|\.aiff|\.obj|\.fbx" || true
git status --short | grep "lwa-ios" || true
```

---

## Commit Message For Implementation

```text
feat(ml): add Director Brain scoring and learning v0
```

---

## Windsurf Prompt

```text
Build the LWA Director Brain ML Foundation v0 safely.

Do not copy the provided `/backend/ml/engine.py` example blindly. The real backend appears to live under `lwa-backend/app/`.

First inspect backend structure:
cd /Users/bdm/LWA/lwa-app
find . -maxdepth 4 -type d | grep -E "lwa-backend|backend|app"
find lwa-backend/app -maxdepth 4 -type f | sort | head -300
grep -R "include_router" -n lwa-backend/app/main.py lwa-backend/app || true
cat lwa-backend/requirements.txt || true
cat lwa-backend/pyproject.toml || true

Goal:
Add an explainable Director Brain ML v0 that scores hooks/captions/content ideas and learns from user outcomes.

Definition of good content:
Good content = engagement potential + conversion potential + viral hook strength + user preference + proof/history outcome.

Default weights:
- viral_hook_strength: 0.25
- retention_engagement: 0.25
- conversion_offer_fit: 0.20
- user_style_preference: 0.20
- proof_history_signal: 0.10

Backend:
Create:
- `lwa-backend/app/services/director_brain_ml.py`
- `lwa-backend/app/api/routes/director_brain_ml.py`

Routes:
- POST `/api/v1/director-brain/score`
- POST `/api/v1/director-brain/rank`
- POST `/api/v1/director-brain/learn`
- GET `/api/v1/director-brain/status`

Register router in `lwa-backend/app/main.py`.

Implementation rules:
- no mandatory sklearn dependency for v0
- no pickle/model artifact commits
- no binary ML files
- deterministic heuristic scoring first
- metadata-only learning events
- explainable component scores
- stable JSON responses

Frontend:
Add API helpers in existing helper location:
- scoreDirectorBrainText
- rankDirectorBrainCandidates
- submitDirectorBrainLearningEvent
- getDirectorBrainStatus

Add Command Center panel:
- `lwa-web/components/command-center/DirectorBrainPanel.tsx`

Wire panel into Command Center navigation.

Panel should show:
- score input
- candidate ranking
- component scores
- reasons
- Lee-Wuh recommendation
- learning status

Integrate with Proof Vault + Style Memory if those systems exist, but keep optional if not.

Safety:
- Preserve `/generate`
- Do not touch `lwa-ios`
- Do not commit secrets
- Do not commit `.pkl`, `.joblib`, `.onnx`, `.pt`, `.pth`
- Do not enable live paid providers

Validation:
python3 -m compileall lwa-backend/app
cd lwa-web
npm run type-check
npm run build
cd ..
git diff --check

Safety checks:
git status --short | grep -Ei "\.env|secret|token|key|credential|pem|p12|mobileprovision|provisionprofile" || true
git status --short | grep -Ei "\.pkl|\.joblib|\.onnx|\.pt|\.pth|\.blend|\.glb|\.gltf|\.mp4|\.mov|\.zip|\.psd|\.wav|\.aiff|\.obj|\.fbx" || true
git status --short | grep "lwa-ios" || true

Commit:
feat(ml): add Director Brain scoring and learning v0

Continue after commit by wiring Director Brain scoring into Lee-Wuh, Proof Vault, Style Memory, Campaign Export, and Generate cards where safe.
```

---

## Acceptance Criteria

Complete only when:

- backend Director Brain service exists
- backend Director Brain route exists
- router registered in main app
- scoring endpoint returns explainable scores
- ranking endpoint ranks candidates
- learn endpoint stores metadata event
- status endpoint reports mode/events
- frontend helpers exist
- Command Center panel exists and is reachable
- validation passes
- no iOS touched
- no secrets or binary model files committed
