# LWA Ingest Engine v0

## Overview

LWA Ingest Engine v0 establishes the foundation for loading and normalizing diverse source assets for automated video creation. This implementation provides source asset management with metadata-only storage for v0.

## What is Implemented

### Backend Services

#### Ingest Engine Service (`lwa-backend/app/services/ingest_engine.py`)
- **Source Asset Types**: URL, video, audio, song, image, script, voice_note, podcast, multi_asset
- **Source Asset Statuses**: uploaded, processing, ready, failed, expired
- **SourceAsset Model**: Complete asset tracking with metadata, storage info, and error handling
- **SourceAssetMetadata Model**: Detailed file information (duration, dimensions, format, etc.)
- **IngestEngine Class**: Asset creation, retrieval, listing, deletion, and validation
- **URL Validation**: Basic URL format validation with filename extraction
- **Mock Processing**: Assets marked as "ready" instantly for v0 development
- **Video OS Integration**: Helper functions for creating assets from Video OS job requests

#### API Routes (`lwa-backend/app/api/routes/source_assets.py`)
- **POST /source-assets**: Create new source assets with URL or content
- **GET /source-assets/{asset_id}**: Retrieve specific asset details
- **GET /source-assets**: List user's source assets with pagination
- **DELETE /source-assets/{asset_id}**: Delete source assets
- **GET /source-assets/types**: Get available asset types and descriptions
- **GET /source-assets/stats**: Get asset statistics and storage info
- **POST /source-assets/batch**: Create multiple assets at once (max 10)

#### Configuration (`lwa-backend/app/core/config.py`)
- **Safe defaults**: Ingest engine enabled by default, local placeholder storage
- **Environment flags**: LWA_INGEST_ENGINE_ENABLED, LWA_INGEST_STORAGE_PROVIDER, limits
- **File size limits**: 100MB default max file size
- **User limits**: 50 assets per user default
- **Allowed file types**: Comprehensive list of supported formats

### Frontend Components

#### Source Assets Panel (`lwa-web/components/source-assets-panel.tsx`)
- **Asset Creation Form**: Type selection, URL input, text content input
- **Asset List Display**: Status, metadata, creation dates, error messages
- **Selection Interface**: Checkbox selection for Video OS integration
- **Type Descriptions**: Helpful descriptions for each asset type
- **Error Handling**: User-friendly error display and validation
- **Storage Indicator**: Clear "metadata only" storage notice

#### Frontend API Helpers (`lwa-web/lib/api.ts`)
- **TypeScript Interfaces**: Complete type definitions for all API responses
- **CRUD Functions**: createSourceAsset, getSourceAsset, listSourceAssets, deleteSourceAsset
- **Utility Functions**: getSourceAssetTypes, getSourceAssetStats, createSourceAssetsBatch
- **Error Handling**: Consistent error handling with existing API patterns

### Asset Types Supported

1. **URL**: External URLs to video, audio, or image content
2. **Video**: Uploaded video files (MP4, MOV, AVI, MKV)
3. **Audio**: Uploaded audio files (MP3, WAV, M4A)
4. **Song**: Music files for visualizers or soundtracks
5. **Image**: Static images for animation or backgrounds (JPG, PNG, GIF)
6. **Script**: Text scripts for video generation (TXT, MD)
7. **Voice Note**: Voice recordings for narration
8. **Podcast**: Podcast episodes for analysis or clipping
9. **Multi Asset**: Multiple assets packaged together

### Asset Statuses

- **uploaded**: Asset has been uploaded/created successfully
- **processing**: Asset is being processed (v0: instant)
- **ready**: Asset is ready for use in Video OS jobs
- **failed**: Asset processing failed with error message
- **expired**: Asset has expired and is no longer available

## What is Metadata Only

### Current Implementation
- **In-memory storage**: Assets stored in memory for v0 development
- **No file persistence**: No actual files are stored on disk
- **Metadata tracking**: All asset metadata is preserved and tracked
- **URL validation**: External URLs are validated and basic info extracted
- **Content storage**: Text content (scripts, notes) is stored in memory
- **Placeholder storage**: storage_provider set to "local_placeholder"

### Storage Behavior
- **URL assets**: URLs are validated and stored as metadata
- **Content assets**: Text content stored directly in asset object
- **File uploads**: Not implemented in v0 (future gated)
- **Binary storage**: Not implemented in v0 (future gated)

## What is Future Gated

### File Upload Integration
- **Multipart form handling**: Real file upload endpoints
- **File validation**: MIME type, size, format validation
- **Binary storage**: Actual file storage to disk/cloud
- **Thumbnail generation**: Image/video thumbnail creation
- **Metadata extraction**: EXIF, duration, dimension extraction

