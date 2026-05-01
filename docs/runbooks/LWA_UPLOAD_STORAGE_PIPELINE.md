# LWA Upload/Storage Pipeline Runbook

## Overview

This runbook verifies the upload, storage, and export pipeline to ensure reliable file handling, proper storage provider integration, and adequate retention policies for production workloads.

## Current Upload/Source Ingest Flow

### Backend Upload Endpoint
- **Route**: `POST /v1/uploads` in `lwa-backend/app/api/routes/upload.py`
- **Authentication**: Optional (guest or authenticated users)
- **File Types**: Video, audio, and image files only
- **Storage**: Local filesystem with user-specific directories
- **Response**: Upload record with public URL and metadata

### Upload Processing Logic
1. **File Validation**: Check file extension and MIME type
2. **User Identification**: Resolve guest or authenticated user ID
3. **Quota Enforcement**: Daily upload limits per user plan
4. **File Storage**: Save to user-specific directory with UUID filename
5. **Database Record**: Create upload record in platform store
6. **Public URL**: Generate accessible URL for file access

### Supported File Types
```python
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga", ".flac"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
```

## Current Clip Export/Download Flow

### Export Bundle Service
- **Service**: `lwa-backend/app/services/export_bundle.py`
- **Output**: ZIP bundles with clips and metadata
- **Storage**: Local filesystem in generated assets directory
- **Artifacts**: JSON packages, captions, subtitles, media files

### Export Processing Logic
1. **Bundle Creation**: Generate unique bundle ID and directory
2. **Clip Processing**: Extract metadata and create per-clip artifacts
3. **Media Handling**: Copy local media files to bundle
4. **ZIP Generation**: Create compressed bundle file
5. **URL Generation**: Generate public download URL

### Download URL Resolution
```python
def build_download_url(clip):
    return (
        clip.get("download_url")
        or clip.get("edited_clip_url")
        or clip.get("preview_url")
        or clip.get("clip_url")
        or clip.get("raw_clip_url")
        or ""
    )
```

## Storage Provider Status

### Current Storage Architecture
- **Primary**: Local filesystem storage
- **Uploads**: `/uploads/{user_id}/` directory structure
- **Generated**: `/generated/` directory for processed assets
- **Database**: SQLite for metadata and tracking
- **Public Access**: Direct file serving via web server

### Storage Provider Analysis
- **S3**: NOT IMPLEMENTED - No AWS S3 integration found
- **R2**: NOT IMPLEMENTED - No Cloudflare R2 integration found
- **Supabase**: NOT IMPLEMENTED - No Supabase storage integration found
- **Local**: ACTIVE - Filesystem-based storage in use

### Storage Paths
```bash
# Uploads
/uploads/{user_id}/{uuid_filename}

# Generated Assets
/generated/export-bundles/{request_id}/{bundle_id}/
/generated/clips/
/generated/thumbnails/

# Railway Volume Mount
/data/lwa-uploads/
/data/lwa-generated/
```

## Required Environment Variables

### Upload Configuration
```bash
# Upload Directory
LWA_UPLOADS_DIR=/data/lwa-uploads

# File Size Limits
MAX_UPLOAD_MB=500

# Railway Volume Mount
RAILWAY_VOLUME_MOUNT_PATH=/data
```

### Generated Assets Configuration
```bash
# Generated Assets Directory
LWA_GENERATED_ASSETS_DIR=/data/lwa-generated

# Retention Policy
LWA_GENERATED_ASSETS_RETENTION_HOURS=24
LWA_GENERATED_ASSETS_MAX_FILES=300
LWA_ASSET_CLEANUP_ON_STARTUP=true

# Cleanup Interval
LWA_GENERATED_ASSET_PRUNE_INTERVAL_SECONDS=1800
```

### Database Paths
```bash
# Platform Database
LWA_PLATFORM_DB_PATH=/data/lwa-platform.sqlite3

# Usage Store
LWA_USAGE_STORE_PATH=/data/lwa-usage.json

# Event Log
LWA_EVENT_LOG_PATH=/data/lwa-events.jsonl
LWA_EVENT_LOG_ENABLED=true
LWA_EVENT_LOG_MAX_BYTES=10485760
```

