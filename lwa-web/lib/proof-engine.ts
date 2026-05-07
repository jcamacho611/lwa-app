export type ProofEventType = 
  | "clip_generated"
  | "content_scored"
  | "render_completed"
  | "job_created"
  | "job_completed"
  | "transaction_processed"
  | "user_action"
  | "system_event"
  | "error_occurred"
  | "recovery_triggered";

export type ProofEvent = {
  id: string;
  type: ProofEventType;
  userId?: string;
  sessionId?: string;
  timestamp: number;
  data: Record<string, any>;
  metadata?: {
    ip?: string;
    userAgent?: string;
    platform?: string;
    version?: string;
    environment?: string;
  };
  relatedIds?: {
    jobId?: string;
    transactionId?: string;
    clipId?: string;
    campaignId?: string;
  };
  severity: "low" | "medium" | "high" | "critical";
  category: "user" | "system" | "business" | "security";
  retention: number; // milliseconds
  archived: boolean;
};

export type ProofRecord = {
  id: string;
  userId: string;
  type: "clip" | "job" | "transaction" | "campaign" | "audit";
  title: string;
  description: string;
  content: {
    original?: any;
    processed?: any;
    result?: any;
    metadata?: Record<string, any>;
  };
  evidence: {
    screenshots?: string[];
    logs?: string[];
    documents?: string[];
    media?: string[];
  };
  verification: {
    verified: boolean;
    verifiedAt?: number;
    verifiedBy?: string;
    method: "manual" | "automated" | "blockchain";
    hash?: string;
    signature?: string;
  };
  status: "draft" | "verified" | "disputed" | "archived";
  createdAt: number;
  updatedAt: number;
  expiresAt?: number;
  accessLevel: "public" | "private" | "restricted";
  tags: string[];
};

export type HistoryEntry = {
  id: string;
  userId: string;
  action: string;
  objectType: string;
  objectId: string;
  previousState?: any;
  newState?: any;
  timestamp: number;
  context: {
    source: "web" | "api" | "mobile" | "system";
    sessionId?: string;
    ip?: string;
    userAgent?: string;
  };
  metadata?: Record<string, any>;
};

export type AuditTrail = {
  id: string;
  scope: "user" | "system" | "data" | "security";
  action: string;
  actorId: string;
  actorType: "user" | "system" | "admin";
  targetId?: string;
  targetType?: string;
  timestamp: number;
  details: Record<string, any>;
  outcome: "success" | "failure" | "partial";
  riskLevel: "low" | "medium" | "high" | "critical";
  compliance: boolean;
  retention: number;
};

export type DataRetention = {
  id: string;
  dataType: string;
  userId?: string;
  retentionPeriod: number;
  autoDelete: boolean;
  archiveAfter: number;
  compliance: {
    gdpr: boolean;
    ccpa: boolean;
    hipaa: boolean;
    other: string[];
  };
  createdAt: number;
  lastAccessed: number;
  accessCount: number;
};

export type ProofConfig = {
  defaultRetention: number;
  maxRetention: number;
  archiveThreshold: number;
  verificationRequired: boolean;
  blockchainEnabled: boolean;
  complianceStandards: string[];
  storageLocations: string[];
  encryptionEnabled: boolean;
};

// Proof Engine Implementation
export class ProofEngine {
  private events: Map<string, ProofEvent> = new Map();
  private records: Map<string, ProofRecord> = new Map();
  private history: Map<string, HistoryEntry[]> = new Map();
  private auditTrails: Map<string, AuditTrail> = new Map();
  private dataRetentions: Map<string, DataRetention> = new Map();
  private config: ProofConfig;
  private eventCallbacks: Map<string, (event: ProofSystemEvent) => void> = new Map();

  constructor(config?: Partial<ProofConfig>) {
    this.config = {
      defaultRetention: 90 * 24 * 60 * 60 * 1000, // 90 days
      maxRetention: 365 * 24 * 60 * 60 * 1000, // 1 year
      archiveThreshold: 30 * 24 * 60 * 60 * 1000, // 30 days
      verificationRequired: false,
      blockchainEnabled: false,
      complianceStandards: ["GDPR", "CCPA"],
      storageLocations: ["primary", "backup", "archive"],
      encryptionEnabled: true,
      ...config,
    };

    this.initializeMockData();
  }

