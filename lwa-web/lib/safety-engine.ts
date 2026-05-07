export type SafetyRiskLevel = 
  | "low"
  | "medium"
  | "high"
  | "critical";

export type SafetyViolationType = 
  | "inappropriate_content"
  | "copyright_infringement"
  | "fraudulent_activity"
  | "spam_behavior"
  | "harassment"
  | "misinformation"
  | "illegal_content"
  | "privacy_violation"
  | "terms_violation"
  | "security_threat";

export type ComplianceStandard = 
  | "GDPR"
  | "CCPA"
  | "COPPA"
  | "HIPAA"
  | "FINRA"
  | "DMCA"
  | "FTC"
  | "INTERNAL";

export type SafetyRule = {
  id: string;
  name: string;
  description: string;
  type: SafetyViolationType;
  severity: SafetyRiskLevel;
  enabled: boolean;
  autoFlag: boolean;
  autoBlock: boolean;
  conditions: SafetyCondition[];
  actions: SafetyAction[];
  compliance: ComplianceStandard[];
  createdAt: number;
  updatedAt: number;
};

export type SafetyCondition = {
  type: "content" | "behavior" | "user" | "transaction" | "system";
  field: string;
  operator: "equals" | "contains" | "matches" | "greater_than" | "less_than" | "in" | "not_in";
  value: any;
  weight: number;
};

export type SafetyAction = {
  type: "flag" | "block" | "warn" | "log" | "notify" | "quarantine" | "suspend";
  parameters?: Record<string, any>;
  delay?: number; // milliseconds
};

export type SafetyReport = {
  id: string;
  type: SafetyViolationType;
  severity: SafetyRiskLevel;
  userId?: string;
  contentId?: string;
  transactionId?: string;
  description: string;
  evidence: {
    content?: string;
    metadata?: Record<string, any>;
    screenshots?: string[];
    logs?: string[];
  };
  ruleId: string;
  ruleName: string;
  status: "pending" | "reviewing" | "resolved" | "dismissed" | "escalated";
  assignedTo?: string;
  reviewedBy?: string;
  resolution?: string;
  actionsTaken: SafetyAction[];
  createdAt: number;
  reviewedAt?: number;
  resolvedAt?: number;
};

export type FraudPattern = {
  id: string;
  name: string;
  description: string;
  type: "payment" | "account" | "content" | "behavior" | "system";
  severity: SafetyRiskLevel;
  indicators: FraudIndicator[];
  threshold: number;
  timeWindow: number; // milliseconds
  enabled: boolean;
  autoBlock: boolean;
  createdAt: number;
  updatedAt: number;
};

export type FraudIndicator = {
  type: "frequency" | "amount" | "pattern" | "anomaly" | "blacklist" | "whitelist";
  field: string;
  condition: string;
  weight: number;
  description: string;
};

export type ComplianceAudit = {
  id: string;
  standard: ComplianceStandard;
  scope: "user_data" | "transactions" | "content" | "system" | "all";
  status: "pending" | "in_progress" | "completed" | "failed";
  results: ComplianceAuditResult[];
  score: number;
  issues: ComplianceIssue[];
  recommendations: string[];
  auditedBy?: string;
  auditedAt?: number;
  nextAudit: number;
  createdAt: number;
};

export type ComplianceAuditResult = {
  category: string;
  requirement: string;
  status: "compliant" | "non_compliant" | "partial";
  details: string;
  risk: SafetyRiskLevel;
  remediation?: string;
};

export type ComplianceIssue = {
  id: string;
  category: string;
  severity: SafetyRiskLevel;
  description: string;
  impact: string;
  remediation: string;
  deadline: number;
  status: "open" | "in_progress" | "resolved" | "overdue";
  assignedTo?: string;
  createdAt: number;
  resolvedAt?: number;
};

export type SafetyConfig = {
  enableAutoFlagging: boolean;
  enableAutoBlocking: boolean;
  reviewQueueSize: number;
  escalationThreshold: number;
  retentionPeriod: number;
  complianceStandards: ComplianceStandard[];
  notificationChannels: string[];
  aiModelEnabled: boolean;
  manualReviewRequired: SafetyViolationType[];
};

