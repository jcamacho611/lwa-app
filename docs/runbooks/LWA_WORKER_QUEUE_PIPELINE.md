# LWA Worker/Queue Pipeline Runbook

## Overview

This runbook verifies the worker/queue pipeline to ensure reliable background job processing, proper retry logic, and scalable architecture for long-running tasks like clip generation and rendering.

## Current Worker/Queue Truth

### Job Storage Architecture
- **Primary Storage**: In-memory job store with SQLite persistence
- **Job Store**: `JobStore` class in `lwa-backend/app/job_store.py`
- **Max Jobs**: 50 jobs in memory (configurable)
- **Concurrency**: Asyncio.Lock for thread safety
- **Persistence**: No external queue broker (Redis, RabbitMQ, etc.)

### Current Queue Implementation
- **Queue Type**: Asyncio.Queue (in-memory)
- **Workers**: Background asyncio tasks
- **Processing**: Single-process, in-memory queue
- **Persistence**: Jobs lost on restart
- **Scaling**: Limited to single process

### Job Types Supported
```python
Job Types:
- upload_processing
- transcript_generation
- ai_clip_score
- clip_generation
- render_generation
- caption_generation
- social_import
- trend_import
```

## Current Job Lifecycle

### Job Creation Flow
1. **Request Received**: API endpoint receives generation request
2. **Throttle Check**: RequestThrottle enforces rate limits
3. **Quota Check**: UsageStore validates user quotas
4. **Job Created**: JobRecord created with status "queued"
5. **Job Enqueued**: Added to asyncio.Queue for processing

### Job Processing Flow
1. **Worker Loop**: Background workers poll queue
2. **Job Dispatch**: Worker processes job based on type
3. **Status Updates**: Job status updated during processing
4. **Completion**: Job marked "completed" or "failed"
5. **Cleanup**: Job removed from processing set

### Job States
```python
Job States:
- queued: Job created, waiting for processing
- running: Job currently being processed
- waiting: Job waiting for external resource
- succeeded: Job completed successfully
- failed: Job failed with error
- cancelled: Job cancelled by user
- retrying: Job scheduled for retry
- expired: Job expired without completion
```

## Queue Provider Status

### Current Queue Implementation
- **Asyncio.Queue**: ACTIVE - In-memory queue implementation
- **Redis**: NOT IMPLEMENTED - No Redis integration
- **RabbitMQ**: NOT IMPLEMENTED - No RabbitMQ integration
- **Celery**: NOT IMPLEMENTED - No Celery integration
- **RQ**: NOT IMPLEMENTED - No Redis Queue integration
- **Dramatiq**: NOT IMPLEMENTED - No Dramatiq integration

### Queue Limitations
- **Memory Only**: Jobs lost on process restart
- **Single Process**: No cross-process job sharing
- **No Persistence**: No durable job storage
- **No Dead Letter**: No failed job handling
- **No Monitoring**: Limited queue visibility

### Worker Configuration
```python
Current Worker Setup:
- Workers: 2 background asyncio tasks
- Queue: asyncio.Queue()
- Processing Set: Set of active job IDs
- Error Handling: Basic exception catching
- Retry Logic: No automatic retry implementation
```

## Retry Policy

### Current Retry Implementation
- **Retry Logic**: NOT IMPLEMENTED - No automatic retry
- **Manual Retry**: Users can resubmit failed jobs
- **Error Classification**: Basic error logging only
- **Backoff Strategy**: No exponential backoff
- **Max Attempts**: No attempt tracking

### Documented Retry Policy (From docs/lwa-worlds-job-retry-policy.md)
```python
Default Attempts:
- render_generation: 3
- clip_generation: 3
- transcript_generation: 3
- social_import: 2
- trend_import: 2
- moderation_scan: 2
- ai_scoring: 2

Backoff Strategy:
- attempt 1: 1 minute
- attempt 2: 2 minutes
- attempt 3: 4 minutes
- capped at 30 minutes
```

### Non-Retryable Jobs
- **Payout Actions**: Financial transactions
- **Entitlement Changes**: Access modifications
- **Manual Admin Decisions**: Human decisions
- **Rights Claim Resolution**: Legal actions
- **Fraud Confirmations**: Security actions

## Failure States

