export type ClipStudioEventType = 
  | "clip_upload"
  | "clip_trim"
  | "effect_apply"
  | "style_transfer"
  | "export_ready"
  | "processing_started"
  | "processing_progress"
  | "processing_complete"
  | "processing_error";

export type ClipStudioEvent = {
  id: string;
  type: ClipStudioEventType;
  clipId: string;
  userId?: string;
  timestamp: number;
  payload: {
    sourceUrl?: string;
    trimStart?: number;
    trimEnd?: number;
    effectId?: string;
    styleId?: string;
    exportFormat?: string;
    progress?: number;
    stage?: string;
    resultUrl?: string;
    error?: string;
    metadata?: Record<string, any>;
  };
};

export type ClipStudioEventBridge = {
  emit: (event: ClipStudioEvent) => void;
  on: (eventType: ClipStudioEventType, handler: (event: ClipStudioEvent) => void) => () => void;
  off: (eventType: ClipStudioEventType, handler: (event: ClipStudioEvent) => void) => void;
  clear: () => void;
};

export type ClipStudioState = {
  clipId: string;
  status: "idle" | "uploading" | "processing" | "completed" | "error";
  progress: number;
  stage?: string;
  resultUrl?: string;
  error?: string;
  metadata?: Record<string, any>;
  events: ClipStudioEvent[];
};

export type ClipStudioEventHandler = (event: ClipStudioEvent) => void;
export type ClipStudioEventListener = {
  eventType: ClipStudioEventType;
  handler: ClipStudioEventHandler;
};

// Event Bridge Implementation
class ClipStudioEventBridgeImpl implements ClipStudioEventBridge {
  private listeners: Map<ClipStudioEventType, Set<ClipStudioEventHandler>> = new Map();
  private eventHistory: ClipStudioEvent[] = [];
  private maxHistorySize = 100;

  emit(event: ClipStudioEvent): void {
    // Add to history
    this.eventHistory.push(event);
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory.shift();
    }

    // Notify listeners
    const listeners = this.listeners.get(event.type);
    if (listeners) {
      listeners.forEach(handler => {
        try {
          handler(event);
        } catch (error) {
          console.error(`Error in event handler for ${event.type}:`, error);
        }
      });
    }
  }

  on(_eventType: ClipStudioEventType, handler: ClipStudioEventHandler): () => void {
    if (!this.listeners.has(_eventType)) {
      this.listeners.set(_eventType, new Set());
    }
    this.listeners.get(_eventType)!.add(handler);

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(_eventType);
      if (listeners) {
        listeners.delete(handler);
        if (listeners.size === 0) {
          this.listeners.delete(_eventType);
        }
      }
    };
  }

  off(_eventType: ClipStudioEventType, handler: ClipStudioEventHandler): void {
    const listeners = this.listeners.get(_eventType);
    if (listeners) {
      listeners.delete(handler);
      if (listeners.size === 0) {
        this.listeners.delete(_eventType);
      }
    }
  }

  clear(): void {
    this.listeners.clear();
    this.eventHistory = [];
  }

  getEventHistory(): ClipStudioEvent[] {
    return [...this.eventHistory];
  }

  getListenerCount(eventType: ClipStudioEventType): number {
    return this.listeners.get(eventType)?.size || 0;
  }
}

// State Management
export class ClipStudioStateManager {
  private states: Map<string, ClipStudioState> = new Map();
  private bridge: ClipStudioEventBridge;

  constructor(bridge: ClipStudioEventBridge) {
    this.bridge = bridge;
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    this.bridge.on("clip_upload", this.handleUploadEvent.bind(this));
    this.bridge.on("processing_started", this.handleProcessingStarted.bind(this));
    this.bridge.on("processing_progress", this.handleProgressEvent.bind(this));
    this.bridge.on("processing_complete", this.handleCompleteEvent.bind(this));
    this.bridge.on("processing_error", this.handleErrorEvent.bind(this));
  }

  private handleUploadEvent(event: ClipStudioEvent): void {
    this.updateState(event.clipId, {
      status: "uploading",
      progress: 0,
      events: [...(this.getState(event.clipId)?.events || []), event]
    });
  }

  private handleProcessingStarted(event: ClipStudioEvent): void {
    this.updateState(event.clipId, {
      status: "processing",
      progress: 0,
      stage: event.payload.stage,
      events: [...(this.getState(event.clipId)?.events || []), event]
    });
  }

  private handleProgressEvent(event: ClipStudioEvent): void {
    this.updateState(event.clipId, {
      status: "processing",
      progress: event.payload.progress || 0,
      stage: event.payload.stage,
      events: [...(this.getState(event.clipId)?.events || []), event]
    });
  }

