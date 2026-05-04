# Windsurf Maintenance Prompt for LWA

## Purpose

This prompt ensures Windsurf maintains the LWA codebase correctly without breaking existing functionality. Use this prompt whenever you need Windsurf to make changes to the codebase.

---

## Universal Rules (Never Violate)

### 1. Health Check Must Pass

**Before ANY commit:**
```bash
bash scripts/health-check.sh
```

**Expected Output:**
```
✅ ALL CHECKS PASSED
🎉 Repo is healthy and ready for commit!
```

**If any check fails:**
- STOP
- Fix the issue
- Re-run health-check.sh
- Only then commit

### 2. Never Break Offline-First Guarantee

**LWA must ALWAYS return usable output without external AI.**

**Required Test:**
```bash
cd lwa-backend && python3 test_offline.py
```

**Must Output:**
```
✅ OFFLINE FALLBACK TEST: PASSED
✅ LWA works 100% offline without API keys!
```

**If this fails:**
- STOP immediately
- Fix the analysis_engine.py
- Re-run test_offline.py
- Only then proceed

### 3. Do Not Remove Existing AI Packages

**Current backend has:**
- anthropic
- openai

**Rule:** Keep them but make them **optional enhancement only**.

**Correct:**
```python
# Try AI first (optional)
try:
    if OPENAI_API_KEY:
        return ai_generate()
except:
    pass

# Always have fallback
return analysis_engine.generate()  # Guaranteed to work
```

**Wrong:**
```python
# Never do this
return openai.generate()  # Will fail without API key
```

### 4. Do Not Touch iOS Unless Explicitly Required

**Directory:** `lwa-ios/`

**Rule:** If not explicitly asked to modify iOS, **leave it alone**.

**Exception:** If iOS build breaks due to shared dependencies, coordinate with mobile engineer.

### 5. No New External AI Dependencies

**Forbidden:**
- New AI SDKs (Google AI, Cohere, etc.)
- New paid cloud services
- New API dependencies

**Allowed:**
- Local libraries
- Open source tools
- Built-in Next.js/React features
- Local analysis algorithms

### 6. Lint Rules

**Current ESLint Config:**
- react-hooks/rules-of-hooks: error
- react-hooks/exhaustive-deps: warn
- no-unused-vars: warn (with _ ignore)

**Fix Strategy:**
1. Add real missing dependencies (preferred)
2. Use useCallback/useMemo if dependencies cause loops
3. Only use eslint-disable with comment explaining why

**Never:**
- Disable ESLint globally
- Ignore all warnings without fixing
- Add @typescript-eslint rules without installing plugin

### 7. TypeScript Strictness

**Current tsconfig.json:**
```json
{
  "compilerOptions": {
    "strict": true,
    "noEmit": true,
    "isolatedModules": true
  }
}
```

**Fix Strategy:**
1. Add proper types (preferred)
2. Use type guards
3. Use optional chaining (?.)
4. Only use `any` as last resort with explanation comment

---

## Phase-Based Execution

### Phase 1: Inspection (Always Do First)

**Run these commands:**
```bash
# 1. Git status
cd /Users/bdm/LWA/lwa-app && git status --short

# 2. Current branch
git branch --show-current

# 3. Package files
ls lwa-web/package.json lwa-backend/requirements.txt

# 4. Config files
ls lwa-web/.eslintrc.json lwa-web/tsconfig.json

# 5. Backend entry
ls lwa-backend/app/main.py

# 6. Generate route
ls lwa-backend/app/api/routes/generate.py

# 7. Test files
ls lwa-backend/test_offline.py scripts/health-check.sh
```

**Report:**
- What files exist
- Current git state
- Any missing infrastructure

### Phase 2: Verification

**Run verification:**
```bash
cd lwa-web && npm install  # if needed
cd lwa-web && npm run lint
cd lwa-web && npm run type-check
cd lwa-web && npm run build

cd lwa-backend && python3 -m compileall .
cd lwa-backend && python3 -c "
import importlib.util
for name in ['fastapi', 'pydantic', 'httpx']:
    assert importlib.util.find_spec(name), f'missing {name}'
print('backend core imports ok')
"
```

**Report:**
- Every error with file path and line number
- Specific error messages
- Suggested fixes

### Phase 3: Fix (Only After Phase 2)

**Fix Strategy:**
1. Fix TypeScript errors first
2. Fix ESLint warnings second
3. Fix build errors third
4. Fix backend issues fourth

