# LWA Shared Context Appendix — 2026-05-03

## Purpose

This appendix captures the shared conversation context that was not already present in the repository master context. It should be read alongside:

```text
docs/architecture/LWA_CANVAS_CONNECTOR_MASTER_CONTEXT.md
```

This file is documentation/context only. It does not change runtime behavior.

---

## Current honest product state

### What LWA can do now

The current app is a real MVP, not just a mockup.

It can take a public video URL, let the user choose a target platform such as TikTok, Instagram, YouTube, or Facebook, optionally use a trend angle, send that job to the backend, and return a clip pack with:

- titles
- hooks
- captions
- timestamps
- scores
- asset links

When the backend is healthy, it can also generate real raw and edited clip assets, including vertical 9:16 exports. The iOS app can preview results, open clip assets, copy hooks/captions, share bundle text, and save past runs locally on the device.

Backend real-clip pipeline status from shared context:

- real-clip pipeline is already working
- iOS Debug build passed
- iOS Release build passed
- iOS Archive build passed

### What LWA cannot do yet

The app does not yet support the full product promise.

Current missing or incomplete capabilities:

- direct upload from phone
- direct upload from camera roll
- direct upload from Files
- direct Google Drive ingest
- reliable private/login-gated source ingest
- full timeline editor
- trim UI
- caption editor
- bulk batch review
- campaign manager
- direct posting to TikTok/Instagram/YouTube from inside the app
- full account platform
- team workspaces
- synced cloud history
- strong entitlement/paywall enforcement
- full Whop clipping workflow inside the app
- consistent OpusClip-level output of 20–40+ polished clips per source
- real short-form caption styling everywhere
- campaign automation

### Honest one-line summary

LWA is currently a working long-form-to-short-form clip generator and review console. It is not yet a full clipping business platform, full video editor, or full Whop campaign operating system.

### Highest-value next additions

Priority additions:

1. More clips per run.
2. Real burned-in short-form captions.
3. Better source ingest: uploads, Drive, device sources.
4. Batch workflow: approve, reject, regenerate, bulk export.
5. Campaign workflow: requirements, allowed platforms, submission tracking.
6. Real account, plan, and credit state so the product feels paid and complete.

---

## Frontend rebuild UI spec

### Rebuild principle

Do not rebuild the whole company from zero.

Rebuild the web experience layer so LWA feels like:

- a clipping-first machine
- a recommendation-first system
- a proof-first interface
- a mythic premium operating surface
- a tool that knows what deserves to be clipped, what should be posted first, what is already ready, what still needs work, and why the clip matters

The interface should stop feeling like:

- generic SaaS card stack
- dashboard that asks too many questions before doing work
- mixed-up pile of strategy cards and rendered media
- pretty shell without enough operator leverage

The new frontend must feel like:

- one input
- one strong generate action
- immediate recommendation
- clear rendered lane
- clear strategy lane
- clear packaging lane
- clear export lane
- mythic premium identity at the edges, not cluttering the center

---

## Core product behavior the frontend must express

### 1. Source first

The first thing the page should communicate:

```text
drop a source in and let LWA decide the best first move
```

Top panel should include:

- source URL input
- optional upload
- auto recommendation chip
- one strong generate button

Avoid:

- big interrogation form
- too many dropdowns
- forced platform choice first
- forced packaging choice first

### 2. Auto destination is default

The UI should show:

- recommended destination
- recommended content type
- recommended output style

These should appear as intelligent recommendations, not mandatory user decisions.

Manual override may exist, but it belongs in a smaller advanced control area.

### 3. Rendered proof comes first

The results page must visually prioritize:

- playable / previewable / rendered clips
- best clip first
- post order
- why it matters
- packaging assets

Strategy-only results must not look identical to playable results.

### 4. Strategy-only results stay useful but secondary

If something is strategy-only:

- label it clearly
- show why it is still valuable
- offer recovery / re-render if available
- do not pretend it is ready for export

