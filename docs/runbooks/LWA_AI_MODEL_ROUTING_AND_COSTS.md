# LWA AI Model Routing and Cost Runbook

## Overview

This runbook verifies the AI model routing, transcription services, and cost control mechanisms to ensure efficient resource usage, proper fallback behavior, and predictable cost management for AI-powered features.

## Current Transcription Truth

### Transcription Provider Status
- **Whisper**: NOT IMPLEMENTED - No OpenAI Whisper integration found
- **AssemblyAI**: NOT IMPLEMENTED - No AssemblyAI integration found
- **Deepgram**: NOT IMPLEMENTED - No Deepgram integration found
- **Custom Transcription**: NOT IMPLEMENTED - No custom transcription service

### Current Transcription Flow
- **Transcript Processing**: MISSING - No active transcription pipeline
- **Audio Processing**: No audio-to-text conversion pipeline
- **Transcript Storage**: No transcript persistence mechanism
- **Transcript Usage**: No transcript integration in clip generation

### Transcription Gaps
- **No Transcription Service**: No audio/video transcription capability
- **No Transcript Storage**: No database for transcript persistence
- **No Transcript Integration**: No usage in clip generation workflow
- **No Transcription Cost Tracking**: No cost monitoring for transcription

## Current LLM/Model Usage Truth

### Anthropic Integration
- **Status**: ACTIVE - Anthropic service implemented
- **Models Available**:
  - `claude-opus-4-7` (Opus) - Premium reasoning model
  - `claude-sonnet-4-6` (Sonnet) - Balanced performance model
  - `claude-haiku-4-5-20251001` (Haiku) - Fast, cost-effective model
- **Service File**: `lwa-backend/app/services/anthropic_service.py`

### OpenAI Integration
- **Status**: CONFIGURED - OpenAI API key configured but not actively used
- **Model**: `gpt-4.1-mini` - Configured but no implementation found
- **Service Integration**: MISSING - No OpenAI service implementation found

### Model Usage Patterns
```python
Current Model Routing:
- Clip Packaging: Sonnet (default) or Opus (premium reasoning)
- Metadata Classification: Haiku (fast, cost-effective)
- Auto Editor Brain: MISSING IMPLEMENTATION
- Director Brain: Algorithm-based, no LLM usage
```

## Provider Status

### Active Providers
- **Anthropic**: ACTIVE - Full integration with three model tiers
- **OpenAI**: CONFIGURED - API key available but not used
- **Seedance**: OPTIONAL - External service with fallback support

### Missing Providers
- **Whisper**: NOT IMPLEMENTED - No transcription service
- **AssemblyAI**: NOT IMPLEMENTED - No transcription alternative
- **Deepgram**: NOT IMPLEMENTED - No transcription alternative
- **Custom LLM**: NOT IMPLEMENTED - No in-house models

### Provider Configuration
```python
Anthropic Models:
- Opus: claude-opus-4-7 (premium reasoning)
- Sonnet: claude-sonnet-4-6 (balanced performance)
- Haiku: claude-haiku-4-5-20251001 (fast/cost-effective)

OpenAI Models:
- GPT-4.1-mini: Configured but unused

External Services:
- Seedance: Optional external AI service
- Visual Engine: Optional visual generation service
```

## Required Environment Variables

### Anthropic Configuration
```bash
# Anthropic AI Services
LWA_ENABLE_ANTHROPIC=true
ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL_OPUS=claude-opus-4-7
ANTHROPIC_MODEL_SONNET=claude-sonnet-4-6
ANTHROPIC_MODEL_HAIKU=claude-haiku-4-5-20251001
LWA_PREMIUM_REASONING_PROVIDER=anthropic
```

### OpenAI Configuration
```bash
# OpenAI Services (configured but unused)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
```

### External Services
```bash
# Seedance (optional)
SEEDANCE_ENABLED=false
SEEDANCE_API_KEY=your_seedance_api_key
SEEDANCE_BASE_URL=https://api.seedance.com
SEEDANCE_MODEL=seedance-2.0
SEEDANCE_TIMEOUT_SECONDS=180

# Visual Engine (optional)
LWA_VISUAL_GENERATION_ENABLED=true
LWA_VISUAL_GENERATION_MODEL=lwa-visual-v1
LWA_VISUAL_GENERATION_TIMEOUT_SECONDS=180
LWA_VISUAL_ENGINE_API_KEY=your_visual_engine_api_key
LWA_VISUAL_ENGINE_API_BASE_URL=https://api.visual-engine.com
```

