import type {
  BillingPlan,
  CampaignSubmission,
  ClipCandidate,
  ClipMoment,
  ClipPack,
  ClipRenderContract,
  ContentRightsClaim,
  CreditBalance,
  CreditTransaction,
  EarningEvent,
  EarningsAccount,
  FraudFlag,
  IntegrationCard,
  LedgerEntry,
  MarketplaceCampaign,
  ModerationQueueItem,
  PayoutPlaceholder,
  StripeConnectReadiness,
  UGCAsset,
  WorldJob,
  WorldJobDashboard,
  WorldJobEvent,
  UserEntitlement,
  UserWorldProfile,
} from "./types";

const RAW_API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "";
const API_BASE = RAW_API_BASE.replace(/\/$/, "");

type BackendCampaign = {
  public_id: string;
  title: string;
  description: string;
  target_platform: string;
  source_type: string;
  budget: { amount: number; currency: "USD" };
  platform_fee_percent?: number;
  clip_count: number;
  deadline?: string | null;
  status: string;
  rights_required: string;
  created_at: string;
};

type BackendSubmission = {
  public_id: string;
  campaign_public_id: string;
  title: string;
  hook: string;
  caption: string;
  asset_url?: string | null;
  status: string;
  estimated_earnings: { amount: number; currency: "USD" };
  review_note?: string | null;
  rights_confirmed: boolean;
  created_at: string;
};

type BackendUGCAsset = {
  public_id: string;
  creator_user_id: string;
  title: string;
  asset_type: string;
  description: string;
  price_amount: number;
  currency: "USD";
  status: UGCAsset["status"];
  moderation_status: UGCAsset["moderationStatus"];
  rights_confirmed: boolean;
  license_summary: string;
  preview_url?: string | null;
  created_at: string;
};

type BackendModerationQueueItem = {
  public_id: string;
  target_type: string;
  target_public_id: string;
  submitted_by_user_id?: string | null;
  status: ModerationQueueItem["status"];
  reason: string;
  automated_score?: number | null;
  reviewer_user_id?: string | null;
  reviewer_note?: string | null;
  created_at: string;
  reviewed_at?: string | null;
};

type BackendFraudFlag = {
  public_id: string;
  user_id?: string | null;
  target_type: string;
  target_public_id?: string | null;
  flag_type: string;
  status: FraudFlag["status"];
  severity: FraudFlag["severity"];
  evidence: string;
  reviewer_user_id?: string | null;
  reviewer_note?: string | null;
  created_at: string;
  resolved_at?: string | null;
};

type BackendRightsClaim = {
  public_id: string;
  claimant_name: string;
  claimant_email: string;
  target_type: string;
  target_public_id: string;
  claim_summary: string;
  status: ContentRightsClaim["status"];
  admin_note?: string | null;
  created_at: string;
  resolved_at?: string | null;
};

type BackendBillingPlan = {
  plan_key: string;
  name: string;
  monthly_price_amount: number;
  currency: "USD";
  monthly_credits: number;
  marketplace_fee_percent: number;
  max_campaigns: number;
  max_ugc_assets: number;
  features: string[];
};

type BackendEntitlement = {
  user_id: string;
  plan_key: string;
  status: UserEntitlement["status"];
  source: UserEntitlement["source"];
  source_reference_id?: string | null;
  current_period_start?: string | null;
  current_period_end?: string | null;
  created_at: string;
  updated_at: string;
};

type BackendCreditBalance = {
  user_id: string;
  balance: number;
  monthly_grant: number;
  used_this_period: number;
  period_start?: string | null;
  period_end?: string | null;
  updated_at: string;
};

type BackendCreditTransaction = {
  public_id: string;
  user_id: string;
  transaction_type: CreditTransaction["transactionType"];
  amount: number;
  balance_after: number;
  reason: string;
  source_type?: string | null;
  source_public_id?: string | null;
  created_at: string;
};

type BackendEarningsAccount = {
  user_id: string;
  estimated_amount: number;
  pending_review_amount: number;
  approved_amount: number;
  payable_amount: number;
  paid_amount: number;
  held_amount: number;
  currency: "USD";
  updated_at: string;
};