### 5. The operator instantly knows what to do next

Every result should answer:

- Is this ready now?
- Is this the first post?
- Why should I post it?
- What hook should I test?
- What caption style fits it?
- What thumbnail text should I use?
- What CTA should I attach?

---

## New page structure

### A. Top shell

The shell should feel premium:

- dark black base
- restrained gold/neon accents
- mythic atmosphere at edges
- subtle motion
- side-world presence if retained
- no center-screen visual noise

The world/background should serve the page, not dominate it.

Header should include:

- LWA logo / mark
- current plan pill
- credits remaining
- account / billing / history access
- compact live status pill if useful

### B. Hero / input stage

This becomes a single clean operator console.

Left side:

- short premium headline
- one-line explanation
- source URL field
- upload button
- generate button

Right side:

- LWA recommendation card
- recommended destination
- recommended content type
- recommended output style
- reason for recommendation
- tiny advanced override control below

Supporting microcopy examples:

```text
Paste one source. LWA ranks the best short-form cuts.
Rendered clips first. Strategy lanes second.
Manual override is optional.
```

The section should feel like:

```text
input → confidence → action
```

Not:

```text
input → confusion → settings menu
```

### C. Processing state

Waiting state should feel premium and useful.

Show:

- source ingest
- moment finding
- rank/packaging
- render/export
- delivery

Also surface:

- provider truth if relevant
- whether output is render-ready
- whether strategy-only fallback is active

### D. Results surface

The results view should have four clear sections.

#### 1. Lead result strip

One hero result card at the top:

- best clip
- play preview
- render status
- post order = #1
- recommended platform
- why it matters
- export / copy / share / recover actions

This should feel like:

```text
Here is the best answer first.
```

#### 2. Rendered clips lane

A horizontal or grid lane showing only rendered/media-ready items.

Each rendered card should show:

- preview/player
- title
- hook
- score / confidence
- post order
- thumbnail text
- CTA
- packaging angle
- export button
- copy package button

This lane is the proof lane.

#### 3. Strategy-only lane

Below rendered clips:

- strategy-only cards
- clear not-yet-media-ready label
- packaging/testing usefulness
- recover/re-render action if available

Each strategy card should show:

- why it matters
- recommended hook variants
- recommended caption style
- post order suggestion
- reason it is not rendered yet
- recovery action

This lane should feel like:

```text
High-value ideas not yet fully materialized.
```

Not:

```text
fake completed clips.
```

#### 4. Packaging / export rail

A compact panel/drawer that collects:

- best hook variants
- caption variants
- thumbnail text
- CTA suggestion
- post order
- packaging angle
- target platform
- output style
- export bundle

---

## New card language

Rendered card language:

- Ready now
- Playable
- Export-ready
- Post first
- Rendered
- Package copied

Strategy-only card language:

- Strategy only
- Not yet rendered
- Recovery available
- Packaging ready
- Test this hook
- Queue recovery

Do not let both card types use the same badge language.

---

## New visual hierarchy

Highest emphasis:

- source input
- generate action
- lead best clip
- rendered clips

Medium emphasis:

- recommendation metadata
- packaging metadata
- export tools

Lower emphasis:

- strategy-only lane
- advanced overrides
- secondary history
- background/world details

---

## Premium world layer rules

Keep:

- side beings
- subtle celestial motion
- energy/fog/aura accents
- premium black/gold tone
- world identity

Remove or reduce:

- center-screen clutter
- heavy abstract glow without utility
- noisy visual competition with results
- background behavior that makes the tool harder to read

Ideal world behavior:

- idle
- analyzing
- rendering
- complete
- premium state

The world should stay at the edge and reinforce mood, not take over the job of the product.

---

## Mobile / containment rules

The rebuild must be mobile-safe:

- stacked input card first
- recommendation card second
- lead result third
- rendered lane as vertical cards
- strategy lane collapsible
- packaging/export as accordions