// Safety Engine Implementation
export class SafetyEngine {
  private rules: Map<string, SafetyRule> = new Map();
  private reports: Map<string, SafetyReport> = new Map();
  private fraudPatterns: Map<string, FraudPattern> = new Map();
  private complianceAudits: Map<string, ComplianceAudit> = new Map();
  private config: SafetyConfig;
  private eventCallbacks: Map<string, (event: SafetyEvent) => void> = new Map();

  constructor(config?: Partial<SafetyConfig>) {
    this.config = {
      enableAutoFlagging: true,
      enableAutoBlocking: false,
      reviewQueueSize: 100,
      escalationThreshold: 5,
      retentionPeriod: 365 * 24 * 60 * 60 * 1000, // 1 year
      complianceStandards: ["GDPR", "CCPA", "COPPA"],
      notificationChannels: ["email", "slack", "dashboard"],
      aiModelEnabled: true,
      manualReviewRequired: ["copyright_infringement", "fraudulent_activity", "illegal_content"],
      ...config,
    };

    this.initializeSafetyRules();
    this.initializeFraudPatterns();
  }

  private initializeSafetyRules(): void {
    const rules: SafetyRule[] = [
      {
        id: "rule_inappropriate_content",
        name: "Inappropriate Content Detection",
        description: "Detects and flags inappropriate or harmful content",
        type: "inappropriate_content",
        severity: "high",
        enabled: true,
        autoFlag: true,
        autoBlock: false,
        conditions: [
          {
            type: "content",
            field: "text",
            operator: "contains",
            value: ["profanity", "hate_speech", "violence", "adult_content"],
            weight: 0.8,
          },
        ],
        actions: [
          { type: "flag" },
          { type: "log" },
          { type: "notify", parameters: { channels: ["admin"] } },
        ],
        compliance: ["GDPR", "CCPA"],
        createdAt: Date.now(),
        updatedAt: Date.now(),
      },
      {
        id: "rule_spam_detection",
        name: "Spam Behavior Detection",
        description: "Identifies spam and repetitive behavior patterns",
        type: "spam_behavior",
        severity: "medium",
        enabled: true,
        autoFlag: true,
        autoBlock: false,
        conditions: [
          {
            type: "behavior",
            field: "post_frequency",
            operator: "greater_than",
            value: 10, // posts per minute
            weight: 0.7,
          },
          {
            type: "content",
            field: "similarity_score",
            operator: "greater_than",
            value: 0.9, // 90% similarity
            weight: 0.6,
          },
        ],
        actions: [
          { type: "flag" },
          { type: "warn" },
          { type: "log" },
        ],
        compliance: ["FTC"],
        createdAt: Date.now(),
        updatedAt: Date.now(),
      },
      {
        id: "rule_suspicious_transactions",
        name: "Suspicious Transaction Monitoring",
        description: "Monitors for potentially fraudulent financial activities",
        type: "fraudulent_activity",
        severity: "critical",
        enabled: true,
        autoFlag: true,
        autoBlock: true,
        conditions: [
          {
            type: "transaction",
            field: "amount",
            operator: "greater_than",
            value: 10000, // $10,000
            weight: 0.9,
          },
          {
            type: "behavior",
            field: "transaction_frequency",
            operator: "greater_than",
            value: 5, // per minute
            weight: 0.8,
          },
        ],
        actions: [
          { type: "flag" },
          { type: "block" },
          { type: "quarantine" },
          { type: "notify", parameters: { channels: ["fraud_team"] } },
        ],
        compliance: ["FINRA", "GDPR"],
        createdAt: Date.now(),
        updatedAt: Date.now(),
      },
    ];

    rules.forEach(rule => {
      this.rules.set(rule.id, rule);
    });
  }