### AI Provider Selection
```bash
# Primary AI Provider
LWA_AI_PROVIDER=auto
AI_PROVIDER=auto
```

## Model Routing Strategy

### Current Routing Logic
```python
Model Selection Rules:
- Premium Reasoning: Opus (claude-opus-4-7)
- Standard Packaging: Sonnet (claude-sonnet-4-6)
- Fast Classification: Haiku (claude-haiku-4-5-20251001)
- Fallback: Strategy-only (no AI cost)
```

### Model Usage Patterns
- **Clip Packaging**: Anthropic Sonnet by default, Opus for premium reasoning
- **Metadata Classification**: Anthropic Haiku for fast, cost-effective processing
- **Content Generation**: No active content generation workflows
- **Analysis Tasks**: No active analysis workflows using LLMs

### Routing Decision Factors
- **Cost Considerations**: Haiku for cheap/fast operations
- **Quality Requirements**: Opus for premium reasoning tasks
- **Speed Requirements**: Haiku for real-time responses
- **Fallback Strategy**: Strategy-only when AI unavailable

## Cheap/Fast Model vs Premium Model Decision Rules

### Current Decision Framework
```python
Model Selection Criteria:
- Haiku (Fast/Cheap):
  * Metadata classification
  * Simple text processing
  * Real-time requirements
  * Cost-sensitive operations

- Sonnet (Balanced):
  * Standard clip packaging
  * General content analysis
  * Moderate complexity tasks
  * Default choice for most operations

- Opus (Premium):
  * Premium reasoning flag enabled
  * Complex analysis requirements
  * High-quality output needed
  * User-paid premium features
```

### Cost Optimization Strategy
- **Default to Cheaper**: Use Haiku when possible
- **Premium Upsell**: Opus for paid/premium features
- **Fallback Protection**: Strategy-only when AI costs too high
- **Batch Processing**: Use cheaper models for bulk operations

### Quality vs Cost Trade-offs
- **Speed Priority**: Haiku (fastest, cheapest)
- **Balance Priority**: Sonnet (moderate cost, good quality)
- **Quality Priority**: Opus (highest cost, best quality)
- **Cost Priority**: Strategy-only (no AI cost)

## Prompt Caching Plan

### Current Caching Status
- **Prompt Caching**: NOT IMPLEMENTED - No prompt caching mechanism
- **Response Caching**: NOT IMPLEMENTED - No response caching
- **Model Caching**: NOT IMPLEMENTED - No model state caching

### Caching Opportunities
```python
Potential Caching Strategies:
- System Prompt Caching: Cache frequently used system prompts
- Template Caching: Cache prompt templates for reuse
- Response Caching: Cache responses for identical inputs
- Model State Caching: Cache model initialization state
```

### Caching Implementation Needs
- **Cache Storage**: Redis or in-memory cache for prompts/responses
- **Cache Keys**: Deterministic keys for cache hits
- **Cache TTL**: Time-based expiration for cached content
- **Cache Invalidation**: Mechanism to clear stale cache entries

## Batch API Plan

### Current Batch Status
- **Batch Processing**: NOT IMPLEMENTED - No batch API usage
- **Parallel Processing**: Limited to single requests
- **Bulk Operations**: No bulk AI processing capabilities

### Batch Processing Opportunities
```python
Potential Batch Operations:
- Bulk Clip Packaging: Process multiple clips in single API call
- Batch Classification: Classify multiple items together
- Parallel Model Calls: Use multiple models simultaneously
- Batch Transcription: Process multiple audio files together
```

### Batch Implementation Needs
- **Batch API Integration**: Use Anthropic/OpenAI batch endpoints
- **Job Queuing**: Queue system for batch operations
- **Error Handling**: Partial failure handling for batch jobs
- **Cost Tracking**: Per-item cost tracking in batch operations

