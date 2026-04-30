export type CampaignStatus =
  | "draft"
  | "pending_review"
  | "open"
  | "in_progress"
  | "submitted"
  | "under_review"
  | "revision_requested"
  | "completed"
  | "cancelled"
  | "disputed";

export type SubmissionStatus =
  | "draft"
  | "submitted"
  | "under_review"
  | "approved"
  | "rejected"
  | "revision_requested"
  | "paid"
  | "disputed";

export type EarningStatus =
  | "estimated"
  | "pending_review"
  | "approved"
  | "payable"
  | "processing"
  | "paid"
  | "failed"
  | "held"
  | "disputed"
  | "refunded"
  | "cancelled";

export type IntegrationStatus =
  | "not_configured"
  | "configured"
  | "connected"
  | "warning"
  | "error"
  | "disabled"
  | "mocked";

export type LedgerEventType =
  | "credit_granted"
  | "credit_spent"
  | "clip_generated"
  | "campaign_created"
  | "submission_created"
  | "submission_approved"
  | "submission_rejected"
  | "revision_requested"
  | "earning_estimated"
  | "earning_pending"
  | "earning_approved"
  | "earning_paid"
  | "platform_fee_collected"
  | "xp_awarded"
  | "badge_awarded"
  | "reputation_awarded"
  | "reputation_penalized"
  | "dispute_opened"
  | "dispute_resolved"
  | "refund_created"
  | "wallet_connected_placeholder"
  | "collectible_awarded_placeholder";

export type LwaClass =
  | "Signalwright"
  | "Clipforger"
  | "Trendseer"
  | "Render Mage"
  | "Campaign Hunter"
  | "Relic Broker"
  | "Loreblade"
  | "Vault Runner"
  | "Echo Smith"
  | "Worldbinder"
  | "Algorithm Knight"
  | "Myth Editor";

export type LwaFaction =
  | "The Signalwrights"
  | "The Clipforged"
  | "The Gold Thread Guild"
  | "The Void Editors"
  | "The Renderborn"
  | "The Mythstream Order"
  | "The Echo Court"
  | "The Relic Cartel"
  | "The Campaign Houses"
  | "The Black Frame Syndicate"
  | "The Algorithm Priests"
  | "The Vault Runners";

export type MoneyAmount = {
  amount: number;
  currency: "USD";
};

export type BillingPlan = {
  planKey: string;
  name: string;
  monthlyPrice: MoneyAmount;
  monthlyCredits: number;
  marketplaceFeePercent: number;
  maxCampaigns: number;
  maxUgcAssets: number;
  features: string[];
};

export type UserEntitlement = {
  userId: string;
  planKey: string;
  status: "active" | "inactive" | "expired" | "cancelled" | "past_due" | "manual_review";
  source: "manual" | "whop" | "stripe" | "apple" | "demo";
  sourceReferenceId?: string;
  currentPeriodStart?: string;
  currentPeriodEnd?: string;
  createdAt: string;
  updatedAt: string;
};

export type CreditBalance = {
  userId: string;
  balance: number;
  monthlyGrant: number;
  usedThisPeriod: number;
  periodStart?: string;
  periodEnd?: string;
  updatedAt: string;
};

export type CreditTransaction = {
  id: string;
  userId: string;
  transactionType: "grant" | "spend" | "refund" | "adjustment";
  amount: number;
  balanceAfter: number;
  reason: string;
  sourceType?: string;
  sourceId?: string;
  createdAt: string;
};

export type EarningsAccount = {
  userId: string;
  estimatedAmount: number;
  pendingReviewAmount: number;
  approvedAmount: number;
  payableAmount: number;
  paidAmount: number;
  heldAmount: number;
  currency: "USD";
  updatedAt: string;
};

export type EarningEvent = {
  id: string;
  userId: string;
  sourceType: string;
  sourceId?: string;
  amount: number;
  platformFeeAmount: number;
  netAmount: number;
  currency: "USD";
  status: EarningStatus;
  note: string;
  createdAt: string;
};

export type PayoutPlaceholder = {
  id: string;
  userId: string;
  amount: number;
  currency: "USD";
  status: "requested" | "pending_review" | "blocked" | "held" | "cancelled";
  blockedReason: string;
  createdAt: string;
  updatedAt: string;
};

