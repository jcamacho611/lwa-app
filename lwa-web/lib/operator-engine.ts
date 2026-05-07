export type AdminRole = 
  | "super_admin"
  | "admin"
  | "moderator"
  | "support"
  | "analyst"
  | "operator";

export type AdminPermission = 
  | "user_management"
  | "content_moderation"
  | "financial_control"
  | "system_config"
  | "analytics_view"
  | "campaign_management"
  | "safety_enforcement"
  | "compliance_audit"
  | "emergency_override";

export type AdminAction = 
  | "user_ban"
  | "user_suspend"
  | "content_remove"
  | "content_approve"
  | "transaction_refund"
  | "campaign_approve"
  | "system_maintenance"
  | "emergency_shutdown"
  | "config_update";

export type AdminUser = {
  id: string;
  userId: string;
  role: AdminRole;
  permissions: AdminPermission[];
  status: "active" | "suspended" | "inactive";
  assignedAreas: string[];
  lastLogin: number;
  sessionExpiry: number;
  twoFactorEnabled: boolean;
  ipWhitelist: string[];
  activityLog: AdminActivity[];
  createdAt: number;
  updatedAt: number;
};

export type AdminActivity = {
  id: string;
  adminId: string;
  action: AdminAction;
  targetId?: string;
  targetType?: string;
  details: Record<string, any>;
  ipAddress: string;
  userAgent: string;
  timestamp: number;
  outcome: "success" | "failure" | "partial";
  notes?: string;
};

export type SystemMetric = {
  id: string;
  name: string;
  category: "performance" | "usage" | "business" | "technical" | "security";
  value: number;
  unit: string;
  threshold: {
    warning: number;
    critical: number;
  };
  status: "normal" | "warning" | "critical";
  trend: "up" | "down" | "stable";
  history: MetricDataPoint[];
  lastUpdated: number;
};

export type MetricDataPoint = {
  timestamp: number;
  value: number;
};

export type SystemAlert = {
  id: string;
  type: "error" | "warning" | "info" | "critical";
  category: "system" | "security" | "performance" | "business" | "compliance";
  title: string;
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  source: string;
  affectedSystems: string[];
  metrics: string[];
  status: "active" | "acknowledged" | "resolved" | "dismissed";
  assignedTo?: string;
  acknowledgedBy?: string;
  acknowledgedAt?: number;
  resolvedBy?: string;
  resolvedAt?: number;
  resolution?: string;
  createdAt: number;
  updatedAt: number;
};

export type ModerationQueue = {
  id: string;
  type: "content" | "user" | "transaction" | "campaign";
  items: ModerationItem[];
  assignees: string[];
  sla: number; // hours
  priority: "low" | "medium" | "high" | "urgent";
  autoApproveThreshold: number;
};

export type ModerationItem = {
  id: string;
  type: "content" | "user" | "transaction" | "campaign";
  targetId: string;
  targetType: string;
  reason: string;
  severity: "low" | "medium" | "high" | "critical";
  evidence: Record<string, any>;
  reporter?: string;
  status: "pending" | "reviewing" | "approved" | "rejected" | "escalated";
  assignedTo?: string;
  reviewedBy?: string;
  reviewedAt?: number;
  decision?: string;
  notes?: string;
  createdAt: number;
  updatedAt: number;
};

export type SystemConfig = {
  id: string;
  category: string;
  key: string;
  value: any;
  type: "string" | "number" | "boolean" | "object" | "array";
  description: string;
  sensitive: boolean;
  requiresRestart: boolean;
  lastModifiedBy?: string;
  lastModifiedAt?: number;
  version: number;
};

export type OperatorConfig = {
  enableTwoFactor: boolean;
  enableIPWhitelist: boolean;
  sessionTimeout: number;
  auditRetention: number;
  alertThresholds: Record<string, number>;
  autoEscalation: boolean;
  emergencyContacts: string[];
  maintenanceWindows: MaintenanceWindow[];
  backupFrequency: number;
  complianceChecks: boolean;
};

export type MaintenanceWindow = {
  id: string;
  scheduledAt: number;
  duration: number;
  description: string;
  systems: string[];
  status: "scheduled" | "in_progress" | "completed" | "cancelled";
  approvedBy?: string;
  performedBy?: string;
  notes?: string;
};

