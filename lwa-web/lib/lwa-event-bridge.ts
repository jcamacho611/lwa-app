export type LwaEventType = 
  | "clip_generated"
  | "clip_saved"
  | "proof_saved"
  | "campaign_exported"
  | "lee_wuh_asset_selected"
  | "recovery_action_selected"
  | "signal_sprint_completed";

export interface LwaEvent {
  id: string;
  type: LwaEventType;
  timestamp: number;
  data: Record<string, any>;
  source: string;
  metadata?: Record<string, any>;
}

export interface LwaEventSummary {
  total: number;
  byType: Record<LwaEventType, number>;
  bySource: Record<string, number>;
  recent: {
    lastHour: number;
    lastDay: number;
  };
}

export interface LwaEventBridgeConfig {
  maxQueueSize: number;
  eventExpiration: number; // milliseconds
  enableDebug: boolean;
}

// Event Queue Implementation
class LwaEventQueue {
  private events: LwaEvent[] = [];
  private config: LwaEventBridgeConfig;
  private listeners: Map<string, (event: LwaEvent) => void> = new Map();

  constructor(config?: Partial<LwaEventBridgeConfig>) {
    this.config = {
      maxQueueSize: 1000,
      eventExpiration: 24 * 60 * 60 * 1000, // 24 hours
      enableDebug: false,
      ...config,
    };
  }

  add(event: LwaEvent): boolean {
    // Validate event type
    if (!this.isValidEventType(event.type)) {
      if (this.config.enableDebug) {
        console.warn(`Invalid event type: ${event.type}`);
      }
      return false;
    }

    // Check queue size limit
    if (this.events.length >= this.config.maxQueueSize) {
      // Remove oldest event
      this.events.shift();
      if (this.config.enableDebug) {
        console.warn('Event queue full, removed oldest event');
      }
    }

    // Add timestamp if not provided
    if (!event.timestamp) {
      event.timestamp = Date.now();
    }

    // Add event to queue
    this.events.push(event);

    // Notify listeners
    this.notifyListeners(event);

    if (this.config.enableDebug) {
      console.log(`Event added: ${event.type}`, event);
    }

    return true;
  }

  getAll(): LwaEvent[] {
    return [...this.events];
  }

  getByType(type: LwaEventType): LwaEvent[] {
    return this.events.filter(event => event.type === type);
  }

  getBySource(source: string): LwaEvent[] {
    return this.events.filter(event => event.source === source);
  }

  getRecent(count: number = 10): LwaEvent[] {
    return this.events.slice(-count);
  }

  clear(): void {
    this.events = [];
    if (this.config.enableDebug) {
      console.log('Event queue cleared');
    }
  }

  cleanup(): number {
    const now = Date.now();
    const initialCount = this.events.length;
    
    // Remove expired events
    this.events = this.events.filter(event => 
      now - event.timestamp < this.config.eventExpiration
    );

    const removedCount = initialCount - this.events.length;
    
    if (this.config.enableDebug && removedCount > 0) {
      console.log(`Cleaned up ${removedCount} expired events`);
    }

    return removedCount;
  }

  getSummary(): LwaEventSummary {
    const now = Date.now();
    const oneHourAgo = now - (60 * 60 * 1000);
    const oneDayAgo = now - (24 * 60 * 60 * 1000);

    const summary: LwaEventSummary = {
      total: this.events.length,
      byType: {} as Record<LwaEventType, number>,
      bySource: {} as Record<string, number>,
      recent: {
        lastHour: 0,
        lastDay: 0,
      },
    };

    // Initialize type counters
    const eventTypes: LwaEventType[] = [
      "clip_generated",
      "clip_saved", 
      "proof_saved",
      "campaign_exported",
      "lee_wuh_asset_selected",
      "recovery_action_selected",
      "signal_sprint_completed"
    ];

    eventTypes.forEach(type => {
      summary.byType[type] = 0;
    });

    // Calculate summary
    this.events.forEach(event => {
      // Count by type
      summary.byType[event.type]++;
      
      // Count by source
      if (event.source) {
        summary.bySource[event.source] = (summary.bySource[event.source] || 0) + 1;
      }

      // Count recent events
      if (event.timestamp >= oneHourAgo) {
        summary.recent.lastHour++;
      }
      if (event.timestamp >= oneDayAgo) {
        summary.recent.lastDay++;
      }
    });

    return summary;
  }