  private initializeFraudPatterns(): void {
    const patterns: FraudPattern[] = [
      {
        id: "pattern_chargeback_fraud",
        name: "Chargeback Fraud Pattern",
        description: "Identifies potential chargeback fraud behavior",
        type: "payment",
        severity: "high",
        indicators: [
          {
            type: "frequency",
            field: "chargeback_rate",
            condition: "> 0.05", // 5% chargeback rate
            weight: 0.8,
            description: "High chargeback rate",
          },
          {
            type: "pattern",
            field: "payment_method",
            condition: "multiple_cards",
            weight: 0.6,
            description: "Multiple payment cards used",
          },
        ],
        threshold: 0.7,
        timeWindow: 30 * 24 * 60 * 60 * 1000, // 30 days
        enabled: true,
        autoBlock: false,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      },
      {
        id: "pattern_account_takeover",
        name: "Account Takeover Pattern",
        description: "Detects potential account compromise attempts",
        type: "account",
        severity: "critical",
        indicators: [
          {
            type: "anomaly",
            field: "login_location",
            condition: "multiple_countries",
            weight: 0.9,
            description: "Logins from multiple countries",
          },
          {
            type: "frequency",
            field: "failed_logins",
            condition: "> 10",
            weight: 0.7,
            description: "Multiple failed login attempts",
          },
        ],
        threshold: 0.8,
        timeWindow: 24 * 60 * 60 * 1000, // 24 hours
        enabled: true,
        autoBlock: true,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      },
    ];

    patterns.forEach(pattern => {
      this.fraudPatterns.set(pattern.id, pattern);
    });
  }

  // Content Safety Check
  async checkContentSafety(content: {
    text?: string;
    mediaUrl?: string;
    userId?: string;
    metadata?: Record<string, any>;
  }): Promise<{
    safe: boolean;
    riskLevel: SafetyRiskLevel;
    violations: SafetyViolation[];
    flagged: boolean;
    blocked: boolean;
  }> {
    const violations: SafetyViolation[] = [];
    let overallRiskLevel: SafetyRiskLevel = "low";
    let flagged = false;
    let blocked = false;

    // Check against all enabled rules
    for (const rule of this.rules.values()) {
      if (!rule.enabled) continue;

      const violation = await this.evaluateRule(rule, content);
      if (violation) {
        violations.push(violation);
        
        // Update risk level
        if (this.compareRiskLevel(violation.severity, overallRiskLevel)) {
          overallRiskLevel = violation.severity;
        }

        // Check auto-flag and auto-block
        if (rule.autoFlag) flagged = true;
        if (rule.autoBlock) blocked = true;
      }
    }

    // Create safety report if violations found
    if (violations.length > 0) {
      this.createSafetyReport({
        type: violations[0].type,
        severity: overallRiskLevel,
        userId: content.userId,
        contentId: content.metadata?.contentId,
        description: `Content safety violations detected: ${violations.map(v => v.ruleName).join(", ")}`,
        evidence: {
          content: content.text,
          metadata: content.metadata,
        },
        ruleId: violations[0].ruleId,
        ruleName: violations[0].ruleName,
      });
    }

    return {
      safe: violations.length === 0,
      riskLevel: overallRiskLevel,
      violations,
      flagged,
      blocked,
    };
  }

  private async evaluateRule(rule: SafetyRule, content: any): Promise<SafetyViolation | null> {
    let score = 0;
    const matchedConditions: SafetyCondition[] = [];

    for (const condition of rule.conditions) {
      if (this.evaluateCondition(condition, content)) {
        score += condition.weight;
        matchedConditions.push(condition);
      }
    }

    // Rule is triggered if score exceeds threshold (simplified: any match)
    if (matchedConditions.length > 0) {
      return {
        ruleId: rule.id,
        ruleName: rule.name,
        type: rule.type,
        severity: rule.severity,
        score,
        matchedConditions,
        timestamp: Date.now(),
      };
    }

    return null;
  }