## Fallback Behavior

### Current Fallback Strategy
```python
Fallback Hierarchy:
1. Anthropic Models: Opus → Sonnet → Haiku
2. External Services: Seedance (if enabled)
3. Strategy-Only: No AI cost, algorithmic approach
4. Error Response: Graceful degradation with error messages
```

### Fallback Triggers
- **API Key Missing**: Fall to strategy-only
- **API Rate Limits**: Switch to cheaper model or strategy-only
- **Model Unavailable**: Try alternative model or fallback
- **Cost Limits**: Enforce cost controls, fall to strategy-only
- **Service Outage**: Fall to strategy-only or cached responses

### Fallback Implementation
```python
Current Fallback Logic:
- Anthropic Available: Use configured Anthropic models
- Anthropic Unavailable: Check Seedance if enabled
- All AI Unavailable: Use strategy-only approach
- Cost Limits Exceeded: Block AI usage, suggest upgrade
```

## Cost Controls

### Current Cost Management
- **Cost Tracking**: NOT IMPLEMENTED - No cost monitoring
- **Budget Limits**: NOT IMPLEMENTED - No budget enforcement
- **Usage Monitoring**: Basic daily usage limits only
- **Cost Alerts**: NOT IMPLEMENTED - No cost alerting

### Cost Control Gaps
```python
Missing Cost Controls:
- Per-User Cost Limits: No individual user cost tracking
- Model Cost Awareness: No cost-per-request tracking
- Budget Enforcement: No spending limits
- Cost Optimization: No automatic cost optimization
```

### Cost Control Implementation Needs
- **Cost Tracking**: Track costs per user, per model, per operation
- **Budget Limits**: Enforce user and system-wide spending limits
- **Cost Alerts**: Notify users and admins of cost thresholds
- **Cost Optimization**: Automatically choose cheapest viable model

## User Credit Implications

### Current Credit System
- **Credit Tracking**: Basic daily usage limits
- **Plan Integration**: Credits tied to user plans (free/pro/scale)
- **Usage Enforcement**: Daily quota enforcement
- **Credit Costs**: NOT IMPLEMENTED - No credit cost for AI usage

### Credit Cost Gaps
```python
Missing Credit Costs:
- AI Usage Costs: No credit deduction for AI operations
- Model-Specific Costs: Different costs for different models
- Premium Features: No extra cost for premium models
- Cost Transparency: Users can't see AI operation costs
```

### Credit System Enhancements Needed
- **AI Cost Integration**: Deduct credits for AI operations
- **Model Pricing**: Different credit costs for different models
- **Premium Upsell**: Charge extra for premium model usage
- **Cost Visibility**: Show users cost breakdown per operation

## Unknowns/Gaps

### Critical Unknowns
1. **Transcription Service**: No transcription provider integration
2. **Cost Tracking**: No cost monitoring or budget enforcement
3. **Prompt Caching**: No caching mechanism for prompts/responses
4. **Batch Processing**: No batch API usage for efficiency
5. **OpenAI Usage**: API key configured but not used

### Performance Gaps
1. **Model Selection**: No intelligent model routing based on content
2. **Cost Optimization**: No automatic cost optimization
3. **Response Caching**: No response caching for repeated queries
4. **Parallel Processing**: No parallel model usage

### Reliability Gaps
1. **Service Monitoring**: No AI service health monitoring
2. **Error Recovery**: Limited error handling and recovery
3. **Rate Limiting**: No API rate limit handling
4. **Service Redundancy**: No backup AI providers

## Next Safe Implementation PR

### Phase 1: Cost Tracking Integration
```python
# Add cost tracking to AI operations
class CostTracker:
    def track_model_usage(self, model: str, tokens: int, user_id: str):
        cost = self.calculate_cost(model, tokens)
        self.deduct_user_credits(user_id, cost)
        self.log_cost_event(user_id, model, cost)

# Add cost per model
MODEL_COSTS = {
    "claude-opus-4-7": 0.015,  # per 1k tokens
    "claude-sonnet-4-6": 0.003,  # per 1k tokens
    "claude-haiku-4-5-20251001": 0.00025,  # per 1k tokens
}
```