**Small Commits:**
- One fix per commit
- Clear commit messages
- Re-run health-check.sh after each fix

### Phase 4: Final Verification

**Required:**
```bash
bash scripts/health-check.sh
cd lwa-backend && python3 test_offline.py
```

**Both must pass.**

### Phase 5: Report

**Document:**
1. Files changed
2. Dependencies added/removed
3. Lint errors fixed
4. Type errors fixed
5. Build result
6. Backend offline fallback result
7. Any remaining warnings
8. Recommended commit message

### Phase 6: Commit (Only If All Pass)

**Commit Message Format:**
```
type(scope): description

- Change 1
- Change 2
- Change 3

Closes #issue-number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

**Scopes:**
- `web`: Frontend
- `api`: Backend API
- `engine`: Analysis/Deterministic engine
- `ios`: iOS app
- `repo`: General repo

---

## Common Tasks & Solutions

### Task: Add New Page

**Example: Add /analytics page**

```bash
# 1. Create directory
mkdir lwa-web/app/analytics

# 2. Create page
cat > lwa-web/app/analytics/page.tsx << 'EOF'
import { LwaShell } from "../../components/worlds/LwaShell";

export default function AnalyticsPage() {
  return (
    <LwaShell title="Analytics">
      <div>Analytics content here</div>
    </LwaShell>
  );
}
EOF

# 3. Add to navigation
# Edit lwa-web/components/navigation/MainNav.tsx
# Add: { href: "/analytics", label: "Analytics", icon: BarChart3 },

# 4. Test
cd lwa-web && npm run type-check
cd lwa-web && npm run build
bash scripts/health-check.sh
```

### Task: Add API Route

**Example: Add /api/v1/analytics**

```python
# 1. Create route file
# lwa-backend/app/api/routes/analytics.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()

class AnalyticsResponse(BaseModel):
    total_clips: int
    total_views: int

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    # Always have fallback
    return AnalyticsResponse(total_clips=0, total_views=0)

# 2. Register in main.py
# app.include_router(analytics.router, prefix="/api/v1")

# 3. Add frontend types
# lwa-web/lib/api.ts
export type AnalyticsResponse = {
  total_clips: number;
  total_views: number;
};

export async function loadAnalytics() {
  return jsonRequest<AnalyticsResponse>("/api/v1/analytics");
}

# 4. Test
cd lwa-backend && python3 -m py_compile app/api/routes/analytics.py
cd lwa-web && npm run type-check
bash scripts/health-check.sh
```

### Task: Fix Hook Dependency Warning

**Example Warning:**
```
React Hook useEffect has a missing dependency: 'activeResult'
```

**Solution Options:**

**Option 1: Add dependency (if safe)**
```typescript
// Before
useEffect(() => {
  doSomething(activeResult);
}, []); // Missing dependency

// After
useEffect(() => {
  doSomething(activeResult);
}, [activeResult]); // Added dependency
```

**Option 2: Use useCallback (if causes loop)**
```typescript
// Before
useEffect(() => {
  handleClip(activeResult);
}, [handleClip, activeResult]);

// After
const handleClip = useCallback((result) => {
  // ...
}, []); // Memoized

useEffect(() => {
  handleClip(activeResult);
}, [handleClip, activeResult]); // Now safe
```

**Option 3: eslint-disable (last resort)**
```typescript
useEffect(() => {
  doSomething(activeResult);
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, []); // Intentionally run once on mount
```

### Task: Migrate <img> to next/image

**Before:**
```tsx
<img src="/logo.png" alt="Logo" width={100} height={50} />
```

**After:**
```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={100} height={50} />
```

**For remote images:**
```typescript
// next.config.js
module.exports = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'example.com' }
    ]
  }
}
```

```tsx
<Image 
  src="https://example.com/image.jpg" 
  alt="Description"
  width={800}
  height={600}
/>
```

### Task: Fix "Object is possibly undefined"

**Error:**
```
'object' is possibly 'undefined'.ts(2532)
```

**Solution:**
```typescript
// Before
{array.map(item => ...)}

// After (Option 1: Optional chaining)
{array?.map(item => ...)}

// After (Option 2: Type guard)
if (array && array.length > 0) {
  array.map(item => ...)
}

// After (Option 3: Default value)
{(array || []).map(item => ...)}
```

---

## Emergency Stop Commands

**If Windsurf starts doing dangerous things, paste this:**

```text
STOP.

Do not rewrite the entire app.
Do not touch lwa-ios/.
Do not remove existing API providers.
Do not add external AI dependencies.
Do not disable lint globally.