  private handleCompleteEvent(event: ClipStudioEvent): void {
    this.updateState(event.clipId, {
      status: "completed",
      progress: 100,
      resultUrl: event.payload.resultUrl,
      metadata: event.payload.metadata,
      events: [...(this.getState(event.clipId)?.events || []), event]
    });
  }

  private handleErrorEvent(event: ClipStudioEvent): void {
    this.updateState(event.clipId, {
      status: "error",
      error: event.payload.error,
      events: [...(this.getState(event.clipId)?.events || []), event]
    });
  }

  private updateState(clipId: string, updates: Partial<ClipStudioState>): void {
    const currentState = this.getState(clipId) || {
      clipId,
      status: "idle",
      progress: 0,
      events: []
    };

    this.states.set(clipId, { ...currentState, ...updates });
  }

  getState(clipId: string): ClipStudioState | undefined {
    return this.states.get(clipId);
  }

  getAllStates(): ClipStudioState[] {
    return Array.from(this.states.values());
  }

  removeState(clipId: string): void {
    this.states.delete(clipId);
  }

  clearAllStates(): void {
    this.states.clear();
  }
}

// Event Factory Functions
export const createClipUploadEvent = (
  clipId: string,
  sourceUrl: string,
  userId?: string
): ClipStudioEvent => ({
  id: `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  type: "clip_upload",
  clipId,
  userId,
  timestamp: Date.now(),
  payload: { sourceUrl }
});

export const createClipTrimEvent = (
  clipId: string,
  trimStart: number,
  trimEnd: number,
  userId?: string
): ClipStudioEvent => ({
  id: `trim_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  type: "clip_trim",
  clipId,
  userId,
  timestamp: Date.now(),
  payload: { trimStart, trimEnd }
});

export const createEffectApplyEvent = (
  clipId: string,
  effectId: string,
  userId?: string
): ClipStudioEvent => ({
  id: `effect_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  type: "effect_apply",
  clipId,
  userId,
  timestamp: Date.now(),
  payload: { effectId }
});

export const createProcessingStartedEvent = (
  clipId: string,
  stage: string
): ClipStudioEvent => ({
  id: `started_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  type: "processing_started",
  clipId,
  timestamp: Date.now(),
  payload: { stage }
});

export const createProgressEvent = (
  clipId: string,
  progress: number,
  stage: string
): ClipStudioEvent => ({
  id: `progress_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  type: "processing_progress",
  clipId,
  timestamp: Date.now(),
  payload: { progress, stage }
});

export const createCompleteEvent = (
  clipId: string,
  resultUrl: string,
  metadata?: Record<string, any>
): ClipStudioEvent => ({
  id: `complete_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  type: "processing_complete",
  clipId,
  timestamp: Date.now(),
  payload: { resultUrl, metadata }
});

export const createErrorEvent = (
  clipId: string,
  error: string
): ClipStudioEvent => ({
  id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  type: "processing_error",
  clipId,
  timestamp: Date.now(),
  payload: { error }
});

// Singleton Instance
export const clipStudioEventBridge: ClipStudioEventBridge = new ClipStudioEventBridgeImpl();
export const clipStudioStateManager: ClipStudioStateManager = new ClipStudioStateManager(clipStudioEventBridge);

// Utility Functions
export const emitClipUpload = (clipId: string, sourceUrl: string, userId?: string): void => {
  clipStudioEventBridge.emit(createClipUploadEvent(clipId, sourceUrl, userId));
};

export const emitClipTrim = (clipId: string, trimStart: number, trimEnd: number, userId?: string): void => {
  clipStudioEventBridge.emit(createClipTrimEvent(clipId, trimStart, trimEnd, userId));
};

export const emitEffectApply = (clipId: string, effectId: string, userId?: string): void => {
  clipStudioEventBridge.emit(createEffectApplyEvent(clipId, effectId, userId));
};

export const emitProcessingStarted = (clipId: string, stage: string): void => {
  clipStudioEventBridge.emit(createProcessingStartedEvent(clipId, stage));
};

export const emitProgress = (clipId: string, progress: number, stage: string): void => {
  clipStudioEventBridge.emit(createProgressEvent(clipId, progress, stage));
};

export const emitComplete = (clipId: string, resultUrl: string, metadata?: Record<string, any>): void => {
  clipStudioEventBridge.emit(createCompleteEvent(clipId, resultUrl, metadata));
};

export const emitError = (clipId: string, error: string): void => {
  clipStudioEventBridge.emit(createErrorEvent(clipId, error));
};