## Object Naming Convention Proposal

### Current Naming Scheme
```bash
# Upload Files
{user_id}/{uuid12}{extension}

# Generated Assets
export-bundles/{request_id}/{bundle_id}/
clips/{clip_id}/
media/{clip_id}_{type}{extension}

# Bundle Files
{safe_title}-{bundle_id[-8:]}.zip
```

### Recommended Naming Convention
```bash
# Upload Files
uploads/{user_type}/{user_id}/{YYYY-MM-DD}/{uuid12}{extension}

# Generated Assets
generated/{asset_type}/{request_id}/{clip_id}/{filename}

# Export Bundles
exports/{request_id}/{bundle_id}/{safe_title}-{bundle_id[-8:]}.zip

# Metadata
metadata/{asset_type}/{id}/{filename}
```

## Signed URL Rules

### Current URL Strategy
- **Public URLs**: Direct file serving via web server
- **No Signed URLs**: NOT IMPLEMENTED
- **Access Control**: Basic authentication only
- **URL Format**: `/uploads/{user_id}/{filename}`

### Security Implications
- **No Expiration**: URLs remain valid indefinitely
- **No Access Control**: Anyone with URL can access files
- **No Rate Limiting**: No protection against URL abuse
- **No Revocation**: Cannot revoke access once URL is shared

### Recommended Signed URL Implementation
```python
# Future Implementation
def generate_signed_url(file_path, expires_in=3600):
    token = generate_access_token(file_path, expires_in)
    return f"/files/{file_path}?token={token}&expires={timestamp}"
```

## Retention/Deletion Policy

### Current Retention Behavior
- **Generated Assets**: 24 hours retention (configurable)
- **Max Files**: 300 files limit (configurable)
- **Cleanup**: Automatic pruning every 30 minutes
- **Uploads**: NO RETENTION POLICY - Files persist indefinitely

### Deletion Process
```python
# Generated Assets Cleanup
def cleanup_generated_assets():
    - Delete files older than retention_hours
    - Delete oldest files if max_files exceeded
    - Run on startup and every 30 minutes
```

### Missing Retention Policies
- **Upload Files**: NO AUTOMATIC DELETION
- **User Data**: NO GDPR compliance cleanup
- **Failed Jobs**: NO cleanup of orphaned files
- **Temp Files**: NO systematic temp file cleanup

## File Size Limits

### Current Limits
```bash
# Upload Size Limit
MAX_UPLOAD_MB=500  # 500MB per file

# Plan-based Upload Limits
Free: 2 uploads/day
Pro: 25 uploads/day
Scale: 100 uploads/day
```

### Clip Generation Limits
```bash
# Clip Count Limits
Free: 3 clips/job
Pro: 6 clips/job
Scale: 12 clips/job

# High Volume Mode
LWA_ENABLE_HIGH_VOLUME_CLIPS=false
LWA_HIGH_VOLUME_MAX_CLIPS=24
```

### Storage Quotas
- **No User Storage Quotas**: Unlimited storage per user
- **No Global Storage Limits**: Only file count limits
- **No Bandwidth Limits**: Unlimited download bandwidth

## Moderation Hook Points

### Current Moderation Integration
- **Upload Validation**: Basic file type checking only
- **Content Scanning**: NOT IMPLEMENTED
- **Manual Review**: No moderation queue integration
- **Automated Detection**: No AI content analysis

### Missing Moderation Features
- **Content Classification**: No inappropriate content detection
- **Copyright Detection**: No duplicate or copyrighted content checking
- **User Reporting**: No user-based content reporting
- **Automated Flagging**: No automated moderation systems

### Recommended Moderation Integration
```python
# Future Implementation
def moderate_upload(file_path, user_id):
    - Scan for inappropriate content
    - Check copyright violations
    - Flag for manual review if needed
    - Block or quarantine suspicious files
```