### Storage Provider Integration
- **Local filesystem**: Real file storage with cleanup
- **Cloud storage**: S3, R2, Supabase integration
- **CDN delivery**: Fast asset serving
- **Signed URLs**: Secure asset access
- **Cleanup policies**: Automatic asset expiration

### Advanced Processing
- **Video transcoding**: Format normalization
- **Audio processing**: Waveform extraction, beat detection
- **Image processing**: Resizing, optimization
- **Content analysis**: AI-powered content understanding
- **Duplicate detection**: Hash-based deduplication

## Video OS Integration

### Asset ID System
- **Normalized IDs**: All assets get unique asset_id identifiers
- **Cross-reference**: Video OS jobs reference assets by asset_id
- **Metadata sharing**: Asset metadata available to Video OS processing
- **Type awareness**: Video OS can filter assets by type for specific jobs

### Helper Functions
```python
# Create assets from Video OS requests
asset_ids = get_asset_ids_for_video_job(asset_requests, user_id)

# Get assets in Video OS format
assets = get_assets_for_video_job(asset_ids)
```

### Job Enhancement
- **Source tracking**: Video OS jobs know their source assets
- **Provenance**: Complete asset lineage tracking
- **Reusability**: Assets can be used across multiple jobs
- **Cost optimization**: Avoid re-processing the same assets

## Safety Rules

### Input Validation
- **URL format validation**: Regex-based URL checking
- **Content length limits**: 100KB limit for text content
- **Asset type validation**: Enum-based type checking
- **Batch size limits**: Maximum 10 assets per batch request
- **User asset limits**: Configurable per-user asset limits

### Content Policy (Placeholder)
- **Malicious URL detection**: Basic URL pattern checking
- **File type restrictions**: Configurable allowed file extensions
- **Size limits**: Configurable file size limits
- **Rate limiting**: Per-user asset creation limits (future)

### Storage Safety
- **No binary storage**: No files written to disk in v0
- **Memory-only**: Assets stored in process memory
- **Metadata isolation**: No sensitive metadata exposure
- **Cleanup on restart**: Memory cleared on process restart

## Cost Rules

### Storage Costs (Future)
- **Metadata storage**: Minimal cost for text metadata
- **File storage**: Per-GB storage costs (future)
- **Bandwidth**: CDN delivery costs (future)
- **Processing**: Transcoding and analysis costs (future)

### Current v0 Costs
- **Memory usage**: Minimal RAM usage for metadata
- **No storage costs**: No persistent storage in v0
- **No bandwidth costs**: No file serving in v0
- **No processing costs**: No transcoding in v0

## Storage Rules

### Current Implementation
- **In-memory storage**: Assets stored in Python dict
- **Provider abstraction**: storage_provider field for future integration
- **Metadata preservation**: All metadata tracked and accessible
- **URL preservation**: External URLs stored and validated
- **Content preservation**: Text content stored in memory

### Future Storage Plan
- **Local filesystem**: Configurable local directory storage
- **Cloud storage**: S3/R2/Supabase integration
- **CDN integration**: Fast global asset delivery
- **Backup policies**: Redundant storage for important assets
- **Cleanup automation**: Expired asset removal

## Frontend Behavior

### User Experience
- **Simple asset creation**: URL or text content input
- **Type guidance**: Clear descriptions for each asset type
- **Status tracking**: Real-time asset status updates
- **Selection interface**: Easy selection for Video OS integration
- **Error handling**: Clear error messages and recovery options

### Interface Design
- **Asset Creation Form**: Type selector, URL input, content textarea
- **Asset List**: Status badges, metadata display, creation dates
- **Selection Mode**: Checkbox selection for multi-asset operations
- **Storage Notice**: Clear "metadata only" storage indicator
- **Responsive Design**: Works on mobile and desktop

### Integration Points
- **Video OS Panel**: Selected assets available for video job creation
- **Asset Stats**: Usage statistics and storage information
- **Batch Operations**: Multiple asset creation and management
- **Type Filtering**: Filter assets by type for specific use cases

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

## Next Implementation Gates

### Gate 1: File Upload Support
- Multipart form handling
- Real file storage
- File validation and processing
- Thumbnail generation

### Gate 2: Storage Provider Integration
- Local filesystem storage
- Cloud storage integration
- CDN setup and configuration
- Signed URL generation

### Gate 3: Advanced Processing
- Video transcoding
- Audio processing
- Image optimization
- Content analysis

### Gate 4: Timeline Integration
- Asset-to-timeline mapping
- Automatic asset selection
- Timeline preview generation
- Asset synchronization

