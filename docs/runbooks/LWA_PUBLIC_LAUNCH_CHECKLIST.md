# LWA Public Launch Checklist

**Target:** Public launch of LWA AI Clip Engine  
**Status:** Pre-launch verification  
**Last updated:** 2024-05-04

---

## ✅ Pre-Launch Verification

### Core Product Flow

| Check | Status | Notes |
|-------|--------|-------|
| Clip generation works end-to-end | ⏳ | Test with YouTube URL |
| Rendered-first results display | ✅ | Lead clip + lanes implemented |
| Strategy-only clips handled | ✅ | Messaging and recovery path in place |
| Campaign Export works | ✅ | Wired to real API |
| Demo Mode functional | ✅ | Onboarding flow complete |

### Lee-Wuh Character

| Check | Status | Notes |
|-------|--------|-------|
| Character visible on homepage | ✅ | LeeWuhCharacterStage integrated |
| Character visible on generate | ✅ | Dynamic mood states |
| Character visible in Command Center | ✅ | Overview panel |
| Floating assistant works | ✅ | Toggle + chat UI |
| **3D GLB runtime asset** | ⏳ | **PENDING** - Run Blender locally |
| Fallback chain works | ✅ | Poster → SVG → emoji |

### Backend & API

| Check | Status | Notes |
|-------|--------|-------|
| All routes registered | ✅ | main.py verified |
| Event tracking live | ✅ | emit_event functional |
| Entitlement system live | ✅ | Credits/unlocks working |
| Director Brain endpoints | ✅ | Score/rank/learn/status |
| Admin/Ops observability | ✅ | Recent events, metrics, status |
| Database migrations | ⏳ | Verify on Railway |
| Environment variables | ⏳ | Verify all set |

### Frontend

| Check | Status | Notes |
|-------|--------|-------|
| TypeScript clean | ✅ | npm run type-check passes |
| Build clean | ✅ | npm run build passes |
| No console errors | ⏳ | Manual verification |
| Responsive on mobile | ⏳ | Manual verification |
| Dark mode consistent | ✅ | Design system in place |

### Security & Safety

| Check | Status | Notes |
|-------|--------|-------|
| No secrets in repo | ✅ | .env in .gitignore |
| No raw heavy assets | ✅ | .blend/.fbx excluded |
| API keys in env | ⏳ | Verify Railway |
| Privacy-safe tracking | ✅ | IP hashing implemented |
| User data handling | ⏳ | Review data retention |

### Deployment

| Check | Status | Notes |
|-------|--------|-------|
| Railway project configured | ⏳ | Verify dashboard |
| Frontend builds on Railway | ⏳ | Verify build command |
| Backend starts without errors | ⏳ | Verify startup logs |
| Health check endpoint works | ✅ | /api/v1/admin/status |
| Custom domain (if applicable) | ⏳ | Configure if needed |

---

## 🔧 Manual Verification Steps

### Step 1: Backend Startup

```bash
cd lwa-backend
python -m compileall app
# Verify no syntax errors
```

Check Railway logs for:
- Database connection successful
- Redis connection (if using)
- All routers loaded
- No import errors

### Step 2: Frontend Build

```bash
cd lwa-web
npm ci
npm run build
# Verify exit code 0
```

### Step 3: End-to-End Clip Generation

1. Open app homepage
2. Select "Content Mission"
3. Paste YouTube URL (public, non-age-restricted)
4. Click "Generate Clip Pack"
5. Verify:
   - Loading state shows
   - Results appear within 2-5 minutes
   - Lead clip is visible
   - Rendered lane shows playable clips (if any)
   - Strategy lane shows ideas (if any)
   - Lee-Wuh character stage visible

### Step 4: Campaign Export

1. From clip results, click "Export Campaign"
2. Verify export modal opens
3. Check that rendered clips are listed
4. Verify strategy-only clips are honest (not fake rendered)
5. Copy export bundle
6. Verify JSON structure is valid

### Step 5: Demo Mode

1. Open app in incognito/private window
2. Verify demo source available
3. Generate demo clips
4. Verify sample outputs

### Step 6: Event Tracking

1. Perform actions (view clip, save, etc.)
2. Check Command Center Admin/Ops panel
3. Verify events appear in recent events list

---

## 🚨 Blockers (Must Resolve Before Launch)

| Blocker | Severity | Owner | Resolution |
|---------|----------|-------|------------|
| Lee-Wuh GLB generation | Medium | @jcamacho611 | Run Blender locally, commit if <5MB |
| Railway env vars | High | @jcamacho611 | Verify all required vars set |
| Database migrations | High | @jcamacho611 | Run migrations on prod DB |

---

## 📝 Post-Launch Monitoring

### Week 1

| Metric | Target | Check |
|--------|--------|-------|
| Clip generation success rate | >80% | Monitor via Admin panel |
| Average generation time | <5 min | Monitor via Admin panel |
| User signups | Baseline | Track via events |
| Error rate | <5% | Monitor logs |

### Week 2-4

- Review user feedback
- Monitor credits/unlock usage
- Check for edge cases in clip generation
- Optimize based on real usage patterns

---

## 🎯 Launch Decision

**Ready to launch when:**
- [ ] All blockers resolved
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] E2E clip generation tested
- [ ] Campaign export tested
- [ ] Demo mode tested
- [ ] Admin observability verified
- [ ] Railway env vars confirmed

**Launch command:**
```bash
# After all checks pass
git tag v0.1.0-launch
git push origin v0.1.0-launch
# Announce on social/Discord
```

---

## 📚 Related Documents

- [LWA_CURRENT_BUILD_STATUS.md](./LWA_CURRENT_BUILD_STATUS.md)
- [LWA_LIVE_SMOKE_TEST.md](./LWA_LIVE_SMOKE_TEST.md)
- [LEE_WUH_CHARACTER_PIPELINE.md](./LEE_WUH_CHARACTER_PIPELINE.md)
- [LWA_WHOP_ENTITLEMENT_VERIFICATION.md](./LWA_WHOP_ENTITLEMENT_VERIFICATION.md)

---

*Update this document as checks are completed.*
