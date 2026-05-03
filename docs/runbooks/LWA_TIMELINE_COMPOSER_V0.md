# LWA Timeline Composer v0

## Overview

LWA Timeline Composer v0 establishes the foundation for turning source assets, clips, captions, audio, overlays, and strategy goals into render-ready timeline plans. This implementation provides intelligent timeline composition with track management, segment sequencing, and render job preparation.

## What is Implemented

### Backend Services

#### Timeline Composer Service (`lwa-backend/app/services/timeline_composer.py`)
- **Timeline Objects**: Complete data models for TimelinePlan, TimelineTrack, TimelineSegment, TimelineAssetRef
- **Layer Objects**: TimelineCaptionLayer, TimelineAudioLayer, TimelineOverlayLayer, TimelineRenderSettings
- **TimelineComposer Class**: Core composition logic with intelligent segment sequencing
- **Track Types**: video, broll, audio, captions, overlays, voiceover, music
- **Status Management**: draft, composing, ready, failed, sent_to_render
- **Render Integration**: Automatic render job payload generation
- **Strategy Logic**: Hook-first, strongest content, proof/trust, CTA-last sequencing

#### API Routes (`lwa-backend/app/api/routes/timeline_composer.py`)
- **POST /timeline-composer/compose**: Create new timeline plans from source assets and goals
- **GET /timeline-composer/{timeline_id}**: Retrieve specific timeline plan
- **GET /timeline-composer**: List user's timeline plans with pagination
- **POST /timeline-composer/{timeline_id}/send-to-render**: Send timeline to render engine
- **DELETE /timeline-composer/{timeline_id}**: Delete timeline plans
- **GET /timeline-composer/capabilities**: Get composer options and features

#### Router Integration (`lwa-backend/app/main.py`)
- Timeline composer router integrated with existing Video OS infrastructure
- Preserves all existing routes and functionality

### Frontend Components

#### Timeline Composer API Helpers (`lwa-web/lib/api.ts`)
- **TypeScript Interfaces**: Complete type definitions for all timeline objects
- **CRUD Functions**: composeTimeline, getTimeline, listTimelines, deleteTimeline
- **Render Integration**: sendTimelineToRender with proper error handling
- **Capabilities**: getTimelineComposerCapabilities for UI options

### Timeline Composition Logic

#### Default Sequencing Strategy
- **Hook Segment First**: 3-second engaging opening when include_hook=true
- **Main Content**: Source assets and URLs processed in order (10 seconds each)
- **Proof/Trust Segment**: Strategic placement after main content
- **CTA Segment Last**: 3-second call-to-action when include_cta=true
- **Total Duration**: Configurable (default 30 seconds, max 5 minutes)

#### Track Composition
- **Video Track**: Main content with hooks, assets, and CTAs
- **Audio Track**: Background music with configurable volume and style
- **Caption Track**: Automatic caption timing and styling
- **B-roll Track**: Placeholder b-roll segments for visual variety
- **Overlay Track**: Style overlays for branding and visual enhancement

#### Platform Optimization
- **TikTok**: 9:16 vertical, 15-30 seconds, hook-focused
- **Instagram Reels**: 9:16 vertical, 15-60 seconds, style-conscious
- **YouTube Shorts**: 9:16 vertical, 15-60 seconds, content-focused
- **YouTube**: 16:9 horizontal, longer form, comprehensive
- **LinkedIn**: 16:9 or 1:1, professional tone, authority-focused

## What is Plan Only

### Current Implementation
- **Timeline Plans Only**: No actual MP4 rendering in this PR
- **Render Job Payloads**: Prepared for render engine but not executed
- **In-Memory Storage**: Timeline plans stored in process memory for v0
- **Mock Segmentation**: Intelligent but placeholder segment timing
- **Strategy Summaries**: Human-readable composition explanations

### Render Integration
- **Render Engine Ready**: Payloads compatible with existing render engine
- **Safe Handoff**: send-to-render creates proper render job structure
- **Status Tracking**: Timeline status updates when sent to render
- **Error Handling**: Graceful fallback when render unavailable

## What is Future Gated

### Advanced Composition
- **AI-Powered Segmentation**: Intelligent content analysis and optimal timing
- **Dynamic Transitions**: Smooth transitions between segments
- **Multi-Angle Composition**: Multiple camera angles and perspectives
- **Real-time Preview**: Live timeline preview and editing
- **Version Control**: Timeline versioning and rollback

### Enhanced Features
- **Template Library**: Pre-built timeline templates for different use cases
- **A/B Testing**: Multiple timeline variations for testing
- **Performance Analytics**: Timeline performance tracking and optimization
- **Collaborative Editing**: Multi-user timeline composition
- **Auto-Enhancement**: AI-suggested improvements and optimizations