export type StripeConnectReadiness = {
  enabled: boolean;
  ready: boolean;
  requiredEnvVars: string[];
  missingEnvVars: string[];
  blockers: string[];
  note: string;
};

export type JobType =
  | "upload_processing"
  | "transcript_generation"
  | "ai_clip_score"
  | "clip_generation"
  | "render_generation"
  | "caption_generation"
  | "ugc_moderation_scan"
  | "campaign_pack_generation"
  | "social_import"
  | "trend_import";

export type JobStatus = "queued" | "running" | "waiting" | "succeeded" | "failed" | "cancelled" | "retrying" | "expired";

export type WorldJob = {
  id: string;
  ownerUserId?: string;
  jobType: JobType;
  status: JobStatus;
  priority: "low" | "normal" | "high" | "urgent";
  progressPercent: number;
  title: string;
  description: string;
  sourceId?: string;
  targetType?: string;
  targetId?: string;
  inputJson: string;
  outputJson: string;
  errorMessage?: string;
  maxAttempts: number;
  attemptCount: number;
  nextRetryAt?: string;
  startedAt?: string;
  completedAt?: string;
  createdAt: string;
  updatedAt: string;
};

export type WorldJobEvent = {
  id: string;
  jobId: string;
  eventType: string;
  message: string;
  statusBefore?: string;
  statusAfter?: string;
  progressPercent?: number;
  metadataJson: string;
  createdAt: string;
};

export type WorldJobDashboard = {
  queued: number;
  running: number;
  succeeded: number;
  failed: number;
  retrying: number;
  cancelled: number;
  recentJobs: WorldJob[];
};

export type ClipMoment = {
  id: string;
  ownerUserId: string;
  sourceId: string;
  transcriptId?: string;
  startSeconds: number;
  endSeconds: number;
  transcriptExcerpt: string;
  momentType: string;
  reason: string;
  confidence: number;
  createdAt: string;
};

export type ClipCandidate = {
  id: string;
  ownerUserId: string;
  sourceId: string;
  transcriptId?: string;
  momentId?: string;
  title: string;
  hook: string;
  caption: string;
  startSeconds: number;
  endSeconds: number;
  targetPlatform: string;
  status: "draft" | "scored" | "selected" | "rejected" | "render_queued" | "rendered" | "failed";
  scoreTotal: number;
  scoreHook: number;
  scoreRetention: number;
  scoreClarity: number;
  scoreEmotion: number;
  scoreShareability: number;
  scorePlatformFit: number;
  riskNotes: string[];
  renderAssetId?: string;
  createdAt: string;
  updatedAt: string;
};

export type ClipPack = {
  id: string;
  ownerUserId: string;
  sourceId: string;
  transcriptId?: string;
  title: string;
  targetPlatform: string;
  desiredClipCount: number;
  status:
    | "draft"
    | "detecting_moments"
    | "scoring"
    | "ready_for_review"
    | "rendering"
    | "completed"
    | "failed"
    | "cancelled";
  selectedCandidateIds: string[];
  jobId?: string;
  createdAt: string;
  updatedAt: string;
};

export type ClipRenderContract = {
  id: string;
  ownerUserId: string;
  clipCandidateId: string;
  sourceId: string;
  outputFormat: string;
  aspectRatio: string;
  resolution: string;
  removeSilence: boolean;
  captionsEnabled: boolean;
  captionStyleJson: string;
  musicEnabled: boolean;
  musicPolicy: "none" | "licensed" | "user_provided";
  introSeconds: number;
  outroSeconds: number;
  renderJobId?: string;
  createdAt: string;
};

export type ClipSummary = {
  id: string;
  title: string;
  hook: string;
  caption: string;
  score: number;
  confidence: number;
  platform: "TikTok" | "Instagram" | "YouTube" | "Facebook" | "Twitch" | "Multi";
  status: "rendered" | "strategy_only" | "failed" | "processing";
  previewUrl?: string;
  thumbnailText?: string;
  cta?: string;
  postOrder?: number;
};

export type MarketplaceCampaign = {
  id: string;
  title: string;
  description: string;
  buyerName: string;
  sourceType: "video_url" | "upload" | "podcast" | "livestream" | "clip_pack";
  targetPlatform: "TikTok" | "Instagram" | "YouTube" | "Facebook" | "Multi";
  budget: MoneyAmount;
  platformFeePercent: number;
  clipCount: number;
  deadline: string;
  status: CampaignStatus;
  requirements: string[];
  rightsRequired: string;
  createdAt: string;
  submissionsCount: number;
  approvedSubmissionsCount: number;
};