  private initializeMockData(): void {
    // Initialize mock data retention policies
    const retentionPolicies: DataRetention[] = [
      {
        id: "retention_clip_data",
        dataType: "clip",
        retentionPeriod: 90 * 24 * 60 * 60 * 1000, // 90 days
        autoDelete: true,
        archiveAfter: 30 * 24 * 60 * 60 * 1000, // 30 days
        compliance: {
          gdpr: true,
          ccpa: true,
          hipaa: false,
          other: [],
        },
        createdAt: Date.now(),
        lastAccessed: Date.now(),
        accessCount: 0,
      },
      {
        id: "retention_transaction_data",
        dataType: "transaction",
        retentionPeriod: 365 * 24 * 60 * 60 * 1000, // 1 year
        autoDelete: false,
        archiveAfter: 180 * 24 * 60 * 60 * 1000, // 6 months
        compliance: {
          gdpr: true,
          ccpa: true,
          hipaa: false,
          other: ["FINRA"],
        },
        createdAt: Date.now(),
        lastAccessed: Date.now(),
        accessCount: 0,
      },
    ];

    retentionPolicies.forEach(policy => {
      this.dataRetentions.set(policy.id, policy);
    });
  }

  // Event Management
  createEvent(
    type: ProofEventType,
    data: Record<string, any>,
    options?: {
      userId?: string;
      sessionId?: string;
      severity?: "low" | "medium" | "high" | "critical";
      category?: "user" | "system" | "business" | "security";
      relatedIds?: ProofEvent["relatedIds"];
      metadata?: ProofEvent["metadata"];
      retention?: number;
    }
  ): string {
    const eventId = `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const event: ProofEvent = {
      id: eventId,
      type,
      userId: options?.userId,
      sessionId: options?.sessionId,
      timestamp: Date.now(),
      data,
      metadata: options?.metadata,
      relatedIds: options?.relatedIds,
      severity: options?.severity || "medium",
      category: options?.category || "user",
      retention: options?.retention || this.config.defaultRetention,
      archived: false,
    };

    this.events.set(eventId, event);
    this.notifyEvent({ type: "event_created", data: event });
    return eventId;
  }

  getEvent(eventId: string): ProofEvent | undefined {
    return this.events.get(eventId);
  }

  getEventsByUser(userId: string): ProofEvent[] {
    return Array.from(this.events.values()).filter(event => event.userId === userId);
  }

  getEventsByType(type: ProofEventType): ProofEvent[] {
    return Array.from(this.events.values()).filter(event => event.type === type);
  }

  getEventsByTimeRange(start: number, end: number): ProofEvent[] {
    return Array.from(this.events.values()).filter(event => 
      event.timestamp >= start && event.timestamp <= end
    );
  }

  getAllEvents(): ProofEvent[] {
    return Array.from(this.events.values());
  }

  // Proof Record Management
  createProofRecord(
    userId: string,
    type: "clip" | "job" | "transaction" | "campaign" | "audit",
    title: string,
    description: string,
    content: ProofRecord["content"],
    evidence?: ProofRecord["evidence"],
    options?: {
      accessLevel?: "public" | "private" | "restricted";
      tags?: string[];
      expiresAt?: number;
    }
  ): string {
    const recordId = `proof_${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const record: ProofRecord = {
      id: recordId,
      userId,
      type,
      title,
      description,
      content,
      evidence: evidence || { screenshots: [], logs: [], documents: [], media: [] },
      verification: {
        verified: false,
        method: this.config.verificationRequired ? "manual" : "automated",
      },
      status: "draft",
      createdAt: Date.now(),
      updatedAt: Date.now(),
      expiresAt: options?.expiresAt,
      accessLevel: options?.accessLevel || "private",
      tags: options?.tags || [],
    };

    this.records.set(recordId, record);
    this.notifyEvent({ type: "record_created", data: record });
    return recordId;
  }

  getProofRecord(recordId: string): ProofRecord | undefined {
    return this.records.get(recordId);
  }

  getProofRecordsByUser(userId: string): ProofRecord[] {
    return Array.from(this.records.values()).filter(record => record.userId === userId);
  }

  getProofRecordsByType(type: ProofRecord["type"]): ProofRecord[] {
    return Array.from(this.records.values()).filter(record => record.type === type);
  }

  verifyProofRecord(recordId: string, verifiedBy: string, method: "manual" | "automated" | "blockchain" = "manual"): boolean {
    const record = this.getProofRecord(recordId);
    if (!record) return false;

    record.verification = {
      verified: true,
      verifiedAt: Date.now(),
      verifiedBy,
      method,
      hash: this.generateHash(record),
    };

    record.status = "verified";
    record.updatedAt = Date.now();

    this.records.set(recordId, record);
    this.notifyEvent({ type: "record_verified", data: record });
    return true;
  }

  private generateHash(record: ProofRecord): string {
    // Simple hash generation - in production, use proper cryptographic hash
    const content = JSON.stringify(record.content);
    return `hash_${Date.now()}_${content.length}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // History Management
  recordHistory(
    userId: string,
    action: string,
    objectType: string,
    objectId: string,
    previousState?: any,
    newState?: any,
    context?: HistoryEntry["context"],
    metadata?: Record<string, any>
  ): string {
    const historyId = `hist_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const entry: HistoryEntry = {
      id: historyId,
      userId,
      action,
      objectType,
      objectId,
      previousState,
      newState,
      timestamp: Date.now(),
      context: context || { source: "web" },
      metadata,
    };

    // Store by user
    if (!this.history.has(userId)) {
      this.history.set(userId, []);
    }
    this.history.get(userId)!.push(entry);

    // Keep only last 1000 entries per user
    const userHistory = this.history.get(userId)!;
    if (userHistory.length > 1000) {
      this.history.set(userId, userHistory.slice(-1000));
    }

    this.notifyEvent({ type: "history_recorded", data: entry });
    return historyId;
  }

  getUserHistory(userId: string, limit?: number): HistoryEntry[] {
    const userHistory = this.history.get(userId) || [];
    return limit ? userHistory.slice(-limit) : userHistory;
  }

  getObjectHistory(objectType: string, objectId: string): HistoryEntry[] {
    const allHistory: HistoryEntry[] = [];
    this.history.forEach(entries => {
      allHistory.push(...entries.filter(entry => 
        entry.objectType === objectType && entry.objectId === objectId
      ));
    });
    return allHistory.sort((a, b) => b.timestamp - a.timestamp);
  }

  // Audit Trail Management
  createAuditTrail(
    scope: "user" | "system" | "data" | "security",
    action: string,
    actorId: string,
    actorType: "user" | "system" | "admin",
    details: Record<string, any>,
    options?: {
      targetId?: string;
      targetType?: string;
      outcome?: "success" | "failure" | "partial";
      riskLevel?: "low" | "medium" | "high" | "critical";
      compliance?: boolean;
      retention?: number;
    }
  ): string {
    const auditId = `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const audit: AuditTrail = {
      id: auditId,
      scope,
      action,
      actorId,
      actorType,
      targetId: options?.targetId,
      targetType: options?.targetType,
      timestamp: Date.now(),
      details,
      outcome: options?.outcome || "success",
      riskLevel: options?.riskLevel || "low",
      compliance: options?.compliance ?? true,
      retention: options?.retention || this.config.maxRetention,
    };

    this.auditTrails.set(auditId, audit);
    this.notifyEvent({ type: "audit_created", data: audit });
    return auditId;
  }

  getAuditTrails(scope?: string, actorId?: string): AuditTrail[] {
    return Array.from(this.auditTrails.values()).filter(audit => {
      if (scope && audit.scope !== scope) return false;
      if (actorId && audit.actorId !== actorId) return false;
      return true;
    });
  }

  // Data Retention Management
  setDataRetentionPolicy(
    dataType: string,
    retentionPeriod: number,
    autoDelete: boolean,
    archiveAfter: number,
    compliance: DataRetention["compliance"],
    userId?: string
  ): string {
    const policyId = `retention_${dataType}_${userId || "global"}_${Date.now()}`;
    const policy: DataRetention = {
      id: policyId,
      dataType,
      userId,
      retentionPeriod,
      autoDelete,
      archiveAfter,
      compliance,
      createdAt: Date.now(),
      lastAccessed: Date.now(),
      accessCount: 0,
    };

    this.dataRetentions.set(policyId, policy);
    this.notifyEvent({ type: "retention_policy_set", data: policy });
    return policyId;
  }

  getDataRetentionPolicy(dataType: string, userId?: string): DataRetention | undefined {
    return Array.from(this.dataRetentions.values()).find(policy => 
      policy.dataType === dataType && (!userId || policy.userId === userId)
    );
  }

  // Cleanup and Maintenance
  cleanupExpiredData(): {
    eventsDeleted: number;
    recordsDeleted: number;
    historyEntriesDeleted: number;
    auditTrailsDeleted: number;
  } {
    const now = Date.now();
    let eventsDeleted = 0;
    let recordsDeleted = 0;
    let historyEntriesDeleted = 0;
    let auditTrailsDeleted = 0;

    // Clean up expired events
    this.events.forEach((event, eventId) => {
      if (now - event.timestamp > event.retention) {
        this.events.delete(eventId);
        eventsDeleted++;
      }
    });

    // Clean up expired records
    this.records.forEach((record, recordId) => {
      if (record.expiresAt && now > record.expiresAt) {
        this.records.delete(recordId);
        recordsDeleted++;
      }
    });

    // Clean up old audit trails
    this.auditTrails.forEach((audit, auditId) => {
      if (now - audit.timestamp > audit.retention) {
        this.auditTrails.delete(auditId);
        auditTrailsDeleted++;
      }
    });

    // Clean up old history entries (keep last 1000 per user)
    this.history.forEach((entries, userId) => {
      if (entries.length > 1000) {
        const deleted = entries.length - 1000;
        this.history.set(userId, entries.slice(-1000));
        historyEntriesDeleted += deleted;
      }
    });

    this.notifyEvent({ 
      type: "cleanup_completed", 
      data: { eventsDeleted, recordsDeleted, historyEntriesDeleted, auditTrailsDeleted }
    });

    return { eventsDeleted, recordsDeleted, historyEntriesDeleted, auditTrailsDeleted };
  }

  // Search and Query
  searchProofRecords(criteria: {
    userId?: string;
    type?: ProofRecord["type"];
    status?: ProofRecord["status"];
    tags?: string[];
    dateFrom?: number;
    dateTo?: number;
    accessLevel?: ProofRecord["accessLevel"];
  }): ProofRecord[] {
    return Array.from(this.records.values()).filter(record => {
      if (criteria.userId && record.userId !== criteria.userId) return false;
      if (criteria.type && record.type !== criteria.type) return false;
      if (criteria.status && record.status !== criteria.status) return false;
      if (criteria.tags && !criteria.tags.every(tag => record.tags.includes(tag))) return false;
      if (criteria.dateFrom && record.createdAt < criteria.dateFrom) return false;
      if (criteria.dateTo && record.createdAt > criteria.dateTo) return false;
      if (criteria.accessLevel && record.accessLevel !== criteria.accessLevel) return false;
      return true;
    });
  }

  // Analytics and Statistics
  getProofStatistics(): {
    totalEvents: number;
    totalRecords: number;
    totalHistoryEntries: number;
    totalAuditTrails: number;
    eventsByType: Record<ProofEventType, number>;
    eventsBySeverity: Record<string, number>;
    recordsByType: Record<ProofRecord["type"], number>;
    recordsByStatus: Record<ProofRecord["status"], number>;
    verifiedRecords: number;
    archivedRecords: number;
    complianceScore: number;
  } {
    const events = this.getAllEvents();
    const records = Array.from(this.records.values());
    const auditTrails = Array.from(this.auditTrails.values());

    const eventsByType = events.reduce((acc, event) => {
      acc[event.type] = (acc[event.type] || 0) + 1;
      return acc;
    }, {} as Record<ProofEventType, number>);

    const eventsBySeverity = events.reduce((acc, event) => {
      acc[event.severity] = (acc[event.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const recordsByType = records.reduce((acc, record) => {
      acc[record.type] = (acc[record.type] || 0) + 1;
      return acc;
    }, {} as Record<ProofRecord["type"], number>);

    const recordsByStatus = records.reduce((acc, record) => {
      acc[record.status] = (acc[record.status] || 0) + 1;
      return acc;
    }, {} as Record<ProofRecord["status"], number>);

    const verifiedRecords = records.filter(record => record.verification.verified).length;
    const archivedRecords = records.filter(record => record.status === "archived").length;

    const totalHistoryEntries = Array.from(this.history.values()).reduce((sum, entries) => sum + entries.length, 0);

    // Simple compliance score based on verification and audit compliance
    const complianceScore = auditTrails.length > 0
      ? (auditTrails.filter(audit => audit.compliance).length / auditTrails.length) * 100
      : 0;

    return {
      totalEvents: events.length,
      totalRecords: records.length,
      totalHistoryEntries,
      totalAuditTrails: auditTrails.length,
      eventsByType,
      eventsBySeverity,
      recordsByType,
      recordsByStatus,
      verifiedRecords,
      archivedRecords,
      complianceScore,
    };
  }

  // Event Management
  onEvent(eventType: string, callback: (event: ProofSystemEvent) => void): () => void {
    const callbackId = `${eventType}_${Date.now()}`;
    this.eventCallbacks.set(callbackId, callback);
    return () => {
      this.eventCallbacks.delete(callbackId);
    };
  }

  private notifyEvent(event: ProofSystemEvent): void {
    this.eventCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error("Error in proof event callback:", error);
      }
    });
  }
}

// Types
export type ProofSystemEvent = {
  type: string;
  data: any;
  timestamp?: number;
};

// Singleton Instance
export const proofEngine = new ProofEngine();