Avoid tiny chips everywhere, over-wide rows that collapse badly, and impossible comparison layouts on smaller screens.

---

## File-level frontend rebuild plan

Likely rebuild targets:

```text
lwa-web/components/clip-studio.tsx
lwa-web/components/VideoCard.tsx
lwa-web/components/HeroClip.tsx
lwa-web/lib/types.ts
lwa-web/lib/api.ts
```

### clip-studio.tsx

Main orchestrator:

- source intake
- recommendation rail
- status phases
- rendered lane
- strategy lane
- export drawer

### VideoCard.tsx

Split into clearer variants:

- rendered card
- strategy-only card

### HeroClip.tsx

Lead best-result card:

- best clip preview
- post-first logic
- export / copy package actions

### types.ts

Needs stronger typing around:

- render state
- strategy state
- packaging metadata
- post order
- recommendation metadata

### api.ts

Keep simple and preserve current contract truth.

---

## What should be deleted or reduced in the UI

Delete or reduce:

- front-loaded forced platform choice
- duplicated chips that repeat the same information
- visually equal treatment for all result types
- weak generic explanatory copy
- clutter blocks that do not help the creator act faster

---

## Code seed: frontend rebuild preview

Use this as a visual/directional starter, not a blind replacement unless the current repo structure confirms compatibility.

