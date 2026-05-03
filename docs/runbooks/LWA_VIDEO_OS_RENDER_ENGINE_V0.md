# LWA Video OS Render Engine v0

## Overview

LWA Video OS v0 establishes the foundation for transforming LWA from a clipping tool into a comprehensive AI video studio. This implementation provides provider-agnostic video job orchestration with mock rendering capabilities.

## What is Implemented

### Backend Services

#### Video OS Service (`lwa-backend/app/services/video_os.py`)
- **VideoJob data models**: Complete job lifecycle tracking with all required fields
- **VideoProviderAdapter base class**: Abstract interface for future provider implementations
- **MockVideoProviderAdapter**: Fully functional mock provider for development
- **VideoOSOrchestrator**: Central orchestration layer with validation and routing
- **Timeline models**: TimelinePlan, TimelineTrack, TimelineClip for future composition
- **Cost estimation**: Provider-agnostic cost calculation based on duration and resolution
- **Request validation**: Comprehensive input validation with safety limits

#### API Routes (`lwa-backend/app/api/routes/video_jobs.py`)
- **POST /video-jobs**: Create new video jobs with full parameter support
- **GET /video-jobs/{job_id}**: Retrieve job status and details
- **GET /video-jobs**: List recent jobs (in-memory storage for v0)
- **POST /video-jobs/{job_id}/cancel**: Cancel in-progress jobs
- **GET /video-jobs/capabilities**: Get system capabilities and configuration
- **POST /video-jobs/estimate-cost**: Estimate costs without creating jobs

#### Configuration (`lwa-backend/app/core/config.py`)
- **Safe defaults**: Video OS disabled by default, mock provider
- **Environment flags**: LWA_VIDEO_OS_ENABLED, LWA_VIDEO_PROVIDER, limits, etc.
- **Cost controls**: Max duration, max inputs, resolution limits
- **Provider gating**: LWA_VIDEO_ALLOW_LIVE_PROVIDERS disabled by default

### Frontend Components

#### Video OS Panel (`lwa-web/components/video-os-panel.tsx`)
- **Create Video tab**: Full job creation interface with all parameters
- **Recent Jobs tab**: Job status tracking with progress indicators
- **Info tab**: System capabilities and configuration display
- **Mock mode indicators**: Clear labeling when not using live providers
- **Error handling**: Comprehensive error display and validation
- **Responsive design**: Works on mobile and desktop

### Job Types Supported

1. **text_to_video**: Generate video from text prompts
2. **image_to_video**: Animate static images
3. **video_to_video**: Remix or enhance existing video
4. **clip_to_video**: Convert clips to finished videos
5. **audio_to_video**: Create visuals from audio
6. **song_visualizer**: Generate music videos
7. **timeline_render**: Render timeline compositions
8. **multi_asset_masterpiece**: Create videos from multiple sources

### Job Statuses

- **queued**: Job queued for processing
- **in_progress**: Currently being processed
- **completed**: Successfully finished
- **failed**: Processing failed
- **provider_not_configured**: Video OS disabled
- **canceled**: Job cancelled by user

## What is Mock Only

### Mock Provider Behavior
- Jobs complete instantly with "mock_render_completed_no_asset" message
- No actual video generation or rendering
- In-memory job storage (non-production)
- Sample timeline plans generated automatically
- Cost estimation works but is not tied to real provider costs

### Frontend Mock Indicators
- "Mock Mode" badge prominently displayed
- "Disabled" state when Video OS is not enabled
- Clear labeling that outputs are placeholder
- Info tab shows mock mode status

## What is Future Gated

### Live Provider Integration
- Sora, Seedance, Runway, Veo, Pika, Luma adapters exist as placeholders
- No actual API calls to live providers
- Provider credentials not exposed
- Live providers disabled by default

### Advanced Features
- Real video rendering (FFmpeg/cloud)
- Persistent job storage (database)
- File upload/ingest
- Actual timeline composition
- Real audio/music generation
- CDN integration for outputs

## Provider Adapter Plan

### Implemented
- **MockVideoProviderAdapter**: Fully functional for development

### Placeholders (Future)
- **SoraVideoProviderAdapter**: OpenAI Sora integration
- **SeedanceVideoProviderAdapter**: Seedance API integration
- **RunwayVideoProviderAdapter**: Runway Gen-2 integration
- **VeoVideoProviderAdapter**: Google Veo integration
- **PikaVideoProviderAdapter**: Pika Labs integration
- **LumaVideoProviderAdapter**: Luma integration
- **ShotstackTimelineProviderAdapter**: Shotstack rendering
- **RemotionRenderProviderAdapter**: Remotion integration
- **LocalFFmpegProviderAdapter**: Local FFmpeg rendering
- **ElevenLabsAudioProviderAdapter**: ElevenLabs audio

### Integration Strategy
1. Enable providers via environment flags
2. Add provider-specific configuration
3. Implement actual API calls
4. Add real cost tracking
5. Implement retry and error handling

## Safety Rules

### Input Validation
- Max duration: 30 seconds (configurable)
- Max inputs: 10 URLs (configurable)
- Allowed aspect ratios: 9:16, 16:9, 1:1, 4:5
- Allowed resolutions: 480p, 720p, 1080p
- Job type validation against enum

### Content Policy (Placeholder)
- Basic keyword filtering framework in place
- Future: celebrity likeness detection
- Future: copyright character blocking
- Future: misleading deepfake prevention

### Provider Safety
- No hardcoded API keys
- Live providers disabled by default
- Provider secrets never exposed to frontend
- Mock provider safe for development