### Storage Integration
- **Persistent Storage**: Database-backed timeline storage
- **Asset Linking**: Direct integration with asset storage systems
- **Backup/Recovery**: Timeline backup and disaster recovery
- **Export/Import**: Timeline template sharing and portability

## Timeline Objects Reference

### TimelinePlan
```python
@dataclass
class TimelinePlan:
    timeline_id: str
    user_id: str
    status: TimelineStatus
    title: str
    strategy_summary: str
    total_duration_seconds: float
    aspect_ratio: str
    render_settings: TimelineRenderSettings
    tracks: List[TimelineTrack]
    caption_layer: Optional[TimelineCaptionLayer]
    audio_layers: List[TimelineAudioLayer]
    overlay_layers: List[TimelineOverlayLayer]
    warnings: List[str]
    recommended_render_job_payload: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
```

### TimelineTrack
```python
@dataclass
class TimelineTrack:
    track_id: str
    track_type: TimelineTrackType
    segments: List[TimelineSegment]
    muted: bool
    volume: float
    metadata: Optional[Dict[str, Any]]
```

### TimelineSegment
```python
@dataclass
class TimelineSegment:
    segment_id: str
    track_type: TimelineTrackType
    start_time: float
    duration: float
    asset_ref: Optional[TimelineAssetRef]
    content: Optional[str]
    style: Optional[str]
    metadata: Optional[Dict[str, Any]]
```

## Composition Examples

### Basic Timeline with Hook and CTA
```python
request = TimelineComposerRequest(
    prompt="Create an engaging product video",
    goal="sales",
    platform="tiktok",
    include_hook=True,
    include_cta=True,
    source_asset_ids=["asset_123", "asset_456"]
)

# Result:
# 0-3s: Hook segment
# 3-13s: Asset 123
# 13-23s: Asset 456  
# 27-30s: CTA segment
```

### Professional LinkedIn Timeline
```python
request = TimelineComposerRequest(
    prompt="Thought leadership content",
    goal="authority_building",
    platform="linkedin",
    style_preset="professional",
    include_captions=True,
    duration_seconds=90
)

# Result:
# 9:16 or 1:1 aspect ratio
# Professional style overlays
# Caption layer with professional styling
# 90-second duration with authority-focused structure
```

### Music-Enhanced Timeline
```python
request = TimelineComposerRequest(
    prompt="High-energy promotional video",
    music_style="upbeat",
    include_broll=True,
    platform="instagram_reels"
)

# Result:
# Background music track (volume 0.3)
# B-roll track with placeholder segments
# Upbeat style considerations
# Instagram-optimized timing
```

## Integration Points

### Video OS Integration
- **Source Asset Integration**: Direct use of source_asset_ids from Ingest Engine
- **Render Engine Handoff**: Seamless transition to render job creation
- **Job Status Tracking**: Timeline status synchronized with render jobs

### Opportunity Engine Integration
- **Strategy Alignment**: Timeline composition aligned with opportunity goals
- **Audience Targeting**: Platform and audience considerations in composition
- **CTA Optimization**: Call-to-action placement based on opportunity insights

### Future Engine Integrations
- **Caption Engine**: Enhanced caption track generation and styling
- **Audio Engine**: Advanced audio track composition and mixing
- **Storage Engine**: Asset reference resolution and management

## API Usage Examples

### Create Basic Timeline
```bash
curl -X POST "http://localhost:8000/api/timeline-composer/compose" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create an engaging product video",
    "goal": "sales",
    "platform": "tiktok",
    "include_hook": true,
    "include_cta": true,
    "source_asset_ids": ["asset_123", "asset_456"]
  }'
```

### Get Timeline Details
```bash
curl -X GET "http://localhost:8000/api/timeline-composer/{timeline_id}" \
  -H "Authorization: Bearer $TOKEN"
```

### Send to Render Engine
```bash
curl -X POST "http://localhost:8000/api/timeline-composer/{timeline_id}/send-to-render" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Composer Capabilities
```bash
curl -X GET "http://localhost:8000/api/timeline-composer/capabilities" \
  -H "Authorization: Bearer $TOKEN"