// Operator Engine Implementation
export class OperatorEngine {
  private adminUsers: Map<string, AdminUser> = new Map();
  private activities: Map<string, AdminActivity> = new Map();
  private metrics: Map<string, SystemMetric> = new Map();
  private alerts: Map<string, SystemAlert> = new Map();
  private moderationQueues: Map<string, ModerationQueue> = new Map();
  private configs: Map<string, SystemConfig> = new Map();
  private config: OperatorConfig;
  private eventCallbacks: Map<string, (event: OperatorEvent) => void> = new Map();

  constructor(config?: Partial<OperatorConfig>) {
    this.config = {
      enableTwoFactor: true,
      enableIPWhitelist: false,
      sessionTimeout: 8 * 60 * 60 * 1000, // 8 hours
      auditRetention: 365 * 24 * 60 * 60 * 1000, // 1 year
      alertThresholds: {
        error_rate: 0.05,
        response_time: 2000,
        cpu_usage: 0.8,
        memory_usage: 0.85,
        disk_usage: 0.9,
      },
      autoEscalation: true,
      emergencyContacts: [],
      maintenanceWindows: [],
      backupFrequency: 24 * 60 * 60 * 1000, // 24 hours
      complianceChecks: true,
      ...config,
    };

    this.initializeSystem();
  }

  private initializeSystem(): void {
    // Initialize admin users
    this.createAdminUser("admin_1", "super_admin", [
      "user_management",
      "content_moderation",
      "financial_control",
      "system_config",
      "analytics_view",
      "campaign_management",
      "safety_enforcement",
      "compliance_audit",
      "emergency_override",
    ]);

    // Initialize system metrics
    this.initializeMetrics();

    // Initialize moderation queues
    this.initializeModerationQueues();

    // Initialize system configs
    this.initializeConfigs();
  }

  private initializeMetrics(): void {
    const metrics: SystemMetric[] = [
      {
        id: "metric_error_rate",
        name: "Error Rate",
        category: "performance",
        value: 0.02,
        unit: "%",
        threshold: { warning: 0.05, critical: 0.1 },
        status: "normal",
        trend: "stable",
        history: [],
        lastUpdated: Date.now(),
      },
      {
        id: "metric_response_time",
        name: "Average Response Time",
        category: "performance",
        value: 450,
        unit: "ms",
        threshold: { warning: 1000, critical: 2000 },
        status: "normal",
        trend: "down",
        history: [],
        lastUpdated: Date.now(),
      },
      {
        id: "metric_active_users",
        name: "Active Users",
        category: "usage",
        value: 1250,
        unit: "count",
        threshold: { warning: 5000, critical: 10000 },
        status: "normal",
        trend: "up",
        history: [],
        lastUpdated: Date.now(),
      },
      {
        id: "metric_cpu_usage",
        name: "CPU Usage",
        category: "technical",
        value: 0.45,
        unit: "%",
        threshold: { warning: 0.7, critical: 0.9 },
        status: "normal",
        trend: "stable",
        history: [],
        lastUpdated: Date.now(),
      },
      {
        id: "metric_memory_usage",
        name: "Memory Usage",
        category: "technical",
        value: 0.62,
        unit: "%",
        threshold: { warning: 0.8, critical: 0.95 },
        status: "normal",
        trend: "up",
        history: [],
        lastUpdated: Date.now(),
      },
    ];

    metrics.forEach(metric => {
      this.metrics.set(metric.id, metric);
    });
  }

  private initializeModerationQueues(): void {
    const queues: ModerationQueue[] = [
      {
        id: "queue_content",
        type: "content",
        items: [],
        assignees: [],
        sla: 24, // 24 hours
        priority: "medium",
        autoApproveThreshold: 0.95,
      },
      {
        id: "queue_user",
        type: "user",
        items: [],
        assignees: [],
        sla: 48, // 48 hours
        priority: "high",
        autoApproveThreshold: 0.9,
      },
      {
        id: "queue_transaction",
        type: "transaction",
        items: [],
        assignees: [],
        sla: 12, // 12 hours
        priority: "urgent",
        autoApproveThreshold: 0.98,
      },
    ];

    queues.forEach(queue => {
      this.moderationQueues.set(queue.id, queue);
    });
  }