```tsx
"use client";

import { useMemo, useState } from "react";

type ProcessingSummary = {
  plan_name?: string;
  plan_code?: string;
  credits_remaining?: number;
  ai_provider?: string;
  target_platform?: string;
  platform_decision?: string;
  recommended_platform?: string | null;
  platform_recommendation_reason?: string | null;
  recommended_content_type?: string | null;
  recommended_output_style?: string | null;
  rendered_clip_count?: number;
  strategy_only_clip_count?: number;
  estimated_turnaround?: string | null;
  recommended_next_step?: string | null;
};

type ClipResult = {
  id: string;
  title: string;
  hook: string;
  caption: string;
  score?: number | null;
  confidence_score?: number | null;
  rank?: number | null;
  post_rank?: number | null;
  why_this_matters?: string | null;
  thumbnail_text?: string | null;
  cta_suggestion?: string | null;
  packaging_angle?: string | null;
  platform_fit?: string | null;
  caption_style?: string | null;
  hook_variants?: string[];
  caption_variants?: Record<string, string>;
  clip_url?: string | null;
  raw_clip_url?: string | null;
  edited_clip_url?: string | null;
  preview_url?: string | null;
  preview_image_url?: string | null;
  download_url?: string | null;
};

type ClipResponse = {
  request_id: string;
  status: string;
  video_url: string;
  processing_summary?: ProcessingSummary;
  clips: ClipResult[];
};

type StudioState = "idle" | "analyzing" | "ready";

function cn(...values: Array<string | false | null | undefined>) {
  return values.filter(Boolean).join(" ");
}

function getPreviewUrl(clip: ClipResult) {
  return clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url || null;
}

function isRendered(clip: ClipResult) {
  return Boolean(getPreviewUrl(clip) || clip.download_url);
}

function StatPill({
  label,
  value,
  accent = false,
}: {
  label: string;
  value: string | number;
  accent?: boolean;
}) {
  return (
    <div
      className={cn(
        "rounded-full border px-3 py-1 text-xs tracking-wide",
        accent
          ? "border-yellow-400/40 bg-yellow-400/10 text-yellow-200"
          : "border-white/10 bg-white/5 text-white/70",
      )}
    >
      <span className="mr-2 text-white/45">{label}</span>
      <span>{value}</span>
    </div>
  );
}

function LeadClipCard({ clip }: { clip: ClipResult }) {
  const preview = getPreviewUrl(clip);

  return (
    <div className="rounded-[28px] border border-yellow-400/20 bg-gradient-to-br from-white/8 to-white/4 p-6 shadow-2xl shadow-black/30">
      <div className="mb-4 flex flex-wrap gap-2">
        <StatPill label="Lead" value={`#${clip.post_rank || clip.rank || 1}`} accent />
        <StatPill label="Score" value={clip.score || 0} />
        <StatPill label="Confidence" value={clip.confidence_score || 0} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="overflow-hidden rounded-[22px] border border-white/10 bg-black/40">
          {preview ? (
            <video src={preview} controls className="aspect-[9/16] w-full object-cover" />
          ) : (
            <div className="flex aspect-[9/16] items-center justify-center text-sm text-white/45">
              Preview unavailable
            </div>
          )}
        </div>

        <div className="flex flex-col justify-between">
          <div>
            <p className="mb-2 text-xs uppercase tracking-[0.3em] text-yellow-200/70">
              Best clip first
            </p>
            <h2 className="text-2xl font-semibold text-white">{clip.title}</h2>
            <p className="mt-4 text-lg leading-7 text-white/85">{clip.hook}</p>
            <p className="mt-4 text-sm leading-7 text-white/60">
              {clip.why_this_matters || "This is the strongest opener in the current pack."}
            </p>
          </div>

          <div className="mt-6 space-y-3">
            <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/45">Thumbnail text</p>
              <p className="mt-2 text-lg text-white">{clip.thumbnail_text || "Best Clip"}</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-white/45">CTA</p>
              <p className="mt-2 text-sm text-white/80">
                {clip.cta_suggestion || "Ask viewers to comment or follow for the next cut."}
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <button className="rounded-full bg-yellow-300 px-5 py-3 text-sm font-medium text-black transition hover:opacity-90">
                Export lead clip
              </button>
              <button className="rounded-full border border-white/15 px-5 py-3 text-sm text-white/80 transition hover:bg-white/5">
                Copy package
              </button>
              <button className="rounded-full border border-white/15 px-5 py-3 text-sm text-white/80 transition hover:bg-white/5">
                Queue post
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function RenderedClipCard({ clip }: { clip: ClipResult }) {
  const preview = getPreviewUrl(clip);

  return (
    <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-emerald-300">
          Rendered
        </span>
        <span className="text-xs text-white/45">Post #{clip.post_rank || clip.rank || "—"}</span>
      </div>

      <div className="overflow-hidden rounded-[18px] border border-white/10 bg-black/40">
        {preview ? (
          <video src={preview} controls className="aspect-[9/16] w-full object-cover" />
        ) : (
          <div className="flex aspect-[9/16] items-center justify-center text-sm text-white/45">
            Preview unavailable
          </div>
        )}
      </div>

      <div className="mt-4">
        <h3 className="text-lg font-medium text-white">{clip.title}</h3>
        <p className="mt-2 text-sm leading-6 text-white/75">{clip.hook}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          <StatPill label="Score" value={clip.score || 0} />
          <StatPill label="Confidence" value={clip.confidence_score || 0} />
        </div>
        <p className="mt-3 text-sm text-white/55">{clip.why_this_matters}</p>
      </div>
    </div>
  );
}