type BackendEarningEvent = {
  public_id: string;
  user_id: string;
  source_type: string;
  source_public_id?: string | null;
  amount: number;
  platform_fee_amount: number;
  net_amount: number;
  currency: "USD";
  status: EarningEvent["status"];
  note: string;
  created_at: string;
};

type BackendPayoutPlaceholder = {
  public_id: string;
  user_id: string;
  amount: number;
  currency: "USD";
  status: PayoutPlaceholder["status"];
  blocked_reason: string;
  created_at: string;
  updated_at: string;
};

type BackendStripeReadiness = {
  enabled: boolean;
  ready: boolean;
  required_env_vars: string[];
  missing_env_vars: string[];
  blockers: string[];
  note: string;
};

type BackendWorldJob = {
  public_id: string;
  owner_user_id?: string | null;
  job_type: WorldJob["jobType"];
  status: WorldJob["status"];
  priority: WorldJob["priority"];
  progress_percent: number;
  title: string;
  description: string;
  source_public_id?: string | null;
  target_type?: string | null;
  target_public_id?: string | null;
  input_json: string;
  output_json: string;
  error_message?: string | null;
  max_attempts: number;
  attempt_count: number;
  next_retry_at?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
};

type BackendWorldJobEvent = {
  public_id: string;
  job_public_id: string;
  event_type: string;
  message: string;
  status_before?: string | null;
  status_after?: string | null;
  progress_percent?: number | null;
  metadata_json: string;
  created_at: string;
};

type BackendWorldJobDashboard = {
  queued: number;
  running: number;
  succeeded: number;
  failed: number;
  retrying: number;
  cancelled: number;
  recent_jobs: BackendWorldJob[];
};

type BackendClipMoment = {
  public_id: string;
  owner_user_id: string;
  source_public_id: string;
  transcript_public_id?: string | null;
  start_seconds: number;
  end_seconds: number;
  transcript_excerpt: string;
  moment_type: string;
  reason: string;
  confidence: number;
  created_at: string;
};

type BackendClipCandidate = {
  public_id: string;
  owner_user_id: string;
  source_public_id: string;
  transcript_public_id?: string | null;
  moment_public_id?: string | null;
  title: string;
  hook: string;
  caption: string;
  start_seconds: number;
  end_seconds: number;
  target_platform: string;
  status: ClipCandidate["status"];
  score_total: number;
  score_hook: number;
  score_retention: number;
  score_clarity: number;
  score_emotion: number;
  score_shareability: number;
  score_platform_fit: number;
  risk_notes: string[];
  render_asset_public_id?: string | null;
  created_at: string;
  updated_at: string;
};

type BackendClipPack = {
  public_id: string;
  owner_user_id: string;
  source_public_id: string;
  transcript_public_id?: string | null;
  title: string;
  target_platform: string;
  desired_clip_count: number;
  status: ClipPack["status"];
  selected_candidate_ids: string[];
  job_public_id?: string | null;
  created_at: string;
  updated_at: string;
};

type BackendClipPackDetail = {
  pack: BackendClipPack;
  moments: BackendClipMoment[];
  candidates: BackendClipCandidate[];
};

type BackendClipRenderContract = {
  public_id: string;
  owner_user_id: string;
  clip_candidate_public_id: string;
  source_public_id: string;
  output_format: string;
  aspect_ratio: string;
  resolution: string;
  remove_silence: boolean;
  captions_enabled: boolean;
  caption_style_json: string;
  music_enabled: boolean;
  music_policy: ClipRenderContract["musicPolicy"];
  intro_seconds: number;
  outro_seconds: number;
  render_job_public_id?: string | null;
  created_at: string;
};

function ensureApiBase() {
  if (!API_BASE) {
    throw new Error("Missing NEXT_PUBLIC_API_BASE_URL or NEXT_PUBLIC_BACKEND_URL");
  }
}