### Gate 5: Multi-Asset Workflows
- Asset packaging
- Batch processing
- Workflow templates
- Asset relationships

## Environment Variables

### Required for Basic Operation
```bash
LWA_INGEST_ENGINE_ENABLED=true          # Enable ingest engine
LWA_INGEST_STORAGE_PROVIDER=local_placeholder  # Storage provider
```

### Limits and Controls
```bash
LWA_INGEST_MAX_FILE_SIZE_MB=100        # Max file size
LWA_INGEST_MAX_ASSETS_PER_USER=50      # Max assets per user
LWA_INGEST_ALLOWED_FILE_TYPES=mp4,mov,avi,mkv,mp3,wav,m4a,jpg,jpeg,png,gif,txt,md
```

### Future Storage Configuration
```bash
# Local Storage
LWA_INGEST_STORAGE_PROVIDER=local
LWA_INGEST_LOCAL_STORAGE_PATH=/tmp/lwa-assets

# Cloud Storage (Future)
LWA_INGEST_STORAGE_PROVIDER=s3
LWA_INGEST_S3_BUCKET=lwa-assets
LWA_INGEST_S3_REGION=us-east-1

# CDN Configuration (Future)
LWA_INGEST_CDN_PROVIDER=cloudflare
LWA_INGEST_CDN_DOMAIN=assets.lwa.ai
```

## Development Workflow

### Local Development
1. Set `LWA_INGEST_ENGINE_ENABLED=true`
2. Use local placeholder storage (default)
3. Test asset creation with URLs and text content
4. Verify asset selection for Video OS integration

### Testing File Uploads
1. Configure local storage provider
2. Set appropriate file size limits
3. Test with various file types
4. Verify metadata extraction

### Production Deployment
1. Configure cloud storage provider
2. Set appropriate limits and quotas
3. Enable CDN for asset delivery
4. Monitor storage usage and costs

## Monitoring and Debugging

### Asset Tracking
- All assets stored in memory (v0)
- Asset IDs use UUID4 format
- Status transitions logged
- Error messages preserved

### Usage Metrics
- Asset creation and deletion rates
- Asset type distribution
- User asset counts
- Storage usage (future)

### Performance Metrics
- Asset creation latency
- List retrieval performance
- Memory usage tracking
- API response times

## Security Considerations

### Input Sanitization
- URL validation and sanitization
- Content length limits
- File type restrictions
- SQL injection prevention

### Storage Security
- No persistent file storage in v0
- Metadata-only storage approach
- Future secure file handling
- Access control implementation

### Access Control
- User authentication required
- Asset ownership validation
- Admin-only asset management
- Audit logging for changes

## Troubleshooting

### Common Issues
1. **Ingest Engine Disabled**: Set `LWA_INGEST_ENGINE_ENABLED=true`
2. **URL Validation Failed**: Check URL format and accessibility
3. **Asset Creation Failed**: Verify input format and content limits
4. **Storage Issues**: Check storage provider configuration

### Debug Mode
- Enable detailed logging
- Check browser console
- Verify environment variables
- Test with simple assets first

### Performance Issues
- Monitor memory usage (in-memory storage)
- Check asset list size
- Verify API response times
- Optimize database queries (future)

## API Examples

### Create URL Asset
```bash
curl -X POST "http://localhost:8000/api/source-assets" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "url",
    "source_url": "https://example.com/video.mp4"
  }'
```

### Create Script Asset
```bash
curl -X POST "http://localhost:8000/api/source-assets" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "script",
    "source_content": "Once upon a time..."
  }'
```

### List Assets
```bash
curl -X GET "http://localhost:8000/api/source-assets" \
  -H "Authorization: Bearer $TOKEN"
```

### Delete Asset
```bash
curl -X DELETE "http://localhost:8000/api/source-assets/{asset_id}" \
  -H "Authorization: Bearer $TOKEN"
```

## Integration Examples

### Video OS Job with Assets
```python
# Create assets first
asset_requests = [
    SourceAssetRequest(asset_type="url", source_url="https://example.com/video.mp4"),
    SourceAssetRequest(asset_type="script", source_content="Script content...")
]

# Get asset IDs for Video OS
asset_ids = get_asset_ids_for_video_job(asset_requests, user_id)

# Create Video OS job with assets
video_request = VideoJobRequest(
    job_type=VideoJobType.VIDEO_TO_VIDEO,
    source_asset_ids=asset_ids,
    # ... other parameters
)
```

This v0 implementation provides a solid foundation for LWA to accept diverse source assets while maintaining safety and preparing for future file storage and processing capabilities.