## Failure States

### Upload Failure Scenarios
1. **File Size Exceeded**: 413 HTTP error
2. **Unsupported Type**: 400 HTTP error
3. **Quota Exceeded**: 402 HTTP error
4. **Storage Full**: 500 HTTP error
5. **Network Timeout**: Connection error

### Export Failure Scenarios
1. **Missing Files**: Partial bundle creation
2. **Disk Full**: ZIP creation failure
3. **Permission Denied**: File access errors
4. **Memory Limit**: Large bundle processing failure

### Recovery Mechanisms
- **Upload Quota Release**: Automatic quota release on failure
- **Partial Cleanup**: Cleanup of orphaned files
- **Retry Logic**: Limited retry for transient failures
- **Error Logging**: Comprehensive error tracking

## Railway Storage Risks

### Railway Volume Mount Issues
- **Ephemeral Storage**: Volume data persists across restarts
- **Size Limits**: Railway volume size limitations
- **Performance**: I/O performance constraints
- **Backup**: No automatic backup mechanism

### Identified Risks
1. **Single Point of Failure**: All storage on single Railway instance
2. **No Redundancy**: No backup or disaster recovery
3. **Scalability Limits**: Limited by single instance storage
4. **Data Loss Risk**: Volume corruption or deletion

### Mitigation Strategies
- **External Storage**: Implement S3/R2 for redundancy
- **Backup Strategy**: Regular backup to external storage
- **Monitoring**: Storage usage monitoring and alerts
- **Cleanup Policies**: Aggressive cleanup to prevent overflow

## What Must Not Be Claimed Publicly

### Storage Capabilities
- ❌ "Cloud storage" - Only local filesystem storage
- ❌ "Unlimited storage" - Limited by Railway volume size
- ❌ "Automatic backup" - No backup mechanism implemented
- ❌ "CDN distribution" - No CDN integration

### Security Features
- ❌ "Secure file sharing" - No signed URLs or access control
- ❌ "Content moderation" - No content scanning implemented
- ❌ "GDPR compliant" - No data retention policies
- ❌ "Enterprise security" - Basic authentication only

### Performance Claims
- ❌ "High-performance storage" - Limited by Railway I/O
- ❌ "Global CDN" - No CDN distribution
- ❌ "Instant uploads" - Limited by network and processing

### Accurate Claims
- ✅ "File upload support" - Basic upload functionality works
- ✅ "Multiple file types" - Video, audio, image support
- ✅ "User quotas" - Daily upload limits enforced
- ✅ "Export bundles" - ZIP bundle generation works

## Verified Working Pieces

### Upload System
- ✅ **File Upload**: POST /v1/uploads endpoint functional
- ✅ **File Validation**: Extension and MIME type checking
- ✅ **User Authentication**: Guest and authenticated user support
- ✅ **Quota Enforcement**: Daily upload limits per plan
- ✅ **Database Storage**: Upload metadata stored correctly

### Export System
- ✅ **Bundle Generation**: ZIP bundle creation works
- ✅ **Metadata Export**: JSON packages with clip data
- ✅ **Subtitle Generation**: SRT and VTT subtitle files
- ✅ **Media Inclusion**: Local media files included in bundles
- ✅ **URL Generation**: Public URLs for downloads

### Storage Management
- ✅ **Directory Structure**: Organized file storage
- ✅ **Generated Assets**: Automatic cleanup of old files
- ✅ **Configuration**: Environment variable configuration
- ✅ **Error Handling**: Basic error handling and logging

## Unknowns/Gaps

### Critical Gaps
1. **External Storage**: No S3/R2/Supabase integration
2. **Signed URLs**: No secure URL generation
3. **Content Moderation**: No content scanning or moderation
4. **Backup Strategy**: No backup or disaster recovery
5. **GDPR Compliance**: No data retention or deletion policies

### Performance Gaps
1. **CDN Integration**: No content distribution network
2. **Compression**: No file compression for storage
3. **Caching**: No caching layer for frequently accessed files
4. **Parallel Processing**: No parallel upload/download handling