async function request<T>(path: string, init?: RequestInit, token?: string | null): Promise<T> {
  ensureApiBase();
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function listMyJobsWithAuth(token: string): Promise<WorldJob[]> {
  const result = await request<BackendWorldJob[]>("/worlds/jobs/me", undefined, token);
  if (!Array.isArray(result)) return [];
  return result.map(mapWorldJob);
}

function campaignStatus(value: string): MarketplaceCampaign["status"] {
  const allowed: MarketplaceCampaign["status"][] = [
    "draft",
    "pending_review",
    "open",
    "in_progress",
    "submitted",
    "under_review",
    "revision_requested",
    "completed",
    "cancelled",
    "disputed",
  ];
  return allowed.includes(value as MarketplaceCampaign["status"]) ? (value as MarketplaceCampaign["status"]) : "draft";
}

function submissionStatus(value: string): CampaignSubmission["status"] {
  const allowed: CampaignSubmission["status"][] = [
    "draft",
    "submitted",
    "under_review",
    "approved",
    "rejected",
    "revision_requested",
    "paid",
    "disputed",
  ];
  return allowed.includes(value as CampaignSubmission["status"]) ? (value as CampaignSubmission["status"]) : "draft";
}

function sourceType(value: string): MarketplaceCampaign["sourceType"] {
  const allowed: MarketplaceCampaign["sourceType"][] = ["video_url", "upload", "podcast", "livestream", "clip_pack"];
  return allowed.includes(value as MarketplaceCampaign["sourceType"]) ? (value as MarketplaceCampaign["sourceType"]) : "video_url";
}

function targetPlatform(value: string): MarketplaceCampaign["targetPlatform"] {
  const allowed: MarketplaceCampaign["targetPlatform"][] = ["TikTok", "Instagram", "YouTube", "Facebook", "Multi"];
  return allowed.includes(value as MarketplaceCampaign["targetPlatform"])
    ? (value as MarketplaceCampaign["targetPlatform"])
    : "Multi";
}

function integrationCategory(value: string): IntegrationCard["category"] {
  const allowed: IntegrationCard["category"][] = ["ai", "social", "payments", "storage", "blockchain", "platform"];
  return allowed.includes(value as IntegrationCard["category"]) ? (value as IntegrationCard["category"]) : "platform";
}

function integrationStatus(value: string): IntegrationCard["status"] {
  const allowed: IntegrationCard["status"][] = [
    "not_configured",
    "configured",
    "connected",
    "warning",
    "error",
    "disabled",
    "mocked",
  ];
  return allowed.includes(value as IntegrationCard["status"]) ? (value as IntegrationCard["status"]) : "not_configured";
}

function ledgerStatus(value: string): LedgerEntry["status"] {
  const allowed: LedgerEntry["status"][] = ["recorded", "pending", "reversed", "failed"];
  return allowed.includes(value as LedgerEntry["status"]) ? (value as LedgerEntry["status"]) : "recorded";
}

function mapCampaign(item: BackendCampaign): MarketplaceCampaign {
  return {
    id: item.public_id,
    title: item.title,
    description: item.description,
    buyerName: "LWA Buyer",
    sourceType: sourceType(item.source_type),
    targetPlatform: targetPlatform(item.target_platform),
    budget: item.budget,
    platformFeePercent: item.platform_fee_percent ?? 20,
    clipCount: item.clip_count,
    deadline: item.deadline || item.created_at,
    status: campaignStatus(item.status),
    requirements: [],
    rightsRequired: item.rights_required,
    createdAt: item.created_at,
    submissionsCount: 0,
    approvedSubmissionsCount: 0,
  };
}

function mapSubmission(item: BackendSubmission): CampaignSubmission {
  return {
    id: item.public_id,
    campaignId: item.campaign_public_id,
    clipperName: "LWA Clipper",
    title: item.title,
    hook: item.hook,
    caption: item.caption,
    assetUrl: item.asset_url || undefined,
    status: submissionStatus(item.status),
    estimatedEarnings: item.estimated_earnings,
    submittedAt: item.created_at,
    reviewNote: item.review_note || undefined,
  };
}

function mapUgcAsset(item: BackendUGCAsset): UGCAsset {
  return {
    id: item.public_id,
    creatorUserId: item.creator_user_id,
    title: item.title,
    assetType: item.asset_type,
    description: item.description,
    price: { amount: item.price_amount, currency: item.currency },
    status: item.status,
    moderationStatus: item.moderation_status,
    rightsConfirmed: item.rights_confirmed,
    licenseSummary: item.license_summary,
    previewUrl: item.preview_url || undefined,
    createdAt: item.created_at,
  };
}

function mapModerationItem(item: BackendModerationQueueItem): ModerationQueueItem {
  return {
    id: item.public_id,
    targetType: item.target_type,
    targetId: item.target_public_id,
    submittedBy: item.submitted_by_user_id || undefined,
    status: item.status,
    reason: item.reason,
    automatedScore: item.automated_score ?? undefined,
    reviewer: item.reviewer_user_id || undefined,
    reviewerNote: item.reviewer_note || undefined,
    createdAt: item.created_at,
    reviewedAt: item.reviewed_at || undefined,
  };
}

function mapFraudFlag(item: BackendFraudFlag): FraudFlag {
  return {
    id: item.public_id,
    userId: item.user_id || undefined,
    targetType: item.target_type,
    targetId: item.target_public_id || undefined,
    flagType: item.flag_type,
    status: item.status,
    severity: item.severity,
    evidence: item.evidence,
    reviewer: item.reviewer_user_id || undefined,
    reviewerNote: item.reviewer_note || undefined,
    createdAt: item.created_at,
    resolvedAt: item.resolved_at || undefined,
  };
}

function mapRightsClaim(item: BackendRightsClaim): ContentRightsClaim {
  return {
    id: item.public_id,
    claimantName: item.claimant_name,
    claimantEmail: item.claimant_email,
    targetType: item.target_type,
    targetId: item.target_public_id,
    claimSummary: item.claim_summary,
    status: item.status,
    adminNote: item.admin_note || undefined,
    createdAt: item.created_at,
    resolvedAt: item.resolved_at || undefined,
  };
}

function mapBillingPlan(item: BackendBillingPlan): BillingPlan {
  return {
    planKey: item.plan_key,
    name: item.name,
    monthlyPrice: { amount: Math.round(item.monthly_price_amount / 100), currency: item.currency },
    monthlyCredits: item.monthly_credits,
    marketplaceFeePercent: item.marketplace_fee_percent,
    maxCampaigns: item.max_campaigns,
    maxUgcAssets: item.max_ugc_assets,
    features: item.features,
  };
}

function mapEntitlement(item: BackendEntitlement): UserEntitlement {
  return {
    userId: item.user_id,
    planKey: item.plan_key,
    status: item.status,
    source: item.source,
    sourceReferenceId: item.source_reference_id || undefined,
    currentPeriodStart: item.current_period_start || undefined,
    currentPeriodEnd: item.current_period_end || undefined,
    createdAt: item.created_at,
    updatedAt: item.updated_at,
  };
}

function mapCreditBalance(item: BackendCreditBalance): CreditBalance {
  return {
    userId: item.user_id,
    balance: item.balance,
    monthlyGrant: item.monthly_grant,
    usedThisPeriod: item.used_this_period,
    periodStart: item.period_start || undefined,
    periodEnd: item.period_end || undefined,
    updatedAt: item.updated_at,
  };
}

function mapCreditTransaction(item: BackendCreditTransaction): CreditTransaction {
  return {
    id: item.public_id,
    userId: item.user_id,
    transactionType: item.transaction_type,
    amount: item.amount,
    balanceAfter: item.balance_after,
    reason: item.reason,
    sourceType: item.source_type || undefined,
    sourceId: item.source_public_id || undefined,
    createdAt: item.created_at,
  };
}

function mapEarningsAccount(item: BackendEarningsAccount): EarningsAccount {
  return {
    userId: item.user_id,
    estimatedAmount: item.estimated_amount,
    pendingReviewAmount: item.pending_review_amount,
    approvedAmount: item.approved_amount,
    payableAmount: item.payable_amount,
    paidAmount: item.paid_amount,
    heldAmount: item.held_amount,
    currency: item.currency,
    updatedAt: item.updated_at,
  };
}

function mapEarningEvent(item: BackendEarningEvent): EarningEvent {
  return {
    id: item.public_id,
    userId: item.user_id,
    sourceType: item.source_type,
    sourceId: item.source_public_id || undefined,
    amount: item.amount,
    platformFeeAmount: item.platform_fee_amount,
    netAmount: item.net_amount,
    currency: item.currency,
    status: item.status,
    note: item.note,
    createdAt: item.created_at,
  };
}

function mapPayoutPlaceholder(item: BackendPayoutPlaceholder): PayoutPlaceholder {
  return {
    id: item.public_id,
    userId: item.user_id,
    amount: item.amount,
    currency: item.currency,
    status: item.status,
    blockedReason: item.blocked_reason,
    createdAt: item.created_at,
    updatedAt: item.updated_at,
  };
}

function mapStripeReadiness(item: BackendStripeReadiness): StripeConnectReadiness {
  return {
    enabled: item.enabled,
    ready: item.ready,
    requiredEnvVars: item.required_env_vars,
    missingEnvVars: item.missing_env_vars,
    blockers: item.blockers,
    note: item.note,
  };
}

function mapWorldJob(item: BackendWorldJob): WorldJob {
  return {
    id: item.public_id,
    ownerUserId: item.owner_user_id || undefined,
    jobType: item.job_type,
    status: item.status,
    priority: item.priority,
    progressPercent: item.progress_percent,
    title: item.title,
    description: item.description,
    sourceId: item.source_public_id || undefined,
    targetType: item.target_type || undefined,
    targetId: item.target_public_id || undefined,
    inputJson: item.input_json,
    outputJson: item.output_json,
    errorMessage: item.error_message || undefined,
    maxAttempts: item.max_attempts,
    attemptCount: item.attempt_count,
    nextRetryAt: item.next_retry_at || undefined,
    startedAt: item.started_at || undefined,
    completedAt: item.completed_at || undefined,
    createdAt: item.created_at,
    updatedAt: item.updated_at,
  };
}

function mapWorldJobEvent(item: BackendWorldJobEvent): WorldJobEvent {
  return {
    id: item.public_id,
    jobId: item.job_public_id,
    eventType: item.event_type,
    message: item.message,
    statusBefore: item.status_before || undefined,
    statusAfter: item.status_after || undefined,
    progressPercent: item.progress_percent ?? undefined,
    metadataJson: item.metadata_json,
    createdAt: item.created_at,
  };
}

export async function getWorldsHealth() {
  return request<{ status: string; service: string; phase: string }>("/worlds/health");
}

export async function listPlans(): Promise<BillingPlan[]> {
  const result = await request<BackendBillingPlan[]>("/worlds/billing/plans");
  if (!Array.isArray(result)) {
    throw new Error("Malformed billing plans response");
  }
  return result.map(mapBillingPlan);
}

export async function getMyEntitlement(): Promise<UserEntitlement> {
  return mapEntitlement(await request<BackendEntitlement>("/worlds/billing/entitlement/me"));
}

export async function getMyCredits(): Promise<CreditBalance> {
  return mapCreditBalance(await request<BackendCreditBalance>("/worlds/credits/me"));
}

export async function listMyCreditTransactions(): Promise<CreditTransaction[]> {
  const result = await request<BackendCreditTransaction[]>("/worlds/credits/transactions/me");
  if (!Array.isArray(result)) {
    throw new Error("Malformed credit transaction response");
  }
  return result.map(mapCreditTransaction);
}

export async function spendCredits(payload: {
  amount: number;
  feature_key: string;
  reason?: string;
  source_type?: string;
  source_public_id?: string;
}): Promise<CreditBalance> {
  return mapCreditBalance(
    await request<BackendCreditBalance>("/worlds/credits/spend", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  );
}

export async function quoteMarketplaceFee(payload: { gross_amount: number; plan_key?: string }) {
  return request<{
    gross_amount: number;
    platform_fee_percent: number;
    platform_fee_amount: number;
    net_amount: number;
    currency: "USD";
    note: string;
  }>("/worlds/marketplace/fee-quote", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getMyEarningsAccount(): Promise<EarningsAccount> {
  return mapEarningsAccount(await request<BackendEarningsAccount>("/worlds/earnings/account/me"));
}

export async function listMyEarningEvents(): Promise<EarningEvent[]> {
  const result = await request<BackendEarningEvent[]>("/worlds/earnings/events/me");
  if (!Array.isArray(result)) {
    throw new Error("Malformed earning event response");
  }
  return result.map(mapEarningEvent);
}

export async function createPayoutPlaceholder(payload: { amount: number; reason?: string }): Promise<PayoutPlaceholder> {
  return mapPayoutPlaceholder(
    await request<BackendPayoutPlaceholder>("/worlds/payouts/placeholders", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  );
}

export async function listMyPayoutPlaceholders(): Promise<PayoutPlaceholder[]> {
  const result = await request<BackendPayoutPlaceholder[]>("/worlds/payouts/placeholders/me");
  if (!Array.isArray(result)) {
    throw new Error("Malformed payout placeholder response");
  }
  return result.map(mapPayoutPlaceholder);
}

export async function getStripeConnectReadiness(): Promise<StripeConnectReadiness> {
  return mapStripeReadiness(
    await request<BackendStripeReadiness>("/worlds/payouts/stripe-connect/readiness"),
  );
}

export async function createWorldJob(payload: {
  job_type: string;
  title?: string;
  description?: string;
  priority?: string;
  source_public_id?: string;
  target_type?: string;
  target_public_id?: string;
  input_json?: string;
}): Promise<WorldJob> {
  return mapWorldJob(
    await request<BackendWorldJob>("/worlds/jobs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  );
}

export async function listMyWorldJobs(): Promise<WorldJob[]> {
  const result = await request<BackendWorldJob[]>("/worlds/jobs/me");
  if (!Array.isArray(result)) {
    throw new Error("Malformed jobs response");
  }
  return result.map(mapWorldJob);
}

export async function getWorldJob(jobId: string): Promise<WorldJob> {
  return mapWorldJob(await request<BackendWorldJob>(`/worlds/jobs/${jobId}`));
}

export async function listWorldJobEvents(jobId: string): Promise<WorldJobEvent[]> {
  const result = await request<BackendWorldJobEvent[]>(`/worlds/jobs/${jobId}/events`);
  if (!Array.isArray(result)) {
    throw new Error("Malformed job events response");
  }
  return result.map(mapWorldJobEvent);
}

export async function cancelWorldJob(jobId: string, reason: string): Promise<WorldJob> {
  return mapWorldJob(
    await request<BackendWorldJob>(`/worlds/jobs/${jobId}/cancel`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),
  );
}

export async function retryWorldJob(jobId: string, reason: string): Promise<WorldJob> {
  return mapWorldJob(
    await request<BackendWorldJob>(`/worlds/jobs/${jobId}/retry`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),
  );
}

export async function getWorldJobDashboard(): Promise<WorldJobDashboard> {
  const result = await request<BackendWorldJobDashboard>("/worlds/jobs/admin/dashboard");
  return {
    queued: result.queued,
    running: result.running,
    succeeded: result.succeeded,
    failed: result.failed,
    retrying: result.retrying,
    cancelled: result.cancelled,
    recentJobs: result.recent_jobs.map(mapWorldJob),
  };
}

export async function listCampaigns(): Promise<MarketplaceCampaign[]> {
  const result = await request<BackendCampaign[]>("/worlds/marketplace/campaigns");
  if (!Array.isArray(result)) {
    throw new Error("Malformed campaign response");
  }
  return result.map(mapCampaign);
}

export async function getCampaign(id: string): Promise<MarketplaceCampaign> {
  return mapCampaign(await request<BackendCampaign>(`/worlds/marketplace/campaigns/${id}`));
}

export async function createCampaign(payload: {
  title: string;
  description: string;
  target_platform: string;
  source_type: string;
  budget_amount: number;
  clip_count: number;
  rights_required?: string;
}) {
  return mapCampaign(
    await request<BackendCampaign>("/worlds/marketplace/campaigns", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  );
}

export async function listSubmissions(): Promise<CampaignSubmission[]> {
  const result = await request<BackendSubmission[]>("/worlds/marketplace/submissions");
  if (!Array.isArray(result)) {
    throw new Error("Malformed submission response");
  }
  return result.map(mapSubmission);
}

export async function createSubmission(payload: {
  campaign_public_id: string;
  title: string;
  hook?: string;
  caption?: string;
  asset_url?: string;
  estimated_earnings_amount?: number;
  rights_confirmed: boolean;
}) {
  return mapSubmission(
    await request<BackendSubmission>("/worlds/marketplace/submissions", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  );
}

export async function reviewSubmission(id: string, payload: { action: string; review_note?: string }) {
  return mapSubmission(
    await request<BackendSubmission>(`/worlds/marketplace/submissions/${id}/review`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  );
}

export async function listUgcAssets(): Promise<UGCAsset[]> {
  const result = await request<BackendUGCAsset[]>("/worlds/ugc/assets");
  if (!Array.isArray(result)) {
    throw new Error("Malformed UGC asset response");
  }
  return result.map(mapUgcAsset);
}

export async function createUgcAsset(payload: {
  title: string;
  asset_type: string;
  description: string;
  price_amount?: number;
  license_summary?: string;
  preview_url?: string;
  rights_confirmed: boolean;
}) {
  return mapUgcAsset(
    await request<BackendUGCAsset>("/worlds/ugc/assets", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  );
}

export async function listModerationQueue(): Promise<ModerationQueueItem[]> {
  const result = await request<BackendModerationQueueItem[]>("/worlds/admin/moderation");
  if (!Array.isArray(result)) {
    throw new Error("Malformed moderation response");
  }
  return result.map(mapModerationItem);
}

export async function listFraudFlags(): Promise<FraudFlag[]> {
  const result = await request<BackendFraudFlag[]>("/worlds/admin/fraud");
  if (!Array.isArray(result)) {
    throw new Error("Malformed fraud response");
  }
  return result.map(mapFraudFlag);
}

export async function listRightsClaims(): Promise<ContentRightsClaim[]> {
  const result = await request<BackendRightsClaim[]>("/worlds/admin/rights/claims");
  if (!Array.isArray(result)) {
    throw new Error("Malformed rights claim response");
  }
  return result.map(mapRightsClaim);
}

export type AdminAuditEntry = {
  public_id: string;
  actor_user_id: string | null;
  action_type: string;
  target_type: string;
  target_public_id: string | null;
  before_state: string | null;
  after_state: string | null;
  note: string | null;
  created_at: string;
};

export async function listAuditLog(): Promise<AdminAuditEntry[]> {
  const result = await request<AdminAuditEntry[]>("/worlds/admin/audit-log");
  if (!Array.isArray(result)) throw new Error("Malformed audit log response");
  return result;
}

export async function getMyWorldProfile(): Promise<UserWorldProfile> {
  const result = await request<{
    user_id: string;
    display_name: string;
    class_name: UserWorldProfile["className"];
    faction: UserWorldProfile["faction"];
    level: number;
    xp: number;
    next_level_xp: number;
    creator_reputation: number;
    clipper_reputation: number;
    marketplace_reputation: number;
  }>("/worlds/profile/me");

  return {
    id: result.user_id,
    displayName: result.display_name,
    className: result.class_name,
    faction: result.faction,
    level: result.level,
    xp: result.xp,
    nextLevelXp: result.next_level_xp,
    creatorReputation: result.creator_reputation,
    clipperReputation: result.clipper_reputation,
    marketplaceReputation: result.marketplace_reputation,
    badges: [],
    relics: [],
    titles: [],
  };
}

export async function getMyLedger(): Promise<LedgerEntry[]> {
  const result = await request<
    Array<{
      public_id: string;
      event_type: LedgerEntry["type"];
      label: string;
      amount?: number | null;
      currency: "USD";
      xp?: number | null;
      reputation?: number | null;
      status: string;
      reference_id?: string | null;
      created_at: string;
    }>
  >("/worlds/ledger/me");

  if (!Array.isArray(result)) {
    throw new Error("Malformed ledger response");
  }

  return result.map((item) => ({
    id: item.public_id,
    type: item.event_type,
    label: item.label,
    amount: typeof item.amount === "number" ? { amount: item.amount, currency: item.currency } : undefined,
    xp: item.xp || undefined,
    reputation: item.reputation || undefined,
    createdAt: item.created_at,
    status: ledgerStatus(item.status),
    referenceId: item.reference_id || undefined,
  }));
}

export async function getIntegrations(): Promise<IntegrationCard[]> {
  const result = await request<
    Array<{
      integration_key: string;
      name: string;
      category: string;
      status: string;
      description: string;
      admin_only: boolean;
    }>
  >("/worlds/integrations");

  if (!Array.isArray(result)) {
    throw new Error("Malformed integrations response");
  }

  return result.map((item) => ({
    id: item.integration_key,
    name: item.name,
    category: integrationCategory(item.category),
    status: integrationStatus(item.status),
    description: item.description,
    envVars: [],
    adminOnly: item.admin_only,
  }));
}

type BackendUserBadge = {
  badge_public_id: string;
  name: string;
  tier: string;
  description: string;
  lore: string;
  unlocked_at: string;
};

type BackendUserRelic = {
  relic_public_id: string;
  name: string;
  tier: string;
  description: string;
  lore: string;
  future_collectible_eligible: boolean;
  unlocked_at: string;
};

type BackendQuestResponse = {
  public_id: string;
  title: string;
  description: string;
  category: string;
  goal: number;
  reward_xp: number;
  reward_badge_public_id: string | null;
  active: boolean;
};

type BackendQuestCompletion = {
  quest_public_id: string;
  progress: number;
  status: string;
};

function badgeTier(value: string): import("./types").Badge["tier"] {
  const allowed = ["common", "rare", "epic", "mythic", "founder"] as const;
  return (allowed as readonly string[]).includes(value) ? (value as import("./types").Badge["tier"]) : "common";
}

function questCategory(value: string): import("./types").Quest["category"] {
  const allowed = ["daily", "weekly", "clipping", "marketplace", "ugc", "faction", "founder", "seasonal"] as const;
  return (allowed as readonly string[]).includes(value)
    ? (value as import("./types").Quest["category"])
    : "clipping";
}

function questStatus(value: string): import("./types").Quest["status"] {
  const allowed = ["available", "in_progress", "completed", "claimed"] as const;
  return (allowed as readonly string[]).includes(value)
    ? (value as import("./types").Quest["status"])
    : "available";
}

export async function getMyBadges(): Promise<import("./types").Badge[]> {
  const result = await request<BackendUserBadge[]>("/worlds/badges/me");
  if (!Array.isArray(result)) return [];
  return result.map((b) => ({
    id: b.badge_public_id,
    name: b.name,
    tier: badgeTier(b.tier),
    description: b.description,
    lore: b.lore,
    unlockedAt: b.unlocked_at,
  }));
}

export async function getMyRelics(): Promise<import("./types").Badge[]> {
  const result = await request<BackendUserRelic[]>("/worlds/relics/me");
  if (!Array.isArray(result)) return [];
  return result.map((r) => ({
    id: r.relic_public_id,
    name: r.name,
    tier: badgeTier(r.tier),
    description: r.description,
    lore: r.lore,
    unlockedAt: r.unlocked_at,
  }));
}

export async function claimQuest(questId: string, token: string): Promise<{ status: string; xp_awarded?: number }> {
  const result = await request<{ status: string; xp_awarded?: number }>(
    `/worlds/quests/${encodeURIComponent(questId)}/claim`,
    { method: "POST", headers: { Authorization: `Bearer ${token}` } },
  );
  return result;
}

export async function listQuests(): Promise<import("./types").Quest[]> {
  const [questDefs, completions] = await Promise.all([
    request<BackendQuestResponse[]>("/worlds/quests"),
    request<BackendQuestCompletion[]>("/worlds/quests/me").catch(() => [] as BackendQuestCompletion[]),
  ]);

  if (!Array.isArray(questDefs)) return [];

  const progressMap = new Map<string, BackendQuestCompletion>(
    (Array.isArray(completions) ? completions : []).map((c) => [c.quest_public_id, c]),
  );

  return questDefs
    .filter((q) => q.active)
    .map((q) => {
      const completion = progressMap.get(q.public_id);
      return {
        id: q.public_id,
        title: q.title,
        description: q.description,
        category: questCategory(q.category),
        progress: completion?.progress ?? 0,
        goal: q.goal,
        rewardXp: q.reward_xp,
        status: completion ? questStatus(completion.status) : ("available" as const),
      };
    });
}