  private evaluateCondition(condition: SafetyCondition, content: any): boolean {
    const value = this.getNestedValue(content, condition.field);
    if (value === undefined) return false;

    switch (condition.operator) {
      case "equals":
        return value === condition.value;
      case "contains":
        if (Array.isArray(condition.value)) {
          return condition.value.some(v => String(value).includes(v));
        }
        return String(value).includes(condition.value);
      case "matches":
        return new RegExp(condition.value).test(String(value));
      case "greater_than":
        return Number(value) > Number(condition.value);
      case "less_than":
        return Number(value) < Number(condition.value);
      case "in":
        return Array.isArray(condition.value) && condition.value.includes(value);
      case "not_in":
        return Array.isArray(condition.value) && !condition.value.includes(value);
      default:
        return false;
    }
  }

  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  private compareRiskLevel(level1: SafetyRiskLevel, level2: SafetyRiskLevel): boolean {
    const levels = { low: 1, medium: 2, high: 3, critical: 4 };
    return levels[level1] > levels[level2];
  }

  // Fraud Detection
  async detectFraud(activity: {
    userId: string;
    type: "transaction" | "login" | "content" | "account";
    data: Record<string, any>;
  }): Promise<{
    fraudDetected: boolean;
    riskScore: number;
    patterns: FraudPattern[];
    recommendations: string[];
  }> {
    const detectedPatterns: FraudPattern[] = [];
    let totalScore = 0;

    // Check against all enabled fraud patterns
    for (const pattern of this.fraudPatterns.values()) {
      if (!pattern.enabled) continue;

      const patternScore = await this.evaluateFraudPattern(pattern, activity);
      if (patternScore >= pattern.threshold) {
        detectedPatterns.push(pattern);
        totalScore += patternScore;
      }
    }

    const riskScore = Math.min(totalScore, 1.0);
    const fraudDetected = detectedPatterns.length > 0;

    // Generate recommendations
    const recommendations = this.generateFraudRecommendations(detectedPatterns, activity);

    // Auto-block if critical and enabled
    if (fraudDetected) {
      const criticalPattern = detectedPatterns.find(p => p.severity === "critical");
      if (criticalPattern && criticalPattern.autoBlock) {
        await this.blockUser(activity.userId, "fraud_detection", criticalPattern.id);
      }
    }

    return {
      fraudDetected,
      riskScore,
      patterns: detectedPatterns,
      recommendations,
    };
  }

  private async evaluateFraudPattern(pattern: FraudPattern, activity: any): Promise<number> {
    let score = 0;
    const matchedIndicators: FraudIndicator[] = [];

    for (const indicator of pattern.indicators) {
      if (this.evaluateFraudIndicator(indicator, activity.data)) {
        score += indicator.weight;
        matchedIndicators.push(indicator);
      }
    }

    return score;
  }

  private evaluateFraudIndicator(indicator: FraudIndicator, data: any): boolean {
    const value = this.getNestedValue(data, indicator.field);
    if (value === undefined) return false;

    // Simple evaluation - in production, use more sophisticated logic
    switch (indicator.type) {
      case "frequency":
        return Number(value) > Number(indicator.condition.split(" ")[1]);
      case "amount":
        return Number(value) > Number(indicator.condition.split(" ")[1]);
      case "pattern":
        return indicator.condition === "multiple_countries" && Array.isArray(value) && value.length > 1;
      case "anomaly":
        return indicator.condition === "multiple_countries" && value !== "home_country";
      default:
        return false;
    }
  }

  private generateFraudRecommendations(patterns: FraudPattern[], activity: any): string[] {
    const recommendations: string[] = [];

    patterns.forEach(pattern => {
      switch (pattern.type) {
        case "payment":
          recommendations.push("Review payment method and verify transaction details");
          recommendations.push("Consider additional authentication for high-value transactions");
          break;
        case "account":
          recommendations.push("Require password reset and two-factor authentication");
          recommendations.push("Review recent account activity for unauthorized access");
          break;
        case "content":
          recommendations.push("Review content for policy violations");
          recommendations.push("Consider temporary content restrictions");
          break;
        case "behavior":
          recommendations.push("Monitor user behavior patterns closely");
          recommendations.push("Implement rate limiting if necessary");
          break;
      }
    });

    return recommendations;
  }

