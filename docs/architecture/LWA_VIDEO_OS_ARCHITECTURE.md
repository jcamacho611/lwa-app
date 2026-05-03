# LWA Video OS Architecture

## Overview

LWA transforms from "AI clipper" to **all-video machine** - a complete Video OS that accepts any input and produces any output.

## Architecture

```
Frontend (React/Next.js)
    ↓
LWA API Gateway / Orchestrator
    ↓
Multiple Engines:
├── 1. Clip Engine (existing)
├── 2. Render Engine (NEW - backbone)
├── 3. AI Video Generation Engine (NEW)
├── 4. Audio/Music/Voice Engine (NEW)
├── 5. Timeline Editing Engine (NEW)
├── 6. Caption/Subtitles Engine (NEW)
├── 7. Storage/CDN Engine (existing)
└── 8. Safety/Rights/Cost Engine (existing)
```

## Input Anything

| Input | What LWA Does |
|-------|---------------|
| Long video | clips, edits, captions, b-roll, shorts |
| Multiple videos | combines best moments into one master edit |
| Audio/song | lyric video, visualizer, shorts, captions |
| Podcast | clips, guest highlights, quote cards |
| Images | image-to-video, slideshow, motion graphics |
| Script | full generated video |
| Voice note | script, narration, video |
| Product/business assets | ad videos, explainers, proof clips |
| Existing clip | remix, extend, loop, polish |

## Output Everything

- Short clips
- Full generated videos
- AI b-roll
- Captions
- Thumbnails
- Titles
- Hooks
- CTAs
- Post copy
- Music
- Voiceover
- Dub versions
- Multiple aspect ratios
- Campaign pack
- Downloadable MP4s
- Proof/case-study assets

## Engine Details

### Engine A: Clip Engine (Partly Existing)

**Purpose**: Find the best moments from existing videos

**Current State**: ✅ Basic clipping with Director Brain intelligence

**Needed**: Enhanced with timeline integration and render pipeline

### Engine B: Render Engine (NEW - URGENT)

**Purpose**: Take clips/assets/timeline instructions and render finished MP4s

**Key Features**:
- Async job processing (like Sora)
- Multiple output formats/resolutions
- Timeline-based rendering
- Asset management
- CDN integration

**Provider Options**:
- Shotstack (JSON timeline API)
- Custom FFmpeg pipeline
- Cloud rendering services

### Engine C: AI Video Generation Engine (NEW)

**Purpose**: Text-to-video, image-to-video, video remix, extend, loop, scene generation

**Pattern**: Async (create job → poll status → download MP4 → store)

**Provider Options**:
- OpenAI Sora API
- Runway Gen-2
- Veo
- Custom models

### Engine D: Timeline Composer (NEW)

**Purpose**: Build edit timeline from multiple clips, images, audio, captions, transitions, titles

**Data Model**: JSON timeline (Shotstack-style)
```json
{
  "timeline": {
    "tracks": [
      {
        "clips": [
          {
            "asset": {"type": "video", "src": "url"},
            "start": 0, "length": 5,
            "transition": {"type": "fade", "duration": 0.5}
          }
        ]
      }
    ],
    "output": {"format": "mp4", "resolution": "1080x1920"}
  }
}
```

### Engine E: Audio/Music/Voice Engine (NEW)

**Purpose**: TTS, dubbing, music generation, sound effects

**Provider Options**:
- ElevenLabs (TTS, dubbing, music, SFX)
- Custom voice models
- Music generation APIs

### Engine F: Caption/Subtitles Engine (NEW)

**Purpose**: Generate, sync, and style captions for all content

**Features**:
- Auto-transcription
- Translation
- Styling (fonts, colors, animations)
- Platform-specific formatting

## API Gateway/Orchestrator

The frontend talks to **one LWA backend API**, not multiple providers.

### Unified Job Model

```json
{
  "job_id": "uuid",
  "input_type": "video|audio|image|script|multi",
  "input_assets": ["url1", "url2"],
  "output_requirements": {
    "formats": ["mp4", "mov"],
    "aspect_ratios": ["9:16", "16:9"],
    "durations": ["short", "full"],
    "engines": ["clip", "render", "ai_generate"]
  },
  "status": "pending|processing|completed|failed",
  "results": {
    "clips": [...],
    "full_video": "url",
    "assets": [...]
  }
}
```

### Engine Routing Logic

```python
def route_job(job):
    engines = []
    
    if job.input_type in ["video", "multi"]:
        engines.append("clip")
    
    if job.output_requirements.get("full_video"):
        engines.append("timeline")
        engines.append("render")
    
    if job.output_requirements.get("ai_generate"):
        engines.append("ai_video")
    
    if job.output_requirements.get("audio"):
        engines.append("audio")
    
    return engines
```

## Implementation Priority

### Phase 1: Render Engine (Backbone)
1. Basic timeline model
2. Shotstack integration
3. Async job processing
4. MP4 output pipeline

### Phase 2: Timeline Composer
1. JSON timeline builder
2. Multi-asset composition
3. Transitions and effects
4. Multiple output formats

### Phase 3: AI Video Generation
1. Sora API integration
2. Async job handling
3. Scene generation
4. Remix and extend workflows

### Phase 4: Audio Engine
1. ElevenLabs integration
2. TTS and dubbing
3. Music generation
4. Sound effects

### Phase 5: Unified API Gateway
1. Job orchestration
2. Engine routing
3. Status polling
4. Result aggregation

## Safety & Cost Controls

- Input validation and sanitization
- Copyright detection
- Cost tracking per engine
- Rate limiting
- Content safety filters
- Provider cost optimization

## Storage Strategy

- Temporary assets (job-specific)
- Permanent assets (user content)
- CDN distribution
- Expiration policies
- Backup and redundancy

## Success Metrics

- Job completion rate
- Render quality
- Processing speed
- Cost efficiency
- User satisfaction
- Asset reuse rate

This architecture transforms LWA from a single-feature app to a comprehensive Video OS that can handle any video creation workflow.
