# LWA Event Bridge

## Purpose

The LWA Event Bridge provides a frontend-safe, typed event system that allows Clip Studio and Lee-Wuh systems to emit local product events without backend dependency. This enables real-time event coordination between different parts of the LWA frontend while maintaining type safety and avoiding backend coupling.

## Architecture

### Core Components

1. **Event Types** - Strongly typed event definitions for all LWA system events
2. **Event Queue** - In-memory queue for storing and managing events
3. **Event Emitter** - Safe event emission with type validation
4. **Event Processor** - Event aggregation and summary generation
5. **React Integration** - Hooks and components for frontend consumption

### Event Types

The event bridge supports the following event types:

- `clip_generated` - When a new clip is created by the creator engine
- `clip_saved` - When a clip is saved to user storage
- `proof_saved` - When proof/history data is recorded
- `campaign_exported` - When campaign data is exported
- `lee_wuh_asset_selected` - When a Lee-Wuh asset is chosen
- `recovery_action_selected` - When a recovery action is triggered
- `signal_sprint_completed` - When a signal sprint finishes

### Event Flow

```
[Component] → emitLwaEvent() → Event Queue → React Hooks → UI Updates
```

## Implementation Strategy

### Frontend-First Design

- **No backend dependency**: All events are processed locally
- **Type safety**: Full TypeScript support for all event types
- **Memory management**: Configurable queue size and cleanup
- **Performance**: Efficient event processing and aggregation

### Safety Considerations

- **Event validation**: Type checking before queue insertion
- **Memory limits**: Configurable maximum queue size
- **Cleanup**: Automatic event expiration and cleanup
- **Error handling**: Graceful failure handling

## Integration Points

### Clip Studio Integration

```typescript
// Clip Studio emits events
emitLwaEvent({
  type: 'clip_generated',
  data: { clipId, url, metadata }
});
```

### Lee-Wuh Integration

```typescript
// Lee-Wuh systems emit events
emitLwaEvent({
  type: 'lee_wuh_asset_selected',
  data: { assetId, assetType, realm }
});
```

### Recovery Engine Integration

```typescript
// Recovery engine emits events
emitLwaEvent({
  type: 'recovery_action_selected',
  data: { action, targetId, outcome }
});
```

## Technical Requirements

### Event Structure

```typescript
interface LwaEvent {
  id: string;
  type: LwaEventType;
  timestamp: number;
  data: Record<string, any>;
  source: string;
  metadata?: Record<string, any>;
}
```

### Queue Management

- **Maximum size**: 1000 events (configurable)
- **Expiration**: 24 hours (configurable)
- **Cleanup**: Automatic removal of expired events

### Performance Targets

- **Event emission**: < 1ms
- **Queue processing**: < 10ms for 100 events
- **Summary generation**: < 5ms
- **Memory usage**: < 10MB for full queue

## Future Extensions

### Backend Integration (Phase 2)

- **Event persistence**: Store events in backend database
- **Real-time sync**: WebSocket-based event synchronization
- **Analytics**: Event tracking and analysis
- **Cross-tab sync**: Event synchronization between browser tabs

### Advanced Features

- **Event filtering**: Client-side event filtering and routing
- **Event replay**: Event history and replay capabilities
- **Event aggregation**: Advanced event aggregation and analytics
- **Event debugging**: Enhanced debugging and monitoring tools

## Usage Examples

### Basic Event Emission

```typescript
import { emitLwaEvent } from '@/lib/lwa-event-bridge';

// Emit a clip generated event
emitLwaEvent({
  type: 'clip_generated',
  data: {
    clipId: 'clip_123',
    url: 'https://cdn.example.com/clip.mp4',
    duration: 30,
    metadata: { platform: 'tiktok' }
  }
});
```

### React Component Integration

```typescript
import { useLwaEvents } from '@/lib/lwa-event-bridge';

function EventDashboard() {
  const { events, summary } = useLwaEvents();
  
  return (
    <div>
      <h2>Recent Events: {summary.total}</h2>
      <ul>
        {events.map(event => (
          <li key={event.id}>{event.type}</li>
        ))}
      </ul>
    </div>
  );
}
```

## Security Considerations

### Data Protection

- **No sensitive data**: Events should not contain sensitive user information
- **Local storage**: All events are stored locally in memory
- **Cleanup**: Automatic cleanup prevents data accumulation

### Access Control

- **Event validation**: Type checking prevents invalid events
- **Source tracking**: All events are tagged with their source
- **Audit trail**: Event history provides audit capabilities

## Monitoring and Debugging

### Event Metrics

- **Event counts**: Track event frequency by type
- **Performance metrics**: Monitor event processing performance
- **Error tracking**: Track and log event errors

### Debugging Tools

- **Event inspector**: View all events in the queue
- **Event replay**: Replay events for debugging
- **Performance profiling**: Profile event processing performance

## Deployment Notes

### Frontend Deployment

- **No backend changes**: Event bridge is frontend-only
- **Bundle size**: Minimal impact on bundle size
- **Performance**: No impact on initial load performance

### Configuration

- **Environment variables**: No environment variables required
- **Feature flags**: Event bridge can be feature-flagged
- **Fallback**: Graceful degradation if event bridge fails