  // Safety Report Management
  createSafetyReport(report: Omit<SafetyReport, "id" | "status" | "actionsTaken" | "createdAt">): string {
    const reportId = `safety_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const safetyReport: SafetyReport = {
      id: reportId,
      status: "pending",
      actionsTaken: [],
      createdAt: Date.now(),
      ...report,
    };

    this.reports.set(reportId, safetyReport);
    this.notifyEvent({ type: "safety_report_created", data: safetyReport });
    return reportId;
  }

  getSafetyReport(reportId: string): SafetyReport | undefined {
    return this.reports.get(reportId);
  }

  getSafetyReportsByUser(userId: string): SafetyReport[] {
    return Array.from(this.reports.values()).filter(report => report.userId === userId);
  }

  getSafetyReportsByStatus(status: SafetyReport["status"]): SafetyReport[] {
    return Array.from(this.reports.values()).filter(report => report.status === status);
  }

  updateSafetyReport(reportId: string, updates: Partial<SafetyReport>): boolean {
    const report = this.reports.get(reportId);
    if (!report) return false;

    const updatedReport = { ...report, ...updates };
    this.reports.set(reportId, updatedReport);
    this.notifyEvent({ type: "safety_report_updated", data: updatedReport });
    return true;
  }

  // Compliance Management
  createComplianceAudit(
    standard: ComplianceStandard,
    scope: ComplianceAudit["scope"]
  ): string {
    const auditId = `audit_${standard}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const audit: ComplianceAudit = {
      id: auditId,
      standard,
      scope,
      status: "pending",
      results: [],
      score: 0,
      issues: [],
      recommendations: [],
      nextAudit: Date.now() + (90 * 24 * 60 * 60 * 1000), // 90 days
      createdAt: Date.now(),
    };

    this.complianceAudits.set(auditId, audit);
    this.notifyEvent({ type: "compliance_audit_created", data: audit });
    return auditId;
  }

  runComplianceAudit(auditId: string): boolean {
    const audit = this.complianceAudits.get(auditId);
    if (!audit) return false;

    audit.status = "in_progress";
    audit.auditedAt = Date.now();

    // Simulate audit execution
    const results = this.generateAuditResults(audit.standard, audit.scope);
    audit.results = results;
    audit.score = this.calculateAuditScore(results);
    audit.issues = this.generateAuditIssues(results, audit.standard);
    audit.status = "completed";

    this.complianceAudits.set(auditId, audit);
    this.notifyEvent({ type: "compliance_audit_completed", data: audit });
    return true;
  }

  private generateAuditResults(standard: ComplianceStandard, scope: ComplianceAudit["scope"]): ComplianceAuditResult[] {
    // Mock audit results - in production, implement actual audit logic
    const results: ComplianceAuditResult[] = [];

    switch (standard) {
      case "GDPR":
        results.push(
          {
            category: "Data Protection",
            requirement: "User consent management",
            status: "compliant",
            details: "Consent mechanisms are properly implemented",
            risk: "low",
          },
          {
            category: "Data Retention",
            requirement: "Data retention policies",
            status: "partial",
            details: "Some data retention periods need adjustment",
            risk: "medium",
            remediation: "Update retention policies to comply with GDPR requirements",
          }
        );
        break;
      case "CCPA":
        results.push(
          {
            category: "Consumer Rights",
            requirement: "Data deletion requests",
            status: "compliant",
            details: "Data deletion process is functional",
            risk: "low",
          },
          {
            category: "Privacy Policy",
            requirement: "Privacy notice transparency",
            status: "compliant",
            details: "Privacy policy meets CCPA requirements",
            risk: "low",
          }
        );
        break;
    }

    return results;
  }

  private calculateAuditScore(results: ComplianceAuditResult[]): number {
    const compliantCount = results.filter(r => r.status === "compliant").length;
    return Math.round((compliantCount / results.length) * 100);
  }