### Job Failure Scenarios
1. **Processing Error**: Exception during job execution
2. **Resource Unavailable**: External service down
3. **Timeout**: Job exceeds time limit
4. **Invalid Input**: Malformed job data
5. **Permission Denied**: Access rights issues

### Error Handling
```python
Current Error Handling:
- Exception catching in worker loop
- Job status set to "failed"
- Error message stored in job record
- Basic error logging
- No automatic retry
- No dead letter queue
```

### Failure Recovery
- **Manual Retry**: User resubmits job
- **Job Cleanup**: Jobs trimmed from memory (max 50)
- **Error Logging**: Basic error information logged
- **User Notification**: Job status reflects failure

## Progress Polling

### Current Progress Tracking
- **Job Status**: Basic status field (queued, running, completed, failed)
- **Progress Percent**: NOT IMPLEMENTED - No progress tracking
- **Progress Updates**: No intermediate progress reporting
- **Real-time Updates**: No WebSocket or SSE implementation

### Job Status API
```python
Available Endpoints:
- GET /v1/jobs/{job_id}: Get job status
- GET /v1/jobs: List user jobs
- Job Status Response: Basic status and message
```

### Frontend Status States
```typescript
Frontend Job Status Types:
- queued: Job waiting to start
- running: Job currently processing
- completed: Job finished successfully
- failed: Job failed with error
- cancelled: Job cancelled by user

Progress Display:
- Progress bar: 0-100% (placeholder)
- Status badge: Visual status indicator
- Error message: Displayed when job fails
```

## Railway Deployment Concerns

### Current Railway Setup
- **Services**: frontend and backend only
- **No Worker Services**: No separate Railway worker instances
- **In-Process Processing**: All jobs run in backend process
- **Resource Limits**: Limited by Railway instance resources

### Railway Worker Requirements (From docs/lwa-railway-service-plan.md)
```text
Future Worker Services:
- lwa-worker-render: Heavy FFmpeg rendering
- lwa-worker-ingest: Source download and ingestion
- lwa-scheduler: Recurring cleanup and scheduled jobs
- lwa-webhooks: Whop webhook processing
```

### Current Limitations
- **Single Instance**: All processing in one backend instance
- **No Scaling**: Cannot scale workers independently
- **Resource Contention**: Jobs compete with API requests
- **No Isolation**: Failed jobs can affect API responsiveness

### Triggers for Worker Services
```text
lwa-worker-render Trigger:
- Render jobs block API responsiveness
- Queue wait time becomes user problem
- Multiple users generate clips concurrently
- Render failure/retry needs isolation

lwa-worker-ingest Trigger:
- Source downloading blocks backend responsiveness
- Multiple long sources queue up
- Uploads need retry isolation
```

## What Must Not Run Inside Request Time

### Long-Running Operations
- **FFmpeg Processing**: Video transcoding and rendering
- **AI Model Calls**: OpenAI API calls with timeouts
- **File Downloads**: yt-dlp source downloading
- **Batch Processing**: Multiple clip generation
- **Export Generation**: Large ZIP bundle creation

### Current Request-Time Processing
- **Strategy-Only Generation**: Fast AI responses
- **Job Creation**: Quick job record creation
- **Status Checks**: Fast database queries
- **User Authentication**: Quick token validation

### Background Processing Required
```python
Operations Needing Background Workers:
- Clip rendering (FFmpeg)
- Video transcoding
- Large file downloads
- Batch export generation
- Caption burn-in rendering
- Thumbnail generation
```

## Known Gaps

### Critical Gaps
1. **No External Queue**: Jobs lost on restart
2. **No Retry Logic**: No automatic job retry
3. **No Progress Tracking**: No real-time progress updates
4. **No Worker Scaling**: Single process limitation
5. **No Dead Letter Queue**: Failed jobs not retried

### Performance Gaps
1. **No Concurrent Processing**: Limited to single process
2. **No Resource Isolation**: Jobs compete with API
3. **No Load Balancing**: No worker distribution
4. **No Monitoring**: Limited queue visibility

### Reliability Gaps
1. **No Persistence**: Jobs lost on restart
2. **No Error Recovery**: Limited failure handling
3. **No Health Checks**: No worker health monitoring
4. **No Circuit Breaker**: No external service protection

## Next Safe Implementation PR