### Security Gaps
1. **Access Control**: No fine-grained permission system
2. **Audit Logging**: No comprehensive audit trail
3. **Rate Limiting**: No protection against abuse
4. **Data Encryption**: No encryption at rest or in transit

## Next Safe Implementation PR

### Phase 1: Storage Provider Integration
```bash
# Add S3/R2 support
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=lwa-assets
```

### Phase 2: Signed URL Implementation
```python
# Add secure URL generation
def generate_signed_url(file_path, expires_in=3600):
    token = create_access_token(file_path, expires_in)
    return f"/files/{file_path}?token={token}"
```

### Phase 3: Content Moderation
```python
# Add content scanning
def moderate_content(file_path, user_id):
    result = scan_content(file_path)
    if result.flagged:
        queue_for_review(user_id, file_path)
    return result
```

### Phase 4: Backup Strategy
```python
# Add backup automation
def backup_to_external_storage():
    sync_to_s3(local_path, s3_path)
    verify_backup_integrity()
```

## Implementation Priority

### High Priority (Production Readiness)
1. **External Storage**: S3/R2 integration for redundancy
2. **Signed URLs**: Secure file access control
3. **Backup Strategy**: Automated backup system
4. **Retention Policies**: GDPR-compliant data cleanup

### Medium Priority (Performance)
1. **CDN Integration**: Content distribution network
2. **Compression**: File compression for storage efficiency
3. **Caching**: Multi-layer caching strategy
4. **Parallel Processing**: Concurrent upload/download

### Low Priority (Enhancement)
1. **Content Moderation**: AI-powered content scanning
2. **Advanced Analytics**: Storage usage analytics
3. **Multi-region**: Geographic distribution
4. **Advanced Security**: Encryption and audit logging

## Monitoring and Alerting

### Key Metrics
- **Storage Usage**: Total storage consumption per user
- **Upload Success Rate**: Percentage of successful uploads
- **Export Success Rate**: Percentage of successful exports
- **Cleanup Efficiency**: Storage reclaimed by cleanup process

### Alerting Triggers
- **Storage Full**: < 10% free space remaining
- **Upload Failures**: > 5% upload failure rate
- **Export Failures**: > 5% export failure rate
- **Cleanup Failures**: Cleanup process failures

### Health Checks
- **Storage Accessibility**: Verify storage mounts are accessible
- **Database Connectivity**: Verify SQLite databases are functional
- **Disk Space**: Monitor available disk space
- **File Integrity**: Verify file integrity after upload

## Testing Procedures

### Manual Testing
1. **Upload Testing**: Test various file types and sizes
2. **Export Testing**: Test bundle generation with different clip counts
3. **Cleanup Testing**: Verify cleanup process works correctly
4. **Failure Testing**: Test error handling and recovery

### Automated Testing
1. **Unit Tests**: Test upload and export functions
2. **Integration Tests**: Test end-to-end workflows
3. **Load Tests**: Test performance under high load
4. **Security Tests**: Test access controls and permissions

## Documentation Requirements

### Technical Documentation
- **API Documentation**: Document upload and export endpoints
- **Configuration Guide**: Document environment variables
- **Storage Architecture**: Document storage layout and conventions
- **Troubleshooting Guide**: Document common issues and solutions

### User Documentation
- **Upload Guide**: How to upload files and supported formats
- **Export Guide**: How to export and download content
- **Storage Limits**: Document quotas and limitations
- **Security Guide**: Best practices for file sharing

## Conclusion

The LWA upload/storage pipeline has a solid foundation with basic functionality working correctly. However, critical gaps exist in storage redundancy, security, and compliance that must be addressed for production readiness.

**Priority**: High - Implement external storage and security features
**Risk**: Medium - Core functionality works, but lacks enterprise features
**Timeline**: 2-3 weeks for critical storage and security improvements

The current system is suitable for development and limited production use, but requires significant enhancement for enterprise-grade reliability and security.