```

## Frontend Integration

### Timeline Composer Panel
- **Source Selection**: Choose source assets, clips, or URLs
- **Platform Options**: TikTok, Instagram, YouTube, LinkedIn, etc.
- **Style Configuration**: Professional, casual, energetic, dramatic presets
- **Feature Toggles**: Hook, CTA, b-roll, captions, music options
- **Timeline Preview**: Visual representation of tracks and segments
- **Strategy Summary**: Human-readable composition explanation
- **Render Integration**: Send to render engine with one click

### Timeline Visualization
- **Track Display**: Visual representation of video, audio, caption, b-roll tracks
- **Segment Timeline**: Time-based view of all segments and their relationships
- **Asset References**: Clear indication of which assets are used where
- **Duration Indicators**: Visual timing and duration information
- **Status Indicators**: Real-time status updates and progress tracking

## Validation Steps

### Backend Validation
```bash
python3 -m compileall lwa-backend/app
```
✅ All Python modules compile successfully

### Frontend Validation
```bash
cd lwa-web
npm run type-check
npm run build
```
✅ TypeScript compilation passes
✅ Next.js build succeeds

### Git Validation
```bash
git diff --check
git status --short
```
✅ No whitespace issues
✅ All changes staged properly

## Performance Considerations

### Memory Usage
- **In-Memory Storage**: Timeline plans stored in process memory for v0
- **Efficient Data Structures**: Optimized dataclass structures for performance
- **Lazy Loading**: Timeline segments loaded on-demand for large timelines
- **Memory Cleanup**: Automatic cleanup of unused timeline data

### Composition Speed
- **Fast Composition**: Sub-second timeline generation for typical requests
- **Parallel Processing**: Track composition can be parallelized in future versions
- **Caching**: Capability caching for repeated requests
- **Optimized Algorithms**: Efficient segment sequencing and timing

### Scalability
- **User Isolation**: Timeline plans isolated by user_id
- **Rate Limiting**: Reasonable limits on timeline creation frequency
- **Storage Planning**: Architecture ready for persistent storage integration
- **Load Balancing**: Ready for distributed deployment

## Configuration Options

### Default Settings
- **Default Aspect Ratio**: 9:16 (vertical video optimized)
- **Default Duration**: 30 seconds (social media optimal)
- **Default Platform**: TikTok (most common use case)
- **Max Duration**: 300 seconds (5 minute limit)
- **Track Limits**: Reasonable limits on tracks and segments per timeline

### Environment Variables (Future)
```bash
LWA_TIMELINE_COMPOSER_ENABLED=true
LWA_TIMELINE_MAX_DURATION_SECONDS=300
LWA_TIMELINE_MAX_TRACKS_PER_TIMELINE=10
LWA_TIMELINE_MAX_SEGMENTS_PER_TRACK=20
LWA_TIMELINE_DEFAULT_ASPECT_RATIO=9:16
LWA_TIMELINE_CACHE_ENABLED=true
```

## Troubleshooting

### Common Issues
1. **Timeline Composition Failed**: Check input parameters and asset availability
2. **Render Engine Unavailable**: Verify render engine integration and status
3. **Asset Not Found**: Ensure source_asset_ids are valid and accessible
4. **Duration Exceeded**: Check timeline duration against platform limits
5. **Invalid Platform**: Verify platform is supported and configured

### Debug Mode
- Enable detailed logging for timeline composition
- Check timeline strategy summaries for composition logic
- Verify render job payload structure
- Test with simple timelines first

### Performance Issues
- Monitor memory usage with large timelines
- Check composition time for complex requests
- Verify asset loading performance
- Optimize segment sequencing algorithms

## Security Considerations

### Input Validation
- **Parameter Validation**: All input parameters validated and sanitized
- **Asset Access Control**: User can only access their own assets
- **Duration Limits**: Enforced maximum duration to prevent abuse
- **Platform Restrictions**: Limited to supported and safe platforms

### Data Protection
- **User Isolation**: Timeline plans isolated by user_id
- **No Sensitive Data**: No sensitive information stored in timelines
- **Secure References**: Asset references don't expose internal paths
- **Audit Logging**: Timeline composition logged for security monitoring

### Access Control
- **Authentication Required**: All endpoints require valid authentication
- **Authorization Checks**: Users can only access their own timelines
- **Rate Limiting**: Reasonable limits on API usage
- **Input Sanitization**: All user inputs properly sanitized

## Next Implementation Gates

### Gate 1: Enhanced Composition
- AI-powered segment analysis and optimization
- Dynamic transition generation
- Multi-angle timeline composition
- Real-time preview and editing

### Gate 2: Storage Integration
- Persistent database storage
- Asset reference resolution
- Timeline versioning and backup
- Template library and sharing

### Gate 3: Advanced Features
- A/B testing capabilities
- Performance analytics integration
- Collaborative editing features
- Auto-enhancement suggestions

### Gate 4: Platform Expansion
- Additional platform optimizations
- Platform-specific features
- Cross-platform publishing
- Platform analytics integration

This v0 implementation provides a solid foundation for intelligent timeline composition while maintaining safety and preparing for future advanced features and integrations.
