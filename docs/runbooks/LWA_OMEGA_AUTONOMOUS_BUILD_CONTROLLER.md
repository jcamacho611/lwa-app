# LWA Omega Autonomous Build Controller

## Mission

The LWA Omega autonomous build controller enables Windsurf to systematically build the complete LWA ecosystem following the master build prompt while maintaining self-awareness through periodic audits.

## LWA Omega Vision Summary

LWA (Lee-Wuh AI) is the AI creator operating system that transforms any source into monetizable content and campaigns. The system includes:

- **Lee-Wuh**: AI mascot, council leader, onboarding guide, game character, future VR avatar
- **Council**: Functional decision layer with defined member roles and responsibilities
- **Core Engines**: Video OS, Creative Engines, Character System, Game World, Marketplace
- **Frontend**: Premium black/gold/purple/white palette with Lee-Wuh presence
- **Deployment**: Railway-ready with safe environment gating

## Lee-Wuh Role Summary

Lee-Wuh serves as:
- **AI Mascot**: Face of LWA with council guidance
- **Brain Controller**: Processes app state and outputs recommendations
- **Council Leader**: Coordinates functional council members
- **Onboarding Guide**: Helps users navigate the system
- **Game Character**: Progression through realms and quests
- **Future VR Avatar**: Immersive command center presence

## Autonomous Build Process

### Core Operating Rhythm

```
inspect → build → audit → validate → commit/PR → continue
```

### Periodic Self-Audit Loop

The agent must run a self-audit at these points:

1. **Before starting** any new feature/system
2. **After every 3–5 files changed**
3. **After every major backend service** is created
4. **After every major frontend component** is created
5. **Before every commit**
6. **After every validation failure**
7. **After every PR is created**
8. **Anytime the branch changes**
9. **Anytime overlapping work** or duplicate systems are noticed
10. **Before moving to the next engine/gate**

## Audit Commands

Run these commands during each audit:

```bash
cd /Users/bdm/LWA/lwa-app

echo "=== LWA OMEGA SELF AUDIT ==="
date
git branch --show-current
git status --short
git diff --stat
gh pr list --state open --limit 30
gh issue list --state open --limit 80

echo "=== CHANGED FILE AREAS ==="
git status --short | awk '{print $2}' | cut -d/ -f1-3 | sort | uniq

echo "=== POSSIBLE SECRETS / ENV RISK ==="
git status --short | grep -Ei "\.env|secret|token|key|credential|pem|p12|mobileprovision|provisionprofile" || true

echo "=== POSSIBLE HEAVY ASSET RISK ==="
git status --short | grep -Ei "\.blend|\.glb|\.gltf|\.mp4|\.mov|\.zip|\.psd|\.wav|\.aiff|\.obj|\.fbx" || true

echo "=== IOS TOUCH CHECK ==="
git status --short | grep "lwa-ios" || true

echo "=== FRONTEND TOUCH CHECK ==="
git status --short | grep "lwa-web" || true

echo "=== BACKEND TOUCH CHECK ==="
git status --short | grep "lwa-backend" || true
```

## Self-Audit Questions

After running commands, answer these internally and act accordingly:

1. **What am I building right now?**
2. **Which issue/gate/phase does it map to?**
3. **Does this connect to one of:**
   - Video OS
   - Lee-Wuh Brain/Council
   - Command Center frontend
   - Marketplace
   - Game/World system
   - Blender/Rive/Spline/XR pipeline
   - Railway readiness
   - Docs/runbooks
4. **Did I accidentally start a random disconnected system?**
5. **Did I touch iOS?** If yes, was it explicitly required?
6. **Did I touch backend contracts?** If yes, is it additive/backward compatible?
7. **Did I create or modify secrets/env files?**
8. **Did I create heavy assets that should not be committed?**
9. **Did I create empty placeholder images incorrectly?**
10. **Are there open PRs that already cover this work?**
11. **Am I duplicating an existing branch or feature?**
12. **Do current changes still preserve /generate?**
13. **Do current changes support the LWA Omega vision?**
14. **Should I keep coding, validate now, commit, create PR, merge/update an existing PR, or stop?**

## Decision Matrix

### CONTINUE BUILDING if:
- Changes are additive
- No secrets or heavy raw assets
- No iOS touched unless required
- Current work maps to LWA Omega vision
- Fewer than 3–5 files changed since last validation
- No obvious overlap/conflict

### VALIDATE NOW if:
- 3–5 files changed
- Backend service added
- Frontend component added
- Route added
- Integration point changed
- Imports changed
- Before commit
- Before PR