function StrategyClipCard({ clip }: { clip: ClipResult }) {
  return (
    <div className="rounded-[24px] border border-amber-400/20 bg-amber-400/[0.04] p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className="rounded-full bg-amber-300/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-amber-200">
          Strategy only
        </span>
        <span className="text-xs text-white/45">Post #{clip.post_rank || clip.rank || "—"}</span>
      </div>

      <h3 className="text-lg font-medium text-white">{clip.title}</h3>
      <p className="mt-2 text-sm leading-6 text-white/75">{clip.why_this_matters}</p>

      <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-3">
        <p className="text-xs uppercase tracking-[0.2em] text-white/45">Best hook variants</p>
        <ul className="mt-2 space-y-2">
          {(clip.hook_variants || []).slice(0, 3).map((hook) => (
            <li key={hook} className="text-sm text-white/80">
              • {hook}
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        <button className="rounded-full border border-white/15 px-4 py-2 text-sm text-white/80 hover:bg-white/5">
          Recover render
        </button>
        <button className="rounded-full border border-white/15 px-4 py-2 text-sm text-white/80 hover:bg-white/5">
          Copy strategy
        </button>
      </div>
    </div>
  );
}

export default function ClipStudioRebuildPreview() {
  const [videoUrl, setVideoUrl] = useState("");
  const [state, setState] = useState<StudioState>("idle");

  const mockResponse: ClipResponse = {
    request_id: "demo_1",
    status: "success",
    video_url: videoUrl,
    processing_summary: {
      plan_name: "Pro",
      credits_remaining: 24,
      recommended_platform: "TikTok",
      platform_recommendation_reason: "Fast interruption-led beat with strong curiosity hook.",
      recommended_content_type: "Reaction / commentary",
      recommended_output_style: "Tension-led short-form",
      rendered_clip_count: 2,
      strategy_only_clip_count: 1,
      recommended_next_step: "Export the lead clip first, then test the second rendered cut.",
    },
    clips: [
      {
        id: "1",
        title: "The interruption moment",
        hook: "This is the exact beat that makes the whole clip hit harder.",
        caption: "Post this first if you want the strongest opening pull.",
        score: 92,
        confidence_score: 89,
        rank: 1,
        post_rank: 1,
        why_this_matters: "Open with this because it creates the cleanest interruption and strongest first-post pull.",
        thumbnail_text: "Interruption Moment",
        cta_suggestion: "Ask viewers if they want the full breakdown next.",
        packaging_angle: "shock",
        caption_style: "Tension-led",
        hook_variants: [
          "Stop scrolling: this changes the whole clip.",
          "The moment nobody sees coming.",
          "This is the opener worth posting first.",
        ],
        preview_url: "https://www.w3schools.com/html/mov_bbb.mp4",
      },
      {
        id: "2",
        title: "The deeper follow-up",
        hook: "Use this second because it deepens the story after the opener lands.",
        caption: "Second-post continuation with stronger context.",
        score: 85,
        confidence_score: 78,
        rank: 2,
        post_rank: 2,
        why_this_matters: "Use this second because it deepens the angle and gives the posting stack a stronger middle beat.",
        thumbnail_text: "Second Beat Payoff",
        cta_suggestion: "Ask viewers if they want the next part.",
        packaging_angle: "story",
        preview_url: "https://www.w3schools.com/html/movie.mp4",
      },
      {
        id: "3",
        title: "The contrarian take",
        hook: "Most creators still post this angle in the wrong order.",
        caption: "This is useful even before render recovery.",
        score: 80,
        confidence_score: 74,
        rank: 3,
        post_rank: 3,
        why_this_matters: "This strategy angle is still valuable because it sharpens the order and package logic.",
        thumbnail_text: "Wrong Posting Order",
        cta_suggestion: "Ask viewers which side they agree with.",
        packaging_angle: "controversy",
        hook_variants: [
          "Most creators still get this wrong.",
          "The take people will argue with instantly.",
          "If you want comments, lead with this contrarian beat.",
        ],
      },
    ],
  };

  const rendered = useMemo(
    () => mockResponse.clips.filter((clip) => isRendered(clip)),
    [mockResponse.clips],
  );

  const strategyOnly = useMemo(
    () => mockResponse.clips.filter((clip) => !isRendered(clip)),
    [mockResponse.clips],
  );

  const lead = rendered[0] || mockResponse.clips[0];

  return (
    <div className="min-h-screen bg-[#060606] text-white">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-yellow-200/60">LWA</p>
            <h1 className="mt-2 text-3xl font-semibold">Clip command center</h1>
            <p className="mt-2 max-w-2xl text-sm text-white/55">
              One source in. Best cut first. Rendered proof first. Strategy lane second.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <StatPill label="Plan" value={mockResponse.processing_summary?.plan_name || "Free"} accent />
            <StatPill label="Credits" value={mockResponse.processing_summary?.credits_remaining || 0} />
            <StatPill label="Rendered" value={mockResponse.processing_summary?.rendered_clip_count || 0} />
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[30px] border border-white/10 bg-white/[0.04] p-6">
            <p className="text-xs uppercase tracking-[0.25em] text-white/45">Source input</p>
            <h2 className="mt-3 text-2xl font-semibold">Drop one source. Let LWA pick the first move.</h2>

            <div className="mt-6 flex flex-col gap-4">
              <input
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="Paste YouTube, TikTok, Instagram, podcast, or upload source..."
                className="h-14 rounded-2xl border border-white/10 bg-black/30 px-4 text-sm outline-none ring-0 placeholder:text-white/30"
              />

              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => setState("analyzing")}
                  className="rounded-full bg-yellow-300 px-5 py-3 text-sm font-medium text-black"
                >
                  Generate clip pack
                </button>
                <button className="rounded-full border border-white/15 px-5 py-3 text-sm text-white/80">
                  Upload source
                </button>
                <button className="rounded-full border border-white/15 px-5 py-3 text-sm text-white/80">
                  Advanced override
                </button>
              </div>
            </div>
          </div>

          <div className="rounded-[30px] border border-yellow-400/15 bg-gradient-to-br from-yellow-400/[0.08] to-transparent p-6">
            <p className="text-xs uppercase tracking-[0.25em] text-yellow-200/70">LWA recommendation</p>
            <div className="mt-4 space-y-4">
              <div>
                <p className="text-sm text-white/45">Recommended destination</p>
                <p className="mt-1 text-xl text-white">{mockResponse.processing_summary?.recommended_platform}</p>
              </div>
              <div>
                <p className="text-sm text-white/45">Content type</p>
                <p className="mt-1 text-white/85">{mockResponse.processing_summary?.recommended_content_type}</p>
              </div>
              <div>
                <p className="text-sm text-white/45">Output style</p>
                <p className="mt-1 text-white/85">{mockResponse.processing_summary?.recommended_output_style}</p>
              </div>
              <div>
                <p className="text-sm text-white/45">Reason</p>
                <p className="mt-1 text-sm leading-6 text-white/70">
                  {mockResponse.processing_summary?.platform_recommendation_reason}
                </p>
              </div>
            </div>
          </div>
        </div>

        {state !== "idle" && (
          <div className="mt-10 space-y-8">
            <LeadClipCard clip={lead} />

            <section>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-emerald-300/70">Rendered lane</p>
                  <h3 className="mt-2 text-2xl font-semibold">Playable clips ready now</h3>
                </div>
              </div>

              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {rendered.map((clip) => (
                  <RenderedClipCard key={clip.id} clip={clip} />
                ))}
              </div>
            </section>

            <section>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.25em] text-amber-200/70">Strategy lane</p>
                  <h3 className="mt-2 text-2xl font-semibold">Useful next angles not yet rendered</h3>
                </div>
              </div>

              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {strategyOnly.map((clip) => (
                  <StrategyClipCard key={clip.id} clip={clip} />
                ))}
              </div>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## Codex prompt for frontend rebuild

```text
Rebuild the web frontend experience layer immediately using the attached UI spec and TSX starter as direction.

Rules:
- preserve the backend and route spine
- preserve auto destination
- preserve rendered-first review
- preserve strategy-only separation
- preserve recovery flow
- preserve provider truth
- preserve plan/credits truth
- do not redesign the backend
- do not reopen solved iOS work
- do not build a fake editor

Execution target:
- rebuild clip-studio.tsx, HeroClip.tsx, and VideoCard.tsx
- keep current API contracts compatible
- implement the new layout:
  - source intake
  - LWA recommendation rail
  - lead best clip
  - rendered lane
  - strategy lane
  - packaging/export rail
- keep the premium world shell but reduce clutter in the center
- prioritize creator clarity, post order, and export readiness
- make the page feel premium, mythic, and operator-grade

Required output:
1. exact files changed
2. what was preserved
3. what was rebuilt
4. build verification
5. commit message
```

---

## Codex terminal lane safety prompts

### Backend terminal emergency stop after wrong frontend prompt

```text
STOP.

You were accidentally given a FRONTEND TRACK prompt.

Do not edit lwa-web.
Do not edit lwa-ios.

Show current status only:
1. git status --short
2. files you inspected
3. files you changed, if any
4. whether any lwa-web or lwa-ios files were touched

If no backend task has started, stop and wait.
If frontend files were changed, do not continue and do not commit.
```

### Frontend terminal lane guard

```text
Continue ONLY as RIGHT CODEX: FRONTEND TRACK.

You may edit lwa-web only.

Do not touch:
- lwa-backend
- lwa-ios

Proceed with the multi-destination money CTA system only if your planned files are frontend files.

Before editing, print:
- current git status --short
- exact files you plan to touch
- confirmation that backend/iOS will not be edited
```

### Both terminals pause report

```text
PAUSE.

Do not commit.

Report:
1. current branch
2. git status --short
3. files changed by this run
4. whether lwa-backend was touched
5. whether lwa-web was touched
6. whether lwa-ios was touched
7. verification commands run, if any

Wait after reporting.
```

### Lane rule

For frontend money CTA work:

- right terminal only
- allowed: lwa-web
- not allowed: lwa-backend, lwa-ios

Backend gets a later chunk: revenue event tracking foundation.

---

## Codex artifact bundle index from shared context

The shared context referenced a Codex terminal artifact bundle with these intended documents:

- START_HERE_CODEX_TERMINAL.md
- 01_MASTER_CODEX_TERMINAL_PROMPT.txt
- 02_SYSTEM_PROMPT_FOR_CODEX.txt
- 03_FRONTEND_REBUILD_TRACK.txt
- 04_BACKEND_FREE_LAUNCH_AND_FALLBACKS.txt
- 05_DIRECTOR_BRAIN_V0.txt
- 06_MARKETPLACE_MVP_LATER.txt
- 07_REALMS_AND_PROOF_LAYER_LATER.txt
- 08_EMERGENCY_STOP.txt
- LWA_Master_Execution_Report.docx
- LWA_30_90_365_Roadmap.xlsx
- LWA_Investor_Pitch_Deck.pptx
- LWA_System_Architecture.pdf
- LWA_Architecture_Blueprint.md
- LWA_System_Flow_Mermaid.md
- LWA_Codex_Terminal_Runbook.md

Repo-safe rule:

Do not commit binary artifact outputs or heavy ZIPs unless explicitly needed. Prefer Markdown/TXT equivalents in repo.

---

## LWA visual direction for Canva / hero asset

Prompt direction:

```text
LWA — pronounced “lee-wuh”
African / Black anime
Afro-futurist mythic sci-fi
powerful big dreadlock hero
3D cinematic world
premium landing-page / showcase visual
```

Choose the visual that feels:

```text
powerful
African
futuristic
creator-world
not generic fantasy
not Omega Worlds
clearly LWA
```

Canva review checklist:

```text
Title says LWA
No “OMEGA WORLDS”
Character has big dreadlocks
Feels African / Afro-futurist
Looks premium enough for homepage
Readable as a landing-page hero
```

Refinement prompt:

```text
Make the central character more powerful and regal. Emphasize large dreadlocks, Afro-futurist armor, African anime facial features, gold-purple glowing sigils, and a premium 3D cinematic world. Keep the title as LWA only. Do not add Omega Worlds.
```

Export target:

```text
lwa-web/public/brand/lwa-hero.png
```

Use PNG 2x or 3x for the landing-page hero asset.

---

## Final instruction for builders

This appendix is not permission to rewrite everything. It is a context lock.

Use it to preserve product truth while building the missing web experience layer:

```text
source → recommendation → rendered proof → strategy lane → packaging/export → unlock/pay → proof/style memory
```