export type CampaignSubmission = {
  id: string;
  campaignId: string;
  clipperName: string;
  title: string;
  hook: string;
  caption: string;
  assetUrl?: string;
  status: SubmissionStatus;
  estimatedEarnings: MoneyAmount;
  submittedAt: string;
  reviewNote?: string;
};

export type UGCAsset = {
  id: string;
  creatorUserId: string;
  title: string;
  assetType: string;
  description: string;
  price: MoneyAmount;
  status: "draft" | "pending_review" | "approved" | "rejected" | "removed" | "disputed";
  moderationStatus: "pending" | "approved" | "rejected" | "flagged" | "escalated" | "removed" | "appealed";
  rightsConfirmed: boolean;
  licenseSummary: string;
  previewUrl?: string;
  createdAt: string;
};

export type ModerationQueueItem = {
  id: string;
  targetType: string;
  targetId: string;
  submittedBy?: string;
  status: "pending" | "approved" | "rejected" | "flagged" | "escalated" | "removed" | "appealed";
  reason: string;
  automatedScore?: number;
  reviewer?: string;
  reviewerNote?: string;
  createdAt: string;
  reviewedAt?: string;
};

export type FraudFlag = {
  id: string;
  userId?: string;
  targetType: string;
  targetId?: string;
  flagType: string;
  status: "open" | "in_review" | "cleared" | "confirmed" | "escalated";
  severity: "low" | "medium" | "high" | "critical";
  evidence: string;
  reviewer?: string;
  reviewerNote?: string;
  createdAt: string;
  resolvedAt?: string;
};

export type ContentRightsClaim = {
  id: string;
  claimantName: string;
  claimantEmail: string;
  targetType: string;
  targetId: string;
  claimSummary: string;
  status: "open" | "in_review" | "information_requested" | "resolved" | "rejected" | "escalated";
  adminNote?: string;
  createdAt: string;
  resolvedAt?: string;
};

export type EarningSummary = {
  estimated: MoneyAmount;
  pendingReview: MoneyAmount;
  approved: MoneyAmount;
  payable: MoneyAmount;
  paid: MoneyAmount;
  held: MoneyAmount;
};

export type LedgerEntry = {
  id: string;
  type: LedgerEventType;
  label: string;
  amount?: MoneyAmount;
  xp?: number;
  reputation?: number;
  createdAt: string;
  status: "recorded" | "pending" | "reversed" | "failed";
  referenceId?: string;
};

export type Badge = {
  id: string;
  name: string;
  tier: "common" | "rare" | "epic" | "mythic" | "founder";
  description: string;
  lore: string;
  unlockedAt?: string;
};

export type UserWorldProfile = {
  id: string;
  displayName: string;
  className: LwaClass;
  faction: LwaFaction;
  level: number;
  xp: number;
  nextLevelXp: number;
  creatorReputation: number;
  clipperReputation: number;
  marketplaceReputation: number;
  badges: Badge[];
  relics: Badge[];
  titles: string[];
};

export type Quest = {
  id: string;
  title: string;
  description: string;
  category: "daily" | "weekly" | "clipping" | "marketplace" | "ugc" | "faction" | "founder" | "seasonal";
  progress: number;
  goal: number;
  rewardXp: number;
  rewardBadge?: Badge;
  status: "available" | "in_progress" | "completed" | "claimed";
};

export type IntegrationCard = {
  id: string;
  name: string;
  category: "ai" | "social" | "payments" | "storage" | "blockchain" | "platform";
  status: IntegrationStatus;
  description: string;
  envVars: string[];
  adminOnly?: boolean;
};

export type AdminQueueItem = {
  id: string;
  type:
    | "campaign_review"
    | "submission_review"
    | "payout_review"
    | "dispute"
    | "fraud_flag"
    | "ugc_review"
    | "rights_claim";
  title: string;
  status: "open" | "in_review" | "resolved" | "blocked";
  priority: "low" | "medium" | "high" | "critical";
  createdAt: string;
  owner?: string;
};