### COMMIT if:
- Validation passes
- Feature slice is coherent
- Changes are not too large to review
- No secret/heavy asset risk
- Git diff check passes

### CREATE OR UPDATE PR if:
- Commit exists on feature branch
- Validation passes
- Work is coherent
- PR body file is used
- Branch is pushed
- No overlapping PR should be used instead

### CONSOLIDATE if:
- Multiple branches touch same feature
- Local main has same work as branch
- PRs overlap
- Duplicate components/services exist
- Same engine is implemented in two places

### PAUSE / STOP if:
- Validation fails and cannot be fixed safely
- Secret risk appears
- Destructive deletion seems needed
- iOS was touched accidentally
- Live provider/payment/API decision is needed
- Merge conflict is dangerous
- Missing asset cannot be found
- Agent cannot identify what issue/phase current work belongs to

## Validation Rules

When audit says validate, run:

```bash
python3 -m compileall lwa-backend/app

cd lwa-web
npm run type-check
npm run build

cd ..
git diff --check
git status --short
```

For docs-only changes:
```bash
git diff --check
git status --short
```

## Audit Report Format

Whenever stopping or creating PR, report:

```
LWA OMEGA SELF-AUDIT RESULT

1. Current branch:
2. Current phase/issue:
3. What was built:
4. Files changed:
5. Frontend touched:
6. Backend touched:
7. iOS touched:
8. Secrets/env risk:
9. Heavy asset risk:
10. Validation:
11. Open PRs affected:
12. Decision:
13. Next action:
```

## Process Memory Rule

At the top of every new major prompt, remind yourself:

"I must inspect, build, audit, validate, then continue. I only stop for failure, danger, or a true owner decision."

## Build Queue Order

### Phase 1: Foundation (High Priority)
1. **Lee-Wuh Council Profiles** - Complete documentation
2. **Lee-Wuh AI Brain / Council Controller** - Backend service and API
3. **Video OS Engines** - Timeline, FFmpeg, Caption, Audio, Safety
4. **Campaign Export Packager** - Multi-platform distribution
5. **Feedback Learning Loop** - Performance analysis and improvement
6. **Railway Deployment Readiness** - Environment configuration

### Phase 2: Experience (Medium Priority)
7. **Blender/Rive/Spline Pipeline Docs** - 3D asset workflows
8. **VR/AR/XR Docs Scaffold** - Immersive experience planning
9. **Marketplace v0** - Metadata-only marketplace
10. **Character System v0** - Lee-Wuh and future characters
11. **Game World System v0** - Creator progression and quests
12. **Remaining Creative Engines** - Thumbnail, B-roll, Hook, Trend, Audience, Offer

### Phase 3: Interface (High Priority)
13. **Frontend Command Center** - Main user interface
14. **Omega Controller Documentation** - This document

## Safety Rules

### Never Commit:
- Secrets or .env files
- Large raw media or model files
- Heavy 3D assets (.blend, .glb, etc.)
- iOS code unless explicitly required
- Destructive deletions of existing systems

### Always Preserve:
- /generate endpoint
- Existing backend contracts
- iOS untouched unless required
- Additive work only

### Validation Requirements:
- Backend must compile: `python3 -m compileall lwa-backend/app`
- Frontend must build: `npm run build`
- Git diff must pass: `git diff --check`
- No whitespace or conflict errors

## Stop Conditions

Stop immediately if:
- Validation fails and cannot be fixed safely
- Secret risk appears in git status
- Heavy assets are about to be committed
- iOS was touched accidentally
- Live provider/payment decision needed
- Merge conflict is dangerous
- Cannot identify current work's purpose
- User explicitly requests to stop

## Success Criteria

The autonomous build succeeds when:
- All Phase 1-3 items are completed
- All validation passes
- No secrets or heavy assets committed
- iOS remains untouched
- /generate endpoint preserved
- Backend contracts maintained
- Frontend builds successfully
- Documentation is complete

## Next Steps

After completing the autonomous build:
1. Run final comprehensive audit
2. Create summary PR with all changes
3. Validate entire system
4. Document any remaining issues
5. Provide handoff report

## Emergency Procedures

If audit reveals critical issues:
1. Stop immediately
2. Run full validation
3. Identify root cause
4. Create issue with details
5. Request user guidance
6. Do not proceed until resolved

---

**This controller ensures the LWA Omega vision is built systematically, safely, and with full self-awareness.**