### Phase 2: Transcription Service Integration
```python
# Add transcription service
class TranscriptionService:
    def transcribe_audio(self, audio_file: str, provider: str = "whisper"):
        if provider == "whisper":
            return self.whisper_transcribe(audio_file)
        elif provider == "assembly":
            return self.assembly_transcribe(audio_file)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
```

### Phase 3: Prompt Caching
```python
# Add prompt caching
class PromptCache:
    def get_cached_response(self, prompt_hash: str) -> Optional[str]:
        return self.cache.get(prompt_hash)
    
    def cache_response(self, prompt_hash: str, response: str, ttl: int = 3600):
        self.cache.set(prompt_hash, response, ttl)
```

### Phase 4: Batch Processing
```python
# Add batch processing
class BatchProcessor:
    def process_batch_clips(self, clips: List[ClipData], model: str = "haiku"):
        return self.batch_api_call(clips, model)
```

## Implementation Priority

### High Priority (Cost Control)
1. **Cost Tracking**: Implement cost monitoring and credit deduction
2. **Budget Enforcement**: Add spending limits and alerts
3. **Model Cost Awareness**: Show users costs per operation
4. **Premium Model Upsell**: Charge extra for premium features

### Medium Priority (Performance)
1. **Prompt Caching**: Cache frequently used prompts and responses
2. **Batch Processing**: Implement batch API usage
3. **Intelligent Routing**: Smart model selection based on content
4. **Response Caching**: Cache responses for repeated queries

### Low Priority (Enhancement)
1. **Transcription Service**: Add audio/video transcription
2. **OpenAI Integration**: Use configured OpenAI models
3. **Advanced Analytics**: Cost optimization analytics
4. **Service Monitoring**: AI service health monitoring

## Monitoring and Alerting

### Key Metrics
- **AI Usage**: Number of AI requests per user/model
- **Cost Tracking**: Total costs per user/model/operation
- **Model Performance**: Response times and success rates
- **Credit Usage**: Credit consumption and remaining balances

### Alerting Triggers
- **Cost Thresholds**: Alert when user costs exceed limits
- **Budget Overruns**: Alert when system budgets exceeded
- **Service Failures**: Alert when AI services are unavailable
- **Unusual Usage**: Alert on abnormal usage patterns

### Health Checks
- **API Key Validation**: Verify API keys are valid
- **Model Availability**: Check if models are accessible
- **Cost Service Health**: Verify cost tracking is working
- **Credit System Health**: Check credit system functionality

## Testing Procedures

### Unit Tests
1. **Model Selection**: Test model routing logic
2. **Cost Calculation**: Test cost tracking accuracy
3. **Fallback Behavior**: Test fallback mechanisms
4. **Credit Deduction**: Test credit system integration

### Integration Tests
1. **End-to-End AI Flow**: Test complete AI operation workflow
2. **Cost Control**: Test budget enforcement and alerts
3. **Service Failures**: Test behavior when services are unavailable
4. **Multi-User Scenarios**: Test cost tracking across users

### Load Tests
1. **Concurrent AI Requests**: Test multiple simultaneous requests
2. **Cost Under Load**: Test cost tracking under high usage
3. **Fallback Performance**: Test fallback behavior under stress
4. **Credit System Load**: Test credit system under high usage

## Documentation Requirements

### Technical Documentation
- **API Documentation**: AI service endpoints and usage
- **Model Guide**: Model capabilities and use cases
- **Cost Guide**: Cost structure and budget management
- **Troubleshooting Guide**: Common AI service issues

### User Documentation
- **AI Features Guide**: How to use AI-powered features
- **Cost Transparency**: How AI usage affects credits
- **Model Comparison**: Differences between AI models
- **Upgrade Guide**: How to access premium features

## Conclusion

The LWA AI model routing and cost system has a solid foundation with Anthropic integration, but lacks critical cost control, transcription services, and optimization features for production scalability.

**Priority**: High - Implement cost tracking and budget enforcement
**Risk**: High - No cost control, unlimited AI spending possible
**Timeline**: 1-2 weeks for basic cost control implementation

The current system is suitable for development with limited AI usage, but requires significant enhancement for production cost management and feature completeness.