  private initializeConfigs(): void {
    const configs: SystemConfig[] = [
      {
        id: "config_maintenance_mode",
        category: "system",
        key: "maintenance_mode",
        value: false,
        type: "boolean",
        description: "Enable maintenance mode",
        sensitive: false,
        requiresRestart: false,
        version: 1,
      },
      {
        id: "config_user_registration",
        category: "user",
        key: "user_registration_enabled",
        value: true,
        type: "boolean",
        description: "Enable new user registration",
        sensitive: false,
        requiresRestart: false,
        version: 1,
      },
      {
        id: "config_api_rate_limit",
        category: "api",
        key: "rate_limit_per_minute",
        value: 1000,
        type: "number",
        description: "API rate limit per minute",
        sensitive: false,
        requiresRestart: false,
        version: 1,
      },
    ];

    configs.forEach(config => {
      this.configs.set(config.id, config);
    });
  }

  // Admin User Management
  createAdminUser(userId: string, role: AdminRole, permissions: AdminPermission[]): string {
    const adminId = `admin_${userId}_${Date.now()}`;
    const adminUser: AdminUser = {
      id: adminId,
      userId,
      role,
      permissions,
      status: "active",
      assignedAreas: [],
      lastLogin: Date.now(),
      sessionExpiry: Date.now() + this.config.sessionTimeout,
      twoFactorEnabled: this.config.enableTwoFactor,
      ipWhitelist: this.config.enableIPWhitelist ? [] : [] as string[],
      activityLog: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    this.adminUsers.set(adminId, adminUser);
    this.notifyEvent({ type: "admin_created", data: adminUser });
    return adminId;
  }

  getAdminUser(userId: string): AdminUser | undefined {
    return Array.from(this.adminUsers.values()).find(admin => admin.userId === userId);
  }

  getAllAdminUsers(): AdminUser[] {
    return Array.from(this.adminUsers.values());
  }

  updateAdminUser(adminId: string, updates: Partial<AdminUser>): boolean {
    const adminUser = this.adminUsers.get(adminId);
    if (!adminUser) return false;

    const updatedAdmin = { ...adminUser, ...updates, updatedAt: Date.now() };
    this.adminUsers.set(adminId, updatedAdmin);
    this.notifyEvent({ type: "admin_updated", data: updatedAdmin });
    return true;
  }

  // Activity Logging
  logActivity(
    adminId: string,
    action: AdminAction,
    targetId?: string,
    targetType?: string,
    details: Record<string, any> = {},
    ipAddress: string = "unknown",
    userAgent: string = "unknown",
    outcome: "success" | "failure" | "partial" = "success"
  ): string {
    const activityId = `activity_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const activity: AdminActivity = {
      id: activityId,
      adminId,
      action,
      targetId,
      targetType,
      details,
      ipAddress,
      userAgent,
      timestamp: Date.now(),
      outcome,
    };

    this.activities.set(activityId, activity);

    // Update admin user's activity log
    const adminUser = this.adminUsers.get(adminId);
    if (adminUser) {
      adminUser.activityLog.push(activity);
      adminUser.lastLogin = Date.now();
      this.adminUsers.set(adminId, adminUser);
    }

    this.notifyEvent({ type: "activity_logged", data: activity });
    return activityId;
  }

  getActivities(adminId?: string, limit?: number): AdminActivity[] {
    const allActivities = Array.from(this.activities.values());
    let filtered = adminId ? allActivities.filter(a => a.adminId === adminId) : allActivities;
    filtered.sort((a, b) => b.timestamp - a.timestamp);
    return limit ? filtered.slice(0, limit) : filtered;
  }

  // System Metrics
  updateMetric(metricId: string, value: number): boolean {
    const metric = this.metrics.get(metricId);
    if (!metric) return false;

    // Add to history
    metric.history.push({
      timestamp: Date.now(),
      value: metric.value,
    });

    // Keep only last 100 data points
    if (metric.history.length > 100) {
      metric.history = metric.history.slice(-100);
    }

    // Update value and status
    metric.value = value;
    metric.lastUpdated = Date.now();

    // Calculate trend (simple implementation)
    if (metric.history.length >= 2) {
      const recent = metric.history.slice(-5);
      const avgRecent = recent.reduce((sum, p) => sum + p.value, 0) / recent.length;
      const older = metric.history.slice(-10, -5);
      if (older.length > 0) {
        const avgOlder = older.reduce((sum, p) => sum + p.value, 0) / older.length;
        metric.trend = avgRecent > avgOlder ? "up" : avgRecent < avgOlder ? "down" : "stable";
      }
    }

    // Update status based on thresholds
    if (value >= metric.threshold.critical) {
      metric.status = "critical";
      this.createAlert("critical", "system", `${metric.name} Critical`, `${metric.name} has reached critical level: ${value}${metric.unit}`, "high");
    } else if (value >= metric.threshold.warning) {
      metric.status = "warning";
      this.createAlert("warning", "system", `${metric.name} Warning`, `${metric.name} has reached warning level: ${value}${metric.unit}`, "medium");
    } else {
      metric.status = "normal";
    }

    this.metrics.set(metricId, metric);
    this.notifyEvent({ type: "metric_updated", data: metric });
    return true;
  }

  getMetric(metricId: string): SystemMetric | undefined {
    return this.metrics.get(metricId);
  }

  getAllMetrics(): SystemMetric[] {
    return Array.from(this.metrics.values());
  }

  // Alerts Management
  createAlert(
    type: "error" | "warning" | "info" | "critical",
    category: "system" | "security" | "performance" | "business" | "compliance",
    title: string,
    description: string,
    severity: "low" | "medium" | "high" | "critical",
    source?: string,
    affectedSystems?: string[],
    metrics?: string[]
  ): string {
    const alertId = `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const alert: SystemAlert = {
      id: alertId,
      type,
      category,
      title,
      description,
      severity,
      source: source || "system",
      affectedSystems: affectedSystems || [],
      metrics: metrics || [],
      status: "active",
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    this.alerts.set(alertId, alert);
    this.notifyEvent({ type: "alert_created", data: alert });
    return alertId;
  }

  getAlert(alertId: string): SystemAlert | undefined {
    return this.alerts.get(alertId);
  }

  getActiveAlerts(): SystemAlert[] {
    return Array.from(this.alerts.values()).filter(alert => alert.status === "active");
  }

  acknowledgeAlert(alertId: string, adminId: string): boolean {
    const alert = this.alerts.get(alertId);
    if (!alert) return false;

    alert.status = "acknowledged";
    alert.acknowledgedBy = adminId;
    alert.acknowledgedAt = Date.now();
    alert.updatedAt = Date.now();

    this.alerts.set(alertId, alert);
    this.notifyEvent({ type: "alert_acknowledged", data: alert });
    return true;
  }

  resolveAlert(alertId: string, adminId: string, resolution: string): boolean {
    const alert = this.alerts.get(alertId);
    if (!alert) return false;

    alert.status = "resolved";
    alert.resolvedBy = adminId;
    alert.resolvedAt = Date.now();
    alert.resolution = resolution;
    alert.updatedAt = Date.now();

    this.alerts.set(alertId, alert);
    this.notifyEvent({ type: "alert_resolved", data: alert });
    return true;
  }

  // Moderation Queue Management
  addToModerationQueue(
    queueType: "content" | "user" | "transaction" | "campaign",
    targetId: string,
    targetType: string,
    reason: string,
    severity: "low" | "medium" | "high" | "critical",
    evidence: Record<string, any>,
    reporter?: string
  ): string {
    const queueId = `queue_${queueType}`;
    const queue = this.moderationQueues.get(queueId);
    if (!queue) throw new Error(`Queue not found: ${queueType}`);

    const itemId = `item_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const item: ModerationItem = {
      id: itemId,
      type: queueType,
      targetId,
      targetType,
      reason,
      severity,
      evidence,
      reporter,
      status: "pending",
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    queue.items.push(item);
    this.moderationQueues.set(queueId, queue);
    this.notifyEvent({ type: "item_queued", data: { queue, item } });
    return itemId;
  }

  getModerationQueue(queueType: "content" | "user" | "transaction" | "campaign"): ModerationQueue | undefined {
    return this.moderationQueues.get(`queue_${queueType}`);
  }

  assignModerationItem(itemId: string, adminId: string): boolean {
    for (const queue of this.moderationQueues.values()) {
      const item = queue.items.find(i => i.id === itemId);
      if (item) {
        item.assignedTo = adminId;
        item.status = "reviewing";
        item.updatedAt = Date.now();
        this.moderationQueues.set(queue.id, queue);
        this.notifyEvent({ type: "item_assigned", data: { queue, item, adminId } });
        return true;
      }
    }
    return false;
  }

  resolveModerationItem(itemId: string, adminId: string, decision: "approved" | "rejected" | "escalated", notes?: string): boolean {
    for (const queue of this.moderationQueues.values()) {
      const item = queue.items.find(i => i.id === itemId);
      if (item) {
        item.status = decision;
        item.reviewedBy = adminId;
        item.reviewedAt = Date.now();
        item.decision = decision;
        item.notes = notes;
        item.updatedAt = Date.now();
        this.moderationQueues.set(queue.id, queue);
        this.notifyEvent({ type: "item_resolved", data: { queue, item, adminId, decision } });
        return true;
      }
    }
    return false;
  }

  // Configuration Management
  getConfig(configId: string): SystemConfig | undefined {
    return this.configs.get(configId);
  }

  getAllConfigs(): SystemConfig[] {
    return Array.from(this.configs.values());
  }

  updateConfig(configId: string, value: any, adminId: string): boolean {
    const config = this.configs.get(configId);
    if (!config) return false;

    config.value = value;
    config.lastModifiedBy = adminId;
    config.lastModifiedAt = Date.now();
    config.version++;

    this.configs.set(configId, config);
    this.notifyEvent({ type: "config_updated", data: { config, adminId } });
    return true;
  }

  // System Operations
  initiateMaintenance(systems: string[], duration: number, description: string, adminId: string): string {
    const windowId = `maintenance_${Date.now()}`;
    const window: MaintenanceWindow = {
      id: windowId,
      scheduledAt: Date.now(),
      duration,
      description,
      systems,
      status: "scheduled",
      approvedBy: adminId,
    };

    this.config.maintenanceWindows.push(window);
    this.notifyEvent({ type: "maintenance_scheduled", data: { window, adminId } });
    return windowId;
  }

  performEmergencyShutdown(reason: string, adminId: string): boolean {
    // Log emergency action
    this.logActivity(adminId, "emergency_shutdown", undefined, "system", { reason }, "unknown", "unknown");

    // Create critical alert
    this.createAlert(
      "critical",
      "system",
      "Emergency Shutdown",
      `System shutdown initiated by admin ${adminId}: ${reason}`,
      "critical",
      "admin",
      ["all"],
      ["all"]
    );

    this.notifyEvent({ type: "emergency_shutdown", data: { reason, adminId } });
    return true;
  }

  // Analytics and Statistics
  getOperatorStatistics(): {
    totalAdmins: number;
    activeAdmins: number;
    totalActivities: number;
    activitiesToday: number;
    activeAlerts: number;
    criticalAlerts: number;
    queuedItems: number;
    overdueItems: number;
    systemHealth: "healthy" | "warning" | "critical";
    uptime: number;
  } {
    const admins = this.getAllAdminUsers();
    const activities = this.getActivities();
    const alerts = this.getActiveAlerts();
    const now = Date.now();
    const today = new Date().setHours(0, 0, 0, 0);

    const activeAdmins = admins.filter(admin => admin.status === "active").length;
    const activitiesToday = activities.filter(a => a.timestamp >= today).length;
    const criticalAlerts = alerts.filter(a => a.severity === "critical").length;

    let queuedItems = 0;
    let overdueItems = 0;
    for (const queue of this.moderationQueues.values()) {
      queuedItems += queue.items.filter(i => i.status === "pending").length;
      overdueItems += queue.items.filter(i => {
        const age = now - i.createdAt;
        return i.status === "pending" && age > queue.sla * 60 * 60 * 1000;
      }).length;
    }

    // Calculate system health
    const metrics = this.getAllMetrics();
    const criticalMetrics = metrics.filter(m => m.status === "critical").length;
    const warningMetrics = metrics.filter(m => m.status === "warning").length;
    const systemHealth = criticalMetrics > 0 ? "critical" : warningMetrics > 0 ? "warning" : "healthy";

    return {
      totalAdmins: admins.length,
      activeAdmins,
      totalActivities: activities.length,
      activitiesToday,
      activeAlerts: alerts.length,
      criticalAlerts,
      queuedItems,
      overdueItems,
      systemHealth,
      uptime: 99.9, // Mock uptime percentage
    };
  }

  // Event Management
  onEvent(eventType: string, callback: (event: OperatorEvent) => void): () => void {
    const callbackId = `${eventType}_${Date.now()}`;
    this.eventCallbacks.set(callbackId, callback);
    return () => {
      this.eventCallbacks.delete(callbackId);
    };
  }

  private notifyEvent(event: OperatorEvent): void {
    this.eventCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error("Error in operator event callback:", error);
      }
    });
  }
}

// Types
export type OperatorEvent = {
  type: string;
  data: any;
  timestamp?: number;
};

// Singleton Instance
export const operatorEngine = new OperatorEngine();