  subscribe(listener: (event: LwaEvent) => void): () => void {
    const id = Math.random().toString(36);
    this.listeners.set(id, listener);
    
    return () => {
      this.listeners.delete(id);
    };
  }

  private isValidEventType(type: string): type is LwaEventType {
    const validTypes: LwaEventType[] = [
      "clip_generated",
      "clip_saved",
      "proof_saved", 
      "campaign_exported",
      "lee_wuh_asset_selected",
      "recovery_action_selected",
      "signal_sprint_completed"
    ];
    
    return validTypes.includes(type as LwaEventType);
  }

  private notifyListeners(event: LwaEvent): void {
    this.listeners.forEach(listener => {
      try {
        listener(event);
      } catch (error) {
        console.error('Error in event listener:', error);
      }
    });
  }
}

// Global event queue instance
const eventQueue = new LwaEventQueue();

// Event Emitter Functions
export function emitLwaEvent(event: Omit<LwaEvent, 'id' | 'timestamp'>): boolean {
  const fullEvent: LwaEvent = {
    id: generateEventId(),
    timestamp: Date.now(),
    ...event,
  };

  return eventQueue.add(fullEvent);
}

export function getLwaEventQueue(): LwaEvent[] {
  return eventQueue.getAll();
}

export function clearLwaEventQueue(): void {
  eventQueue.clear();
}

export function summarizeLwaEvents(): LwaEventSummary {
  return eventQueue.getSummary();
}

export function cleanupLwaEvents(): number {
  return eventQueue.cleanup();
}

import { useState, useEffect } from 'react';

// React Hook
export function useLwaEvents() {
  const [events, setEvents] = useState<LwaEvent[]>([]);
  const [summary, setSummary] = useState<LwaEventSummary>(eventQueue.getSummary());

  useEffect(() => {
    // Initial load
    setEvents(eventQueue.getAll());
    setSummary(eventQueue.getSummary());

    // Subscribe to new events
    const unsubscribe = eventQueue.subscribe((event) => {
      setEvents(eventQueue.getAll());
      setSummary(eventQueue.getSummary());
    });

    // Cleanup subscription
    return unsubscribe;
  }, []);

  return {
    events,
    summary,
    emit: emitLwaEvent,
    clear: clearLwaEventQueue,
    cleanup: cleanupLwaEvents,
  };
}

// Helper Functions
function generateEventId(): string {
  return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Event Factory Functions
export function createClipGeneratedEvent(data: {
  clipId: string;
  url: string;
  duration?: number;
  metadata?: Record<string, any>;
}, source: string = 'unknown'): Omit<LwaEvent, 'id' | 'timestamp'> {
  return {
    type: 'clip_generated',
    data,
    source,
  };
}

export function createClipSavedEvent(data: {
  clipId: string;
  userId: string;
  location: string;
}, source: string = 'unknown'): Omit<LwaEvent, 'id' | 'timestamp'> {
  return {
    type: 'clip_saved',
    data,
    source,
  };
}

export function createProofSavedEvent(data: {
  proofId: string;
  type: string;
  userId: string;
}, source: string = 'unknown'): Omit<LwaEvent, 'id' | 'timestamp'> {
  return {
    type: 'proof_saved',
    data,
    source,
  };
}

export function createCampaignExportedEvent(data: {
  campaignId: string;
  format: string;
  userId: string;
}, source: string = 'unknown'): Omit<LwaEvent, 'id' | 'timestamp'> {
  return {
    type: 'campaign_exported',
    data,
    source,
  };
}

export function createLeeWuhAssetSelectedEvent(data: {
  assetId: string;
  assetType: string;
  realm?: string;
}, source: string = 'unknown'): Omit<LwaEvent, 'id' | 'timestamp'> {
  return {
    type: 'lee_wuh_asset_selected',
    data,
    source,
  };
}

export function createRecoveryActionSelectedEvent(data: {
  action: string;
  targetId: string;
  outcome: string;
}, source: string = 'unknown'): Omit<LwaEvent, 'id' | 'timestamp'> {
  return {
    type: 'recovery_action_selected',
    data,
    source,
  };
}

export function createSignalSprintCompletedEvent(data: {
  sprintId: string;
  score: number;
  rank: number;
  userId: string;
}, source: string = 'unknown'): Omit<LwaEvent, 'id' | 'timestamp'> {
  return {
    type: 'signal_sprint_completed',
    data,
    source,
  };
}

// Export the event queue for advanced usage
export { eventQueue as lwaEventQueue };