## Cost Rules

### Cost Estimation Formula
```
base_cost = $0.02
duration_multiplier = max(1, duration_seconds / 10)
resolution_multiplier = {480p: 0.5, 720p: 1.0, 1080p: 2.0, 4k: 6.0}
estimated_cost = base_cost * duration_multiplier * resolution_multiplier
```

### Cost Controls
- Per-job cost estimation before creation
- User limits enforced via configuration
- Provider-specific cost tracking (future)
- Budget integration with existing AI cost controls

## Storage Rules

### Current Implementation
- In-memory job storage (v0 limitation)
- No persistent file storage
- Output URLs are placeholder
- No thumbnail generation

### Future Storage Plan
- Local file system for development
- S3/R2/Supabase for production
- CDN integration for delivery
- Signed URLs for secure access
- Automatic cleanup policies

## Frontend Behavior

### User Experience
- **Disabled State**: Clear messaging when Video OS is not enabled
- **Mock Mode**: Prominent indicators showing placeholder status
- **Progress Tracking**: Real-time job status updates
- **Error Handling**: User-friendly error messages
- **Cost Transparency**: Pre-job cost estimation

### Interface Design
- **Create Video**: Full parameter control with descriptions
- **Recent Jobs**: Status, progress, and output access
- **Info Panel**: System capabilities and limits
- **Responsive**: Works on mobile and desktop
- **Accessible**: Proper labels and keyboard navigation

## Validation Steps

### Backend Validation
```bash
python3 -m compileall lwa-backend/app
```
✅ All Python modules compile successfully

### Frontend Validation
```bash
cd lwa-web && npm run type-check && npm run build
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

## Next Implementation Gates

### Gate 1: Upload/Ingest Engine
- File upload endpoints
- Multi-file processing
- Asset normalization
- Storage integration

### Gate 2: Timeline Composer
- Real timeline building
- Track management
- Transition system
- Overlay support

### Gate 3: FFmpeg Render Engine
- Local video rendering
- Real MP4 output
- Thumbnail generation
- Format conversion

### Gate 4: Live Provider Integration
- Real API integration
- Provider selection
- Cost tracking
- Error handling

### Gate 5: Audio/Music Engine
- Audio processing
- Music generation
- Voice synthesis
- Sound effects

### Gate 6: Caption Engine
- Auto-transcription
- Styled captions
- Subtitle export
- Karaoke mode

### Gate 7: Masterpiece Mode
- One-click generation
- Multi-asset processing
- Automatic optimization
- Campaign generation

## Environment Variables

### Required for Basic Operation
```bash
LWA_VIDEO_OS_ENABLED=false          # Enable Video OS
LWA_VIDEO_PROVIDER=mock             # Provider selection
```

### Limits and Controls
```bash
LWA_VIDEO_MAX_DURATION_SECONDS=30   # Max video duration
LWA_VIDEO_MAX_INPUTS=10             # Max input URLs
LWA_VIDEO_MAX_RESOLUTION=1080p       # Max resolution
LWA_VIDEO_ALLOW_LIVE_PROVIDERS=false # Enable live providers
LWA_VIDEO_STORAGE_PROVIDER=local_placeholder
```

### Future Provider Configuration
```bash
# Sora
OPENAI_API_KEY=your_key
LWA_SORA_ENABLED=false

# Shotstack
SHOTSTACK_API_KEY=your_key
LWA_SHOTSTACK_ENABLED=false

# ElevenLabs (Audio)
ELEVENLABS_API_KEY=your_key
LWA_ELEVENLABS_ENABLED=false
```

## Development Workflow

### Local Development
1. Set `LWA_VIDEO_OS_ENABLED=true`
2. Use mock provider (default)
3. Test job creation and status tracking
4. Verify frontend behavior

### Testing Live Providers
1. Set `LWA_VIDEO_ALLOW_LIVE_PROVIDERS=true`
2. Configure provider credentials
3. Set `LWA_VIDEO_PROVIDER=<provider>`
4. Test with small jobs first

### Production Deployment
1. Enable required providers
2. Configure storage backend
3. Set appropriate limits
4. Monitor costs and usage

## Monitoring and Debugging

### Job Tracking
- All jobs stored in memory (v0)
- Job IDs use UUID4 format
- Status transitions logged
- Error messages preserved

### Cost Monitoring
- Pre-job cost estimation
- Per-job cost tracking
- Provider cost comparison
- Budget limit enforcement

### Performance Metrics
- Job creation latency
- Processing time tracking
- Provider response times
- Error rate monitoring

## Security Considerations

### Input Sanitization
- URL validation and sanitization
- Prompt length limits
- File type restrictions
- SQL injection prevention

### Provider Security
- API keys stored securely
- No keys in frontend code
- Provider request signing
- Rate limiting per provider

### Access Control
- User authentication required
- Job ownership validation
- Admin-only provider management
- Audit logging for changes

## Troubleshooting

### Common Issues
1. **Video OS Disabled**: Set `LWA_VIDEO_OS_ENABLED=true`
2. **Provider Not Configured**: Check provider settings
3. **Job Creation Fails**: Validate input parameters
4. **Frontend Errors**: Check API connectivity

### Debug Mode
- Enable detailed logging
- Check browser console
- Verify environment variables
- Test with mock provider first

### Performance Issues
- Monitor memory usage (in-memory storage)
- Check job queue length
- Verify provider response times
- Optimize database queries (future)

This v0 implementation provides a solid foundation for LWA's transformation into a comprehensive AI video studio while maintaining safety, security, and development best practices.