  private generateAuditIssues(results: ComplianceAuditResult[], standard: ComplianceStandard): ComplianceIssue[] {
    return results
      .filter(r => r.status !== "compliant")
      .map(r => ({
        id: `issue_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        category: r.category,
        severity: r.risk === "critical" ? "critical" : r.risk === "high" ? "high" : "medium",
        description: `${r.requirement} - ${r.details}`,
        impact: `Non-compliance with ${standard} requirements`,
        remediation: r.remediation || "Address the identified compliance gaps",
        deadline: Date.now() + (30 * 24 * 60 * 60 * 1000), // 30 days
        status: "open" as const,
        createdAt: Date.now(),
      }));
  }

  // User Management
  async blockUser(userId: string, reason: string, ruleId?: string): Promise<boolean> {
    // Create safety report
    this.createSafetyReport({
      type: "security_threat",
      severity: "high",
      userId,
      description: `User blocked: ${reason}`,
      ruleId: ruleId || "manual_block",
      ruleName: "Manual Block",
      evidence: {},
    });

    // In production, implement actual user blocking logic
    this.notifyEvent({ type: "user_blocked", data: { userId, reason, ruleId } });
    return true;
  }

  async warnUser(userId: string, message: string, ruleId?: string): Promise<boolean> {
    // Create safety report
    this.createSafetyReport({
      type: "terms_violation",
      severity: "medium",
      userId,
      description: `User warned: ${message}`,
      ruleId: ruleId || "manual_warning",
      ruleName: "Manual Warning",
      evidence: {},
    });

    // In production, implement actual user warning logic
    this.notifyEvent({ type: "user_warned", data: { userId, message, ruleId } });
    return true;
  }

  // Analytics and Statistics
  getSafetyStatistics(): {
    totalReports: number;
    reportsByType: Record<SafetyViolationType, number>;
    reportsBySeverity: Record<SafetyRiskLevel, number>;
    pendingReports: number;
    resolvedReports: number;
    fraudDetections: number;
    complianceAudits: number;
    averageAuditScore: number;
    activeRules: number;
    blockedUsers: number;
  } {
    const reports = Array.from(this.reports.values());
    const audits = Array.from(this.complianceAudits.values());

    const reportsByType = reports.reduce((acc, report) => {
      acc[report.type] = (acc[report.type] || 0) + 1;
      return acc;
    }, {} as Record<SafetyViolationType, number>);

    const reportsBySeverity = reports.reduce((acc, report) => {
      acc[report.severity] = (acc[report.severity] || 0) + 1;
      return acc;
    }, {} as Record<SafetyRiskLevel, number>);

    const pendingReports = reports.filter(r => r.status === "pending").length;
    const resolvedReports = reports.filter(r => r.status === "resolved").length;

    const averageAuditScore = audits.length > 0
      ? audits.reduce((sum, audit) => sum + audit.score, 0) / audits.length
      : 0;

    return {
      totalReports: reports.length,
      reportsByType,
      reportsBySeverity,
      pendingReports,
      resolvedReports,
      fraudDetections: reports.filter(r => r.type === "fraudulent_activity").length,
      complianceAudits: audits.length,
      averageAuditScore,
      activeRules: Array.from(this.rules.values()).filter(r => r.enabled).length,
      blockedUsers: reports.filter(r => r.actionsTaken.some(a => a.type === "block")).length,
    };
  }

  // Event Management
  onEvent(eventType: string, callback: (event: SafetyEvent) => void): () => void {
    const callbackId = `${eventType}_${Date.now()}`;
    this.eventCallbacks.set(callbackId, callback);
    return () => {
      this.eventCallbacks.delete(callbackId);
    };
  }

  private notifyEvent(event: SafetyEvent): void {
    this.eventCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error("Error in safety event callback:", error);
      }
    });
  }
}

// Types
export type SafetyViolation = {
  ruleId: string;
  ruleName: string;
  type: SafetyViolationType;
  severity: SafetyRiskLevel;
  score: number;
  matchedConditions: SafetyCondition[];
  timestamp: number;
};

export type SafetyEvent = {
  type: string;
  data: any;
  timestamp?: number;
};

// Singleton Instance
export const safetyEngine = new SafetyEngine();