Return to the maintenance plan:
1. Run bash scripts/health-check.sh
2. Report current status
3. Fix issues one at a time
4. Re-run health-check.sh
5. Only then commit
```

---

## File Structure Reference

### Frontend (lwa-web/)

```
lwa-web/
├── app/                          # Next.js App Router
│   ├── page.tsx                  # Homepage
│   ├── layout.tsx                # Root layout
│   ├── generate/page.tsx          # Clip generation
│   ├── dashboard/page.tsx         # Dashboard
│   ├── realm/page.tsx            # Game/World
│   ├── marketplace/page.tsx     # Marketplace
│   ├── campaigns/page.tsx        # Campaigns
│   ├── history/page.tsx         # History
│   ├── wallet/page.tsx          # Wallet
│   ├── upload/page.tsx          # Upload
│   └── ... (23 more pages)
├── components/
│   ├── clip-studio.tsx          # Main clip UI (3,300 lines)
│   ├── clip-results/            # Clip display components
│   │   ├── HeroClip.tsx
│   │   ├── PostingSchedule.tsx
│   │   └── index.ts
│   ├── navigation/              # Navigation
│   │   ├── MainNav.tsx
│   │   └── index.ts
│   └── worlds/                  # World/Game components
├── lib/
│   ├── api.ts                   # API layer
│   ├── demo-data.ts            # Demo mode data
│   ├── error-translation.ts    # Error handling
│   └── version-states.ts       # Version definitions
├── package.json
├── tsconfig.json
└── .eslintrc.json
```

### Backend (lwa-backend/)

```
lwa-backend/
├── app/
│   ├── main.py                  # FastAPI app setup
│   ├── api/
│   │   └── routes/
│   │       ├── generate.py      # Clip generation API
│   │       └── ...              # Other routes
│   └── services/
│       ├── analysis_engine.py   # Offline engine (NEW)
│       ├── deterministic_clip_engine.py  # Deterministic engine
│       └── ...                  # Other services
├── scripts/
│   └── test_analysis_engine.py  # Local test script
├── test_offline.py             # Offline smoke test
├── requirements.txt
└── Dockerfile (if exists)
```

### Root (lwa-app/)

```
lwa-app/
├── lwa-web/                    # Frontend
├── lwa-backend/                # Backend
├── lwa-ios/                    # iOS (do not touch)
├── scripts/
│   └── health-check.sh        # Comprehensive health check
├── ENGINEERING_TEAM.md         # Team structure
├── WINDSURF_MAINTENANCE_PROMPT.md  # This file
└── .git/
```

---

## Quick Command Reference

### Health Check (Most Important)
```bash
bash scripts/health-check.sh
```

### Frontend Only
```bash
cd lwa-web
npm install
npm run lint
npm run type-check
npm run build
npm run check  # Does all three above
```

### Backend Only
```bash
cd lwa-backend
python3 -m compileall .
python3 test_offline.py
python3 scripts/test_analysis_engine.py
```

### Full Verification
```bash
cd /Users/bdm/LWA/lwa-app
bash scripts/health-check.sh && cd lwa-backend && python3 test_offline.py
```

### Git Operations
```bash
git status --short
git add <files>
git commit -m "type(scope): description"
git push origin main
```

---

## Success Criteria

**Before any task is considered complete:**

✅ **Must Pass:**
1. `bash scripts/health-check.sh` → "ALL CHECKS PASSED"
2. `cd lwa-backend && python3 test_offline.py` → "PASSED"
3. No TypeScript errors
4. No critical ESLint errors
5. Build succeeds
6. Python compiles without errors

✅ **Must Document:**
1. Files changed
2. Any new dependencies
3. Any new environment variables
4. Any breaking changes
5. Migration steps (if any)

✅ **Must Commit:**
1. Clear commit message
2. All changes in logical commit
3. No work-in-progress commits to main

---

## Contact Information

**If this prompt doesn't work:**

1. Check health-check.sh output
2. Check test_offline.py output
3. Review ENGINEERING_TEAM.md
4. Escalate to technical lead

**Emergency:**
- If health-check.sh consistently fails → Senior Frontend Engineer
- If test_offline.py consistently fails → Senior Backend Engineer
- If both fail → Engineering Lead + Full Team

---

## Version History

- **v1.0** (May 4, 2024): Initial comprehensive maintenance prompt

---

*This document is a living document. Update it as the system evolves.*