### Phase 1: Basic Retry Logic
```python
# Add retry configuration
RETRY_ATTEMPTS = {
    "render_generation": 3,
    "clip_generation": 3,
    "transcript_generation": 3,
    "social_import": 2,
    "trend_import": 2,
}

# Add exponential backoff
def calculate_backoff(attempt: int) -> int:
    backoff = min(2 ** attempt, 30)  # Cap at 30 minutes
    return backoff * 60  # Convert to seconds
```

### Phase 2: Progress Tracking
```python
# Add progress updates
class JobProgress:
    current_step: int
    total_steps: int
    message: str
    timestamp: str

# Add progress reporting
async def update_job_progress(job_id: str, progress: JobProgress):
    job_store.update_progress(job_id, progress)
```

### Phase 3: External Queue Integration
```python
# Add Redis queue support
import redis
from rq import Queue

redis_conn = redis.Redis()
job_queue = Queue("lwa_jobs", connection=redis_conn)

# Add durable job storage
class PersistentJobStore:
    def __init__(self, redis_conn):
        self.redis = redis_conn
        self.jobs = {}
```

### Phase 4: Worker Scaling
```python
# Add worker configuration
WORKER_CONFIG = {
    "render_workers": 2,
    "ingest_workers": 1,
    "general_workers": 2,
}

# Add worker health monitoring
class WorkerHealth:
    def __init__(self):
        self.last_heartbeat = {}
        self.worker_status = {}
```

## Implementation Priority

### High Priority (Reliability)
1. **Retry Logic**: Implement automatic job retry
2. **Progress Tracking**: Add real-time progress updates
3. **Error Classification**: Better error handling and categorization
4. **Job Persistence**: Prevent job loss on restart

### Medium Priority (Performance)
1. **External Queue**: Redis/RQ integration
2. **Worker Scaling**: Separate worker processes
3. **Load Balancing**: Distribute jobs across workers
4. **Monitoring**: Queue and worker health monitoring

### Low Priority (Enhancement)
1. **Dead Letter Queue**: Handle failed jobs
2. **Circuit Breaker**: Protect against external service failures
3. **Batch Processing**: Optimize for bulk operations
4. **Analytics**: Job performance metrics

## Monitoring and Alerting

### Key Metrics
- **Queue Length**: Number of pending jobs
- **Processing Time**: Average job duration
- **Success Rate**: Percentage of successful jobs
- **Failure Rate**: Percentage of failed jobs
- **Worker Utilization**: CPU and memory usage

### Alerting Triggers
- **Queue Backlog**: > 100 pending jobs
- **High Failure Rate**: > 10% job failure rate
- **Worker Down**: Worker not responding
- **Long Running Jobs**: Jobs exceeding timeout

### Health Checks
- **Queue Health**: Verify queue is processing
- **Worker Health**: Check worker responsiveness
- **Database Health**: Verify job store connectivity
- **Resource Health**: Monitor CPU/memory usage

## Testing Procedures

### Unit Tests
1. **Job Creation**: Test job record creation
2. **Queue Operations**: Test enqueue/dequeue
3. **Status Updates**: Test job status changes
4. **Error Handling**: Test failure scenarios

### Integration Tests
1. **End-to-End**: Test complete job lifecycle
2. **Concurrency**: Test multiple workers
3. **Failure Recovery**: Test retry logic
4. **Performance**: Test under load

### Load Tests
1. **Queue Capacity**: Test maximum job capacity
2. **Worker Scaling**: Test multiple workers
3. **Long Running Jobs**: Test timeout handling
4. **Resource Limits**: Test memory/CPU constraints

## Documentation Requirements

### Technical Documentation
- **API Documentation**: Job creation and status endpoints
- **Worker Configuration**: Worker setup and configuration
- **Queue Architecture**: Queue design and implementation
- **Troubleshooting Guide**: Common issues and solutions

### Operational Documentation
- **Monitoring Guide**: How to monitor queue health
- **Scaling Guide**: How to scale workers
- **Failure Handling**: How to handle job failures
- **Recovery Procedures**: How to recover from failures

## Conclusion

The LWA worker/queue pipeline has a basic foundation with in-memory job processing, but lacks critical reliability and scalability features for production workloads.

**Priority**: High - Implement retry logic and progress tracking
**Risk**: High - Jobs lost on restart, no automatic retry
**Timeline**: 1-2 weeks for basic reliability improvements

The current system is suitable for development and limited testing, but requires significant enhancement for production reliability and scalability.
