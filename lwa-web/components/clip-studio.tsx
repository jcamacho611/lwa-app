"use client";

import Link from "next/link";
import { ChangeEvent, FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { AccountWorkspace } from "./account-workspace";
import { AuthPanel } from "./auth-panel";
import { BatchPanel } from "./batch-panel";
import { CampaignPanel } from "./campaign-panel";
import { ClipCard } from "./clip-card";
import { ClipPackEditor, ClipPatchPayload } from "./clip-pack-editor";
import { FeatureGatePanel } from "./feature-gate-panel";
import { HistoryPanel } from "./history-panel";
import Navbar from "./Navbar";
import { PostingPanel } from "./posting-panel";
import { ReadyQueuePanel } from "./ready-queue-panel";
import { SettingsPanel } from "./settings-panel";
import { WalletPanel } from "./wallet-panel";
import {
  BatchSummary,
  CampaignAssignment,
  CampaignDetail,
  CampaignSummary,
  ClipPackDetail,
  ClipResult,
  ClipPackSummary,
  FeatureFlags,
  GenerateResponse,
  PlatformOption,
  PostingConnection,
  ScheduledPost,
  UploadAsset,
  UserProfile,
  WalletLedgerEntry,
  WalletSummary,
  WorkspaceRole,
} from "../lib/types";
import {
  ApiError,
  createBatch,
  createCampaignAssignments,
  createCampaign,
  createPayoutRequest,
  createPostingConnection,
  createScheduledPost,
  generateClips,
  loadBatches,
  loadCampaign,
  loadCampaigns,
  loadClipPack,
  loadClipPacks,
  loadMe,
  loadPostingConnections,
  loadScheduledPosts,
  loadUploads,
  loadWallet,
  loadWalletLedger,
  logOut,
  patchClip,
  updateCampaign,
  updateCampaignAssignment,
  updateScheduledPost,
  uploadSource,
} from "../lib/api";
import { clearStoredToken, readStoredToken, storeToken } from "../lib/auth";
import {
  applyPreferenceBoost,
  buildPreferenceProfile,
  createFeedbackRecord,
  readFeedbackRecords,
  readImproveResultsPreference,
  type ClipFeedbackRecord,
  upsertFeedbackRecord,
  writeImproveResultsPreference,
} from "../lib/feedback";
import {
  clearReadyQueue,
  createReadyQueueItem,
  moveReadyQueueItem,
  readReadyQueue,
  removeReadyQueueItem,
  type ReadyQueueItem,
  upsertReadyQueueItem,
} from "../lib/queue";
import { getPlanSurface } from "../lib/plans";

const platforms: PlatformOption[] = ["TikTok", "Instagram Reels", "YouTube Shorts"];

const appNavItems = [
  { href: "/dashboard", label: "Dashboard", section: "dashboard" },
  { href: "/generate", label: "Generate", section: "generate" },
  { href: "/upload", label: "Upload", section: "upload" },
  { href: "/history", label: "History", section: "history" },
  { href: "/batches", label: "Batches", section: "batches" },
  { href: "/campaigns", label: "Campaigns", section: "campaigns" },
  { href: "/wallet", label: "Wallet", section: "wallet" },
  { href: "/settings", label: "Settings", section: "settings" },
] as const;

const marketingNavItems = [
  { href: "/generate", label: "Generate" },
  { href: "/history", label: "History" },
  { href: "/campaigns", label: "Campaigns" },
] as const;

type StudioSection =
  | "home"
  | "dashboard"
  | "generate"
  | "upload"
  | "history"
  | "batches"
  | "campaigns"
  | "wallet"
  | "settings";

type ClipStudioProps = {
  initialSection?: StudioSection;
  autoOpenAuth?: boolean;
  initialAuthMode?: "login" | "signup";
  pageLabel?: string;
  pageTitle?: string;
  pageDescription?: string;
};

export function ClipStudio({
  initialSection = "home",
  autoOpenAuth = false,
  initialAuthMode = "login",
  pageLabel,
  pageTitle,
  pageDescription,
}: ClipStudioProps) {
  const [videoUrl, setVideoUrl] = useState("");
  const [platform, setPlatform] = useState<PlatformOption>("TikTok");
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "signup">(initialAuthMode);
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [wallet, setWallet] = useState<WalletSummary | null>(null);
  const [walletLedger, setWalletLedger] = useState<WalletLedgerEntry[]>([]);
  const [clipPacks, setClipPacks] = useState<ClipPackSummary[]>([]);
  const [uploads, setUploads] = useState<UploadAsset[]>([]);
  const [batches, setBatches] = useState<BatchSummary[]>([]);
  const [campaigns, setCampaigns] = useState<CampaignSummary[]>([]);
  const [selectedCampaignId, setSelectedCampaignId] = useState<string | null>(null);
  const [selectedCampaign, setSelectedCampaign] = useState<CampaignDetail | null>(null);
  const [isCampaignLoading, setIsCampaignLoading] = useState(false);
  const [postingConnections, setPostingConnections] = useState<PostingConnection[]>([]);
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([]);
  const [selectedClipPackId, setSelectedClipPackId] = useState<string | null>(null);
  const [selectedClipPack, setSelectedClipPack] = useState<ClipPackDetail | null>(null);
  const [isClipPackLoading, setIsClipPackLoading] = useState(false);
  const [isAccountLoading, setIsAccountLoading] = useState(false);
  const [accountError, setAccountError] = useState<string | null>(null);
  const [uploadingFileName, setUploadingFileName] = useState<string | null>(null);
  const [selectedUpload, setSelectedUpload] = useState<UploadAsset | null>(null);
  const [feedbackRecords, setFeedbackRecords] = useState<ClipFeedbackRecord[]>([]);
  const [improveResults, setImproveResults] = useState(false);
  const [readyQueue, setReadyQueue] = useState<ReadyQueueItem[]>([]);
  const [paywallMessage, setPaywallMessage] = useState<string | null>(null);
  const [loadingStageIndex, setLoadingStageIndex] = useState(0);

  const activeSourceLabel = useMemo(() => {
    if (selectedUpload?.file_name || selectedUpload?.filename) {
      return `Using upload: ${selectedUpload.file_name || selectedUpload.filename}`;
    }
    if (videoUrl.trim()) {
      return "Using pasted URL";
    }
    return "No source selected";
  }, [selectedUpload, videoUrl]);

  const pageIntro = useMemo(() => {
    if (pageTitle || pageDescription || pageLabel) {
      return {
        label: pageLabel || "Workspace",
        title: pageTitle || "LWA workspace",
        description: pageDescription || "Run the product from any browser.",
      };
    }

    switch (initialSection) {
      case "dashboard":
        return {
          label: "Dashboard",
          title: "Your control room",
          description: "Runs, queue, campaigns, and account state in one place.",
        };
      case "generate":
        return {
          label: "Generate",
          title: "Build a ranked clip pack",
          description: "Paste a source. Get clips worth posting.",
        };
      case "upload":
        return {
          label: "Upload",
          title: "Bring your own file",
          description: "Run the same flow with local video, audio, or images.",
        };
      case "history":
        return {
          label: "History",
          title: "Reopen saved work",
          description: "Review past packs and reopen what still hits.",
        };
      case "batches":
        return {
          label: "Batches",
          title: "Queue multiple sources",
          description: "Group links and uploads into one repeatable run.",
        };
      case "campaigns":
        return {
          label: "Campaigns",
          title: "Run content pushes",
          description: "Assign clips, track status, and keep ops moving.",
        };
      case "wallet":
        return {
          label: "Wallet",
          title: "Track value and payout state",
          description: "See ledger movement, readiness, and payout requests.",
        };
      case "settings":
        return {
          label: "Settings",
          title: "Manage account and workflow",
          description: "Plan, credits, role, and unlocked workflow depth.",
        };
      default:
        return null;
    }
  }, [initialSection, pageDescription, pageLabel, pageTitle]);

  useEffect(() => {
    const existingToken = readStoredToken();
    if (existingToken) {
      setToken(existingToken);
    }
    setFeedbackRecords(readFeedbackRecords());
    setImproveResults(readImproveResultsPreference());
    setReadyQueue(readReadyQueue());
  }, []);

  useEffect(() => {
    function syncQueue() {
      setReadyQueue(readReadyQueue());
    }

    window.addEventListener("storage", syncQueue);
    return () => window.removeEventListener("storage", syncQueue);
  }, []);

  useEffect(() => {
    writeImproveResultsPreference(improveResults);
  }, [improveResults]);

  useEffect(() => {
    if (autoOpenAuth && !token) {
      setAuthMode(initialAuthMode);
      setAuthOpen(true);
    }
  }, [autoOpenAuth, initialAuthMode, token]);

  useEffect(() => {
    if (!token) {
      setUser(null);
      setWallet(null);
      setWalletLedger([]);
      setClipPacks([]);
      setUploads([]);
      setBatches([]);
      setCampaigns([]);
      setSelectedCampaign(null);
      setSelectedCampaignId(null);
      setPostingConnections([]);
      setScheduledPosts([]);
      return;
    }
    void refreshAccount(token);
  }, [token]);

  useEffect(() => {
    if (!isLoading) {
      setLoadingStageIndex(0);
      return;
    }

    const interval = window.setInterval(() => {
      setLoadingStageIndex((current) => (current + 1) % 5);
    }, 1400);

    return () => window.clearInterval(interval);
  }, [isLoading]);

  useEffect(() => {
    if (initialSection !== "campaigns" || !token || !campaigns.length || selectedCampaignId) {
      return;
    }
    void openCampaign(campaigns[0].id);
  }, [campaigns, initialSection, selectedCampaignId, token]);

  async function refreshAccount(authToken: string) {
    setIsAccountLoading(true);
    setAccountError(null);

    try {
      const me = await loadMe(authToken);
      setUser(me);
    } catch (refreshError) {
      const message = refreshError instanceof Error ? refreshError.message : "Unable to load account.";
      setAccountError(message);
      clearStoredToken();
      setToken(null);
      setIsAccountLoading(false);
      return;
    }

    const results = await Promise.allSettled([
      loadWallet(authToken),
      loadWalletLedger(authToken),
      loadClipPacks(authToken),
      loadUploads(authToken),
      loadBatches(authToken),
      loadCampaigns(authToken),
      loadPostingConnections(authToken),
      loadScheduledPosts(authToken),
    ]);

    const failures: string[] = [];

    const [
      walletResult,
      ledgerResult,
      clipPacksResult,
      uploadsResult,
      batchesResult,
      campaignsResult,
      connectionsResult,
      scheduledResult,
    ] = results;

    if (walletResult.status === "fulfilled") {
      setWallet(walletResult.value);
    } else {
      failures.push(walletResult.reason instanceof Error ? walletResult.reason.message : "Wallet unavailable.");
    }

    if (ledgerResult.status === "fulfilled") {
      setWalletLedger(ledgerResult.value);
    } else {
      failures.push(ledgerResult.reason instanceof Error ? ledgerResult.reason.message : "Ledger unavailable.");
    }

    if (clipPacksResult.status === "fulfilled") {
      setClipPacks(clipPacksResult.value);
    } else {
      failures.push(clipPacksResult.reason instanceof Error ? clipPacksResult.reason.message : "History unavailable.");
    }

    if (uploadsResult.status === "fulfilled") {
      setUploads(uploadsResult.value);
    } else {
      failures.push(uploadsResult.reason instanceof Error ? uploadsResult.reason.message : "Uploads unavailable.");
    }

    if (batchesResult.status === "fulfilled") {
      setBatches(batchesResult.value);
    } else {
      failures.push(batchesResult.reason instanceof Error ? batchesResult.reason.message : "Batches unavailable.");
    }

    if (campaignsResult.status === "fulfilled") {
      setCampaigns(campaignsResult.value);
    } else {
      failures.push(campaignsResult.reason instanceof Error ? campaignsResult.reason.message : "Campaigns unavailable.");
    }

    if (connectionsResult.status === "fulfilled") {
      setPostingConnections(connectionsResult.value);
    } else {
      failures.push(connectionsResult.reason instanceof Error ? connectionsResult.reason.message : "Posting connections unavailable.");
    }

    if (scheduledResult.status === "fulfilled") {
      setScheduledPosts(scheduledResult.value);
    } else {
      failures.push(scheduledResult.reason instanceof Error ? scheduledResult.reason.message : "Posting queue unavailable.");
    }

    setAccountError(failures.length ? failures[0] : null);
    setIsAccountLoading(false);
  }

  async function openClipPack(requestId: string) {
    if (!token) {
      return;
    }
    setSelectedClipPackId(requestId);
    setIsClipPackLoading(true);
    setAccountError(null);
    try {
      const payload = await loadClipPack(token, requestId);
      setSelectedClipPack(payload);
    } catch (loadError) {
      setAccountError(loadError instanceof Error ? loadError.message : "Unable to load clip pack.");
    } finally {
      setIsClipPackLoading(false);
    }
  }

  async function openCampaign(campaignId: string) {
    if (!token) {
      return;
    }
    setSelectedCampaignId(campaignId);
    setIsCampaignLoading(true);
    setAccountError(null);
    try {
      const payload = await loadCampaign(token, campaignId);
      setSelectedCampaign(payload);
    } catch (loadError) {
      setAccountError(loadError instanceof Error ? loadError.message : "Unable to load campaign detail.");
    } finally {
      setIsCampaignLoading(false);
    }
  }

  async function saveClipMetadata(clipId: string, updates: ClipPatchPayload) {
    if (!token || !selectedClipPackId) {
      return;
    }
    await patchClip(token, clipId, updates);
    const refreshed = await loadClipPack(token, selectedClipPackId);
    setSelectedClipPack(refreshed);
    await refreshAccount(token);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!videoUrl.trim() && !selectedUpload?.file_id && !selectedUpload?.source_ref?.upload_id) {
      setError("Paste a public source URL or upload a file to generate your clip pack.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setPaywallMessage(null);

    try {
      const data = await generateClips(
        {
          url: videoUrl.trim() || undefined,
          platform,
          uploadFileId: selectedUpload?.file_id || selectedUpload?.source_ref?.upload_id,
          contentAngle: improveResults ? preferenceProfile.topPackagingAngle : undefined,
        },
        token,
      );
      setResult(data);
      setPaywallMessage(null);
      if (token) {
        await refreshAccount(token);
      }
    } catch (submitError) {
      setResult(null);
      if (submitError instanceof ApiError && submitError.status === 402) {
        setError(null);
        setPaywallMessage(submitError.message);
      } else {
        setError(submitError instanceof Error ? submitError.message : "Unable to generate clips right now.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  async function onSignOut() {
    if (token) {
      try {
        await logOut(token);
      } catch {
        // Keep client logout resilient.
      }
    }
    clearStoredToken();
    setToken(null);
    setUser(null);
    setSelectedUpload(null);
    setSelectedClipPack(null);
    setSelectedClipPackId(null);
  }

  async function onUploadSelected(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    if (!token) {
      setAuthMode("login");
      setAuthOpen(true);
      return;
    }
    setUploadingFileName(file.name);
    setError(null);
    try {
      const upload = await uploadSource(file, token);
      setSelectedUpload(upload);
      await refreshAccount(token);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Unable to upload that file right now.");
    } finally {
      setUploadingFileName(null);
      event.target.value = "";
    }
  }

  async function handleBatchCreate(payload: {
    title: string;
    target_platform: string;
    selected_trend?: string;
    sources: Array<{ source_kind: "url" | "upload"; video_url?: string; upload_id?: string }>;
  }) {
    if (!token) {
      setAuthMode("login");
      setAuthOpen(true);
      throw new Error("Sign in to create a batch.");
    }
    await createBatch(token, payload);
    await refreshAccount(token);
  }

  async function handleCampaignCreate(payload: {
    title: string;
    description?: string;
    allowed_platforms: string[];
    target_angle?: string;
    requirements?: string;
    payout_cents_per_1000_views?: number;
  }) {
    if (!token) {
      setAuthMode("login");
      setAuthOpen(true);
      throw new Error("Sign in to create a campaign.");
    }
    const created = await createCampaign(token, payload);
    await refreshAccount(token);
    await openCampaign(created.id);
  }

  async function handleCampaignStatusUpdate(campaignId: string, status: string) {
    if (!token) {
      throw new Error("Authentication required.");
    }
    await updateCampaign(token, campaignId, { status });
    await refreshAccount(token);
    await openCampaign(campaignId);
  }

  async function handleCampaignAssignmentCreate(campaignId: string, payload: {
    request_id?: string;
    clip_ids?: string[];
    target_platform?: string;
    packaging_angle?: string;
    assignee_role?: string;
    assignee_label?: string;
    note?: string;
    payout_amount_cents?: number;
  }) {
    if (!token) {
      throw new Error("Authentication required.");
    }
    await createCampaignAssignments(token, campaignId, payload);
    await refreshAccount(token);
    await openCampaign(campaignId);
  }

  async function handleCampaignAssignmentUpdate(
    campaignId: string,
    assignmentId: string,
    payload: {
      status?: string;
      assignee_role?: string;
      assignee_label?: string;
      note?: string;
      payout_amount_cents?: number;
    },
  ) {
    if (!token) {
      throw new Error("Authentication required.");
    }
    await updateCampaignAssignment(token, campaignId, assignmentId, payload);
    await refreshAccount(token);
    await openCampaign(campaignId);
  }

  async function handlePayoutRequest(amountCents: number) {
    if (!token) {
      throw new Error("Authentication required.");
    }
    const payout = await createPayoutRequest(token, amountCents);
    await refreshAccount(token);
    return payout;
  }

  async function handleCreatePostingConnection(payload: { provider: string; account_label?: string }) {
    if (!token) {
      throw new Error("Authentication required.");
    }
    await createPostingConnection(token, payload);
    await refreshAccount(token);
  }

  async function handleCreateScheduledPost(payload: {
    clip_id: string;
    provider: string;
    caption?: string;
    scheduled_for?: string;
  }) {
    if (!token) {
      throw new Error("Authentication required.");
    }
    await createScheduledPost(token, payload);
    await refreshAccount(token);
  }

  async function handleUpdateScheduledPost(postId: string, payload: { status?: string; caption?: string; scheduled_for?: string }) {
    if (!token) {
      throw new Error("Authentication required.");
    }
    await updateScheduledPost(token, postId, payload);
    await refreshAccount(token);
  }

  const preferenceProfile = useMemo(() => buildPreferenceProfile(feedbackRecords), [feedbackRecords]);
  const displayedClips = useMemo(
    () => applyPreferenceBoost(result?.clips || [], preferenceProfile, improveResults),
    [improveResults, preferenceProfile, result?.clips],
  );
  const feedbackByClipId = useMemo(
    () =>
      feedbackRecords.reduce<Record<string, "good" | "bad">>((accumulator, item) => {
        accumulator[item.clipId] = item.vote;
        return accumulator;
      }, {}),
    [feedbackRecords],
  );
  const planSurface = useMemo(
    () => getPlanSurface(user?.plan_code, result?.processing_summary?.feature_flags as FeatureFlags | undefined),
    [result?.processing_summary?.feature_flags, user?.plan_code],
  );
  const activeFeatureFlags = planSurface.featureFlags;
  const visibleAppNavItems = useMemo(
    () =>
      appNavItems.filter((item) => {
        if (item.section === "campaigns" && !activeFeatureFlags.campaign_mode) {
          return false;
        }
        if (item.section === "wallet" && !activeFeatureFlags.wallet_view) {
          return false;
        }
        return true;
      }),
    [activeFeatureFlags.campaign_mode, activeFeatureFlags.wallet_view],
  );
  const planLimits = {
    clipLimit: activeFeatureFlags.clip_limit || 0,
    generationsPerDay: activeFeatureFlags.max_generations_per_day || 0,
    uploadsPerDay: activeFeatureFlags.max_uploads_per_day || 0,
  };
  const creditsRemaining = result?.processing_summary?.credits_remaining;
  const editorUnlocked = Boolean(activeFeatureFlags.caption_editor || activeFeatureFlags.timeline_editor);
  const campaignsUnlocked = Boolean(activeFeatureFlags.campaign_mode);
  const walletUnlocked = Boolean(activeFeatureFlags.wallet_view);
  const postingQueueUnlocked = Boolean(activeFeatureFlags.posting_queue);

  const isHome = initialSection === "home";
  const featuredClip = displayedClips[0] ?? null;
  const remainingClips = displayedClips.slice(1);
  const requiresAccount = !["home", "generate", "upload"].includes(initialSection);
  const showGenerator = ["home", "generate", "upload"].includes(initialSection);
  const showDashboard = ["dashboard"].includes(initialSection);
  const showHistory = initialSection === "history";
  const showBatches = initialSection === "batches";
  const showCampaigns = initialSection === "campaigns";
  const showWallet = initialSection === "wallet";
  const showSettings = initialSection === "settings";
  const showPostingOnDashboard = initialSection === "dashboard";
  const topAngles = (preferenceProfile.preferredAngles.length
    ? preferenceProfile.preferredAngles
    : displayedClips.map((clip) => clip.packaging_angle).filter(Boolean)) as string[];
  const featureProof = ["Ranked", "Queue-ready", "Campaign flow"];
  const loadingStages = [
    "Reading source",
    "Pulling media",
    "Understanding content",
    "Finding clips",
    "Packaging outputs",
  ];
  const sourceTruthSummary = useMemo(() => {
    const content = result?.transcript || result?.visual_summary || "This source was processed into ranked short-form outputs.";
    if (!content) {
      return null;
    }
    return content.length > 260 ? `${content.slice(0, 257).trimEnd()}...` : content;
  }, [result?.transcript, result?.visual_summary]);

  function handleFeedbackVote(clip: GenerateResponse["clips"][number], vote: "good" | "bad") {
    setFeedbackRecords((current) => upsertFeedbackRecord(current, createFeedbackRecord(clip, vote, platform)));
  }

  function resolveClipQueueId(clip: ClipResult) {
    return clip.record_id || clip.clip_id || clip.id;
  }

  function isQueued(clip: ClipResult) {
    const clipId = resolveClipQueueId(clip);
    return readyQueue.some((item) => item.clipId === clipId);
  }

  function handleToggleQueue(clip: ClipResult) {
    const clipId = resolveClipQueueId(clip);
    setReadyQueue((current) =>
      current.some((item) => item.clipId === clipId)
        ? removeReadyQueueItem(current, clipId)
        : upsertReadyQueueItem(current, createReadyQueueItem(clip, platform)),
    );
  }

  function handleMoveQueue(clipId: string, direction: -1 | 1) {
    setReadyQueue((current) => moveReadyQueueItem(current, clipId, direction));
  }

  function handleRemoveQueue(clipId: string) {
    setReadyQueue((current) => removeReadyQueueItem(current, clipId));
  }

  function handleClearQueue() {
    setReadyQueue(clearReadyQueue());
  }

  const homeGeneratorSection = (
    <section className="hero-card rounded-[34px] p-6 sm:p-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="section-kicker">Generate first</p>
          <h2 className="mt-3 text-2xl font-semibold text-ink sm:text-[2rem]">Paste once. Get the pack.</h2>
          <p className="mt-3 max-w-xl text-sm leading-7 text-subtext/90">Drop in a source. LWA handles the ranking.</p>
        </div>
        <StatPill tone="accent">{platform}</StatPill>
      </div>

      <form onSubmit={onSubmit} className="mt-7 space-y-5">
        <label className="block">
          <span className="mb-3 block text-sm font-medium text-ink/84">Source URL</span>
          <input
            type="url"
            value={videoUrl}
            onChange={(event) => setVideoUrl(event.target.value)}
            placeholder="Paste YouTube, TikTok, Instagram, or any public media URL"
            className="input-surface w-full rounded-[24px] px-5 py-4 text-sm"
          />
        </label>

        <div>
          <span className="mb-3 block text-sm font-medium text-ink/84">Platform target</span>
          <div className="grid gap-2 sm:grid-cols-3">
            {platforms.map((item) => {
              const active = item === platform;
              return (
                <button
                  key={item}
                  type="button"
                  onClick={() => setPlatform(item)}
                  className={[
                    "rounded-[20px] border px-4 py-3 text-sm font-medium transition",
                    active
                      ? "border-neonPurple/30 bg-[linear-gradient(135deg,rgba(124,58,237,0.24),rgba(37,99,255,0.18))] text-white shadow-neon"
                      : "border-white/10 bg-white/[0.04] text-ink/72 hover:border-white/20 hover:bg-white/[0.06] hover:text-ink",
                  ].join(" ")}
                >
                  {item}
                </button>
              );
            })}
          </div>
        </div>

        <div className="metric-tile rounded-[24px] p-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium text-ink">Improve my results</p>
              <p className="mt-1 text-sm text-ink/60">Bias future runs toward what you keep.</p>
            </div>
            <label className="secondary-button inline-flex items-center gap-3 rounded-full px-4 py-2.5 text-sm font-medium">
              <input
                type="checkbox"
                checked={improveResults}
                onChange={(event) => setImproveResults(event.target.checked)}
                className="h-4 w-4 accent-cyan-400"
              />
              Improve results
            </label>
          </div>
        </div>

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-ink/60">{loadingStages[loadingStageIndex]}. Short-form outputs are on the way.</p>
          <button
            type="submit"
            disabled={isLoading}
            className="primary-button inline-flex min-w-[220px] items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? "Compiling clip pack..." : "Generate clips"}
          </button>
        </div>

        {isLoading ? (
          <InlineState
            title="Compiling clip pack..."
            description={`${loadingStages[loadingStageIndex]}. ${loadingStageIndex >= 2 ? "Ranking hooks and angles." : "Shaping the pack."}${improveResults && preferenceProfile.topPackagingAngle ? ` Leaning ${preferenceProfile.topPackagingAngle}.` : ""}`}
          />
        ) : null}

        {error ? <InlineAlert tone="error">{error}</InlineAlert> : null}
        {paywallMessage ? (
          <InlineAlert tone="violet" title="Out of credits">
            <div className="space-y-3">
              <p>{paywallMessage}</p>
              <div className="flex flex-wrap gap-3">
                <Link href="/settings" className="primary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold">
                  Review plan
                </Link>
                <Link href="/wallet" className="secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium">
                  Open wallet
                </Link>
              </div>
            </div>
          </InlineAlert>
        ) : null}
      </form>
    </section>
  );

  const generatorSection = (
    <section className="space-y-6">
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr),320px]">
        <section className="hero-card rounded-[34px] p-6 sm:p-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-2xl">
              <p className="section-kicker">{initialSection === "upload" ? "Upload + Generate" : "Generate"}</p>
              <h2 className="page-title mt-3 text-3xl font-semibold text-ink sm:text-[2.4rem]">
                Turn one source into ranked clips
              </h2>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-subtext">Source in. Clips worth posting out.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <StatPill tone="accent">{planSurface.name}</StatPill>
              <StatPill tone="signal">{result?.processing_summary?.ai_provider || "Live output"}</StatPill>
            </div>
          </div>

          <form onSubmit={onSubmit} className="mt-8 space-y-6">
            <label className="block">
              <span className="mb-3 block text-sm font-medium text-ink/84">Source URL</span>
              <input
                type="url"
                value={videoUrl}
                onChange={(event) => setVideoUrl(event.target.value)}
                placeholder="Paste YouTube, TikTok, Instagram, or any public media URL"
                className="input-surface w-full rounded-[24px] px-5 py-4 text-sm"
              />
            </label>

            <div>
              <span className="mb-3 block text-sm font-medium text-ink/84">Platform target</span>
              <div className="grid gap-2 sm:grid-cols-3">
                {platforms.map((item) => {
                  const active = item === platform;
                  return (
                    <button
                      key={item}
                      type="button"
                      onClick={() => setPlatform(item)}
                      className={[
                        "rounded-[20px] border px-4 py-3 text-sm font-medium transition",
                        active
                          ? "border-neonPurple/30 bg-[linear-gradient(135deg,rgba(124,58,237,0.24),rgba(37,99,255,0.18))] text-white shadow-neon"
                          : "border-white/10 bg-white/[0.04] text-ink/72 hover:border-white/20 hover:bg-white/[0.06] hover:text-ink",
                      ].join(" ")}
                    >
                      {item}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="metric-tile rounded-[24px] p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-sm font-medium text-ink">Improve my results</p>
                    <p className="mt-1 text-sm text-ink/60">Bias future runs toward your taste.</p>
                    {preferenceProfile.topPackagingAngle || preferenceProfile.topHookStyle ? (
                      <p className="mt-3 text-sm text-accent">
                        Favoring {preferenceProfile.topPackagingAngle || "strong"} packaging
                        {preferenceProfile.topHookStyle ? ` and ${preferenceProfile.topHookStyle} hooks` : ""}.
                      </p>
                    ) : (
                      <p className="mt-3 text-sm text-ink/46">Mark what hits. The browser remembers.</p>
                    )}
                  </div>
                  <label className="secondary-button inline-flex items-center gap-3 rounded-full px-4 py-2.5 text-sm font-medium">
                    <input
                      type="checkbox"
                      checked={improveResults}
                      onChange={(event) => setImproveResults(event.target.checked)}
                      className="h-4 w-4 accent-cyan-400"
                    />
                    Improve results
                  </label>
                </div>
              </div>

              <div className="metric-tile rounded-[24px] p-4">
                <p className="text-sm font-medium text-ink">What comes back</p>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {[
                    "Ranked clips",
                    "Hook variants",
                    "Caption styles",
                    "Post order",
                  ].map((item) => (
                    <div key={item} className="rounded-[18px] border border-white/10 bg-white/[0.04] px-3 py-3 text-sm text-ink/76">
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <p className="text-sm text-ink/60">
                {result
                  ? "Clip pack is ready. Pick the winners and move."
                  : "Use a public link or upload a video, audio file, or image."}
              </p>
              <button
                type="submit"
                disabled={isLoading}
                className="primary-button inline-flex min-w-[240px] items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isLoading ? "Compiling clip pack..." : "Generate clips"}
              </button>
            </div>

            {isLoading ? (
              <InlineState
                title="Compiling clip pack..."
                description={`${loadingStages[loadingStageIndex]}. ${loadingStageIndex >= 2 ? "Ranking hooks and angles." : "Shaping the pack."}${improveResults && preferenceProfile.topPackagingAngle ? ` Leaning ${preferenceProfile.topPackagingAngle}.` : ""}`}
              />
            ) : null}

            {error ? <InlineAlert tone="error">{error}</InlineAlert> : null}

            {paywallMessage ? (
              <InlineAlert tone="violet" title="Out of credits">
                <div className="space-y-3">
                  <p>{paywallMessage}</p>
                  <div className="flex flex-wrap gap-3">
                    <Link href="/settings" className="primary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold">
                      Review plan
                    </Link>
                    <Link href="/wallet" className="secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium">
                      Open wallet
                    </Link>
                  </div>
                </div>
              </InlineAlert>
            ) : null}
          </form>
        </section>

        <aside className="space-y-4">
          <div className="glass-panel rounded-[28px] p-5">
            <p className="section-kicker">Plan + credits</p>
            <h3 className="mt-3 text-2xl font-semibold text-ink">{planSurface.name}</h3>
            <div className="mt-5 grid gap-3">
              <MetricTile
                label="Credits remaining"
                value={typeof creditsRemaining === "number" ? String(creditsRemaining) : String(planLimits.generationsPerDay)}
                detail={typeof creditsRemaining === "number" ? "Available today" : "Daily generation limit"}
              />
              <MetricTile label="Clip limit" value={String(planLimits.clipLimit)} detail="Ranked clips returned per run" />
              <MetricTile label="Uploads" value={String(planLimits.uploadsPerDay)} detail="Source uploads available per day" />
            </div>
            <p className="mt-4 text-sm leading-7 text-ink/60">{planSurface.watermark ? "Watermark stays on free exports." : "Clean exports are unlocked."}</p>
          </div>

          <div className="glass-panel rounded-[28px] p-5">
            <p className="section-kicker">Upload a source</p>
            <h3 className="mt-3 text-xl font-semibold text-ink">Run it from a local file</h3>
            <p className="mt-3 text-sm leading-7 text-ink/60">{token ? "Same ranking flow. More source control." : "Sign in to unlock uploads and saved source reuse."}</p>
            <p className="mt-4 text-sm text-accent">{uploadingFileName ? `Uploading ${uploadingFileName}...` : activeSourceLabel}</p>
            <label className="secondary-button mt-5 inline-flex w-full cursor-pointer items-center justify-center rounded-full px-5 py-3 text-sm font-medium">
              {token ? "Upload source file" : "Sign in to upload"}
              <input
                type="file"
                accept=".mp4,.mov,.m4v,.webm,.mp3,.wav,.m4a,.aac,.ogg,.oga,.flac,.jpg,.jpeg,.png,.webp,.heic,.heif,video/*,audio/*,image/*"
                className="hidden"
                onChange={onUploadSelected}
              />
            </label>
          </div>

          <div className="glass-panel rounded-[28px] p-5">
            <p className="section-kicker">Why this works</p>
            <div className="mt-4 space-y-3 text-sm leading-7 text-ink/68">
              <p>1. One source becomes multiple ranked outputs.</p>
              <p>2. Hooks, captions, and angles come back ready to test.</p>
              <p>3. Queue and campaign flow keep the best clips moving.</p>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );

  const resultsSection = result ? (
    <section className="space-y-6">
      <div className="hero-card rounded-[32px] p-6 sm:p-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="section-kicker">Clip pack ready</p>
            <h3 className="page-title mt-3 text-3xl font-semibold text-ink sm:text-[2.4rem]">Your best clips are ranked</h3>
            <p className="mt-4 text-sm leading-7 text-subtext">Pick the winners, queue them, or move them into campaign flow.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <StatPill tone="accent">{displayedClips.length} clips</StatPill>
            <StatPill tone="neutral">{result.source_platform || "Upload"}</StatPill>
            {result.source_type ? <StatPill tone="neutral">{result.source_type.replace("_", " ")}</StatPill> : null}
            {result.processing_summary?.recommended_next_step ? <StatPill tone="signal">{result.processing_summary.recommended_next_step}</StatPill> : null}
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr),340px]">
        <div className="space-y-6">
          <div className="glass-panel rounded-[28px] p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-3xl">
                <p className="section-kicker">Source truth</p>
                <h4 className="mt-3 text-2xl font-semibold text-ink">{result.source_title || "Processed source"}</h4>
                <p className="mt-3 text-sm leading-7 text-ink/70">{sourceTruthSummary}</p>
              </div>
              <div className="flex flex-wrap gap-3">
                {result.preview_asset_url ? (
                  <a
                    href={result.preview_asset_url}
                    target="_blank"
                    rel="noreferrer"
                    className="secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium"
                  >
                    Preview source
                  </a>
                ) : null}
                {result.download_asset_url ? (
                  <a
                    href={result.download_asset_url}
                    download
                    className="primary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold"
                  >
                    Download source
                  </a>
                ) : (
                  <span className="rounded-full border border-neonPurple/18 bg-neonPurple/10 px-4 py-2 text-sm text-white/78">
                    Pro unlocks download
                  </span>
                )}
              </div>
            </div>
          </div>

          {featuredClip ? (
            <div className="space-y-3">
              <p className="section-kicker">Top output</p>
              <ClipCard
                clip={featuredClip}
                featured
                feedbackVote={feedbackByClipId[featuredClip.record_id || featuredClip.clip_id || featuredClip.id] || null}
                onVote={handleFeedbackVote}
                queued={isQueued(featuredClip)}
                onToggleQueue={handleToggleQueue}
              />
            </div>
          ) : null}

          {remainingClips.length ? (
            <div className="space-y-4">
              <div className="flex items-end justify-between gap-4">
                <div>
                  <p className="section-kicker">Remaining ranked clips</p>
                  <h4 className="mt-2 text-2xl font-semibold text-ink">More clips worth testing</h4>
                </div>
              </div>
              <div className="grid gap-5 lg:grid-cols-2">
                {remainingClips.map((clip) => (
                  <ClipCard
                    key={clip.id}
                    clip={clip}
                    feedbackVote={feedbackByClipId[clip.record_id || clip.clip_id || clip.id] || null}
                    onVote={handleFeedbackVote}
                    queued={isQueued(clip)}
                    onToggleQueue={handleToggleQueue}
                  />
                ))}
              </div>
            </div>
          ) : null}
        </div>

        <div className="space-y-5">
          <ReadyQueuePanel items={readyQueue} onMove={handleMoveQueue} onRemove={handleRemoveQueue} onClear={handleClearQueue} />

          <div className="glass-panel rounded-[28px] p-5">
            <p className="section-kicker">Top performing angles</p>
            <h4 className="mt-3 text-xl font-semibold text-ink">What the workspace is learning</h4>
            <div className="mt-4 flex flex-wrap gap-2">
              {(topAngles.length ? topAngles : ["curiosity", "value", "story"]).slice(0, 4).map((angle) => (
                <span key={angle} className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-2 text-sm text-ink/82">
                  {angle}
                </span>
              ))}
            </div>
            <p className="mt-4 text-sm leading-7 text-ink/60">
              {preferenceProfile.preferredHookStyles.length
                ? `Preferred hook styles: ${preferenceProfile.preferredHookStyles.join(", ")}.`
                : "No strong hook signal yet. Mark what hits."}
            </p>
          </div>

          <div className="glass-panel rounded-[28px] p-5">
            <p className="section-kicker">Execution guide</p>
            <h4 className="mt-3 text-xl font-semibold text-ink">Move this pack fast</h4>
            <div className="mt-4 space-y-3 text-sm text-ink/72">
              <p>1. Post the top clip first.</p>
              <p>2. Test the variants before recutting the source.</p>
              <p>3. Mark what works so future runs tighten around your taste.</p>
            </div>
            <p className="mt-4 text-sm text-accent">
              {improveResults ? "Preference learning is on." : "Turn on Improve results to apply local learning."}
            </p>
          </div>
        </div>
      </div>
    </section>
  ) : null;

  const emptyGeneratorState = !result && !isLoading && showGenerator ? (
    <section className="glass-panel rounded-[28px] p-6 sm:p-8">
      <p className="section-kicker">Ready</p>
      <h3 className="mt-3 text-2xl font-semibold text-ink sm:text-3xl">Your next pack lands here</h3>
      <p className="mt-3 max-w-2xl text-sm leading-7 text-ink/60">Expect ranked clips, hooks, captions, angles, and post order.</p>
    </section>
  ) : null;

  return (
    <main className="app-shell-grid min-h-screen bg-hero-radial">
      <div className="hero-orb hero-orb-purple left-[-8rem] top-[-4rem] h-80 w-80" />
      <div className="hero-orb hero-orb-blue right-[-5rem] top-24 h-72 w-72" />
      <div className="hero-orb hero-orb-cyan bottom-20 right-[14%] h-60 w-60" />
      <AuthPanel
        isOpen={authOpen}
        mode={authMode}
        onClose={() => setAuthOpen(false)}
        onSwitchMode={setAuthMode}
        onAuthenticated={({ token: accessToken, user: profile }) => {
          storeToken(accessToken);
          setToken(accessToken);
          setUser(profile);
          setAuthOpen(false);
        }}
      />

      {isHome ? (
        <div className="mx-auto w-full max-w-7xl px-4 pb-20 pt-6 sm:px-6 lg:px-8">
          <Navbar
            items={marketingNavItems.map((item) => ({ href: item.href, label: item.label }))}
            showTagline
            rightSlot={
              <div className="flex items-center gap-2">
                {user ? (
                  <>
                    <Link href="/dashboard" className="secondary-button inline-flex rounded-full px-4 py-2.5 text-sm font-medium">
                      Open workspace
                    </Link>
                    <span className="hidden rounded-full border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm text-ink/72 sm:inline-flex">
                      {planSurface.name}
                    </span>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => {
                        setAuthMode("login");
                        setAuthOpen(true);
                      }}
                      className="secondary-button inline-flex rounded-full px-4 py-2.5 text-sm font-medium"
                    >
                      Sign in
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setAuthMode("signup");
                        setAuthOpen(true);
                      }}
                      className="primary-button inline-flex rounded-full px-4 py-2.5 text-sm font-semibold"
                    >
                      Start now
                    </button>
                  </>
                )}
              </div>
            }
          />

          <section className="grid gap-12 pb-10 pt-16 lg:grid-cols-[1.06fr,0.94fr] lg:items-start">
            <div className="space-y-7">
              <div className="space-y-5">
                <p className="section-kicker">AI content repurposer</p>
                <h1 className="page-title max-w-5xl text-5xl font-semibold leading-[0.98] text-ink sm:text-6xl lg:text-7xl">
                  Turn one source into <span className="text-gradient">ranked clips worth posting</span>
                </h1>
                <p className="max-w-3xl text-base leading-8 text-subtext sm:text-lg">Hooks, captions, timestamps, and ranked outputs in one premium workspace.</p>
              </div>

              <div className="flex flex-wrap gap-3">
                <Link href="/generate" className="primary-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold">
                  Generate clips
                </Link>
                <Link
                  href={user ? "/dashboard" : "/signup"}
                  className="secondary-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-medium"
                >
                  Open workspace
                </Link>
              </div>

              <p className="text-sm uppercase tracking-[0.24em] text-ink/56">Built for creators, clippers, and operators</p>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {[
                  { label: "Ranked outputs", detail: "See the winner fast." },
                  { label: "Caption-ready", detail: "Hooks and styles come packaged." },
                  { label: "Campaign flow", detail: "Move winners into ops." },
                  { label: "Ready queue", detail: "Stack the next posts in order." },
                ].map((item) => (
                  <div key={item.label} className="metric-tile rounded-[24px] p-4">
                    <p className="text-sm font-semibold text-ink">{item.label}</p>
                    <p className="mt-2 text-sm leading-6 text-ink/62">{item.detail}</p>
                  </div>
                ))}
              </div>

              <div className="flex flex-wrap gap-2">
                {featureProof.map((item, index) => (
                  <StatPill key={item} tone={index === 1 ? "signal" : "neutral"}>
                    {item}
                  </StatPill>
                ))}
              </div>
            </div>

            <div className="space-y-5">
              {homeGeneratorSection}
              {!result && !isLoading ? <MarketingPreview user={user} /> : null}
            </div>
          </section>

          {resultsSection ? <div className="space-y-6 pb-8">{resultsSection}</div> : null}
        </div>
      ) : (
        <div className="mx-auto w-full max-w-[1480px] px-4 py-6 sm:px-6 lg:px-8">
          <Navbar
            items={visibleAppNavItems.map((item) => ({ href: item.href, label: item.label }))}
            compactLogo
            rightSlot={
              user ? (
                <div className="flex items-center gap-2">
                  <span className="hidden rounded-full border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm text-ink/72 lg:inline-flex">
                    {planSurface.name}
                  </span>
                  <button
                    type="button"
                    onClick={onSignOut}
                    className="secondary-button inline-flex rounded-full px-4 py-2.5 text-sm font-medium"
                  >
                    Sign out
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("login");
                    setAuthOpen(true);
                  }}
                  className="primary-button inline-flex rounded-full px-4 py-2.5 text-sm font-semibold"
                >
                  Sign in
                </button>
              )
            }
          />

          <div className="mt-8 grid gap-6 xl:grid-cols-[280px,minmax(0,1fr)]">
            <aside className="hidden xl:block">
              <div className="sticky top-28 space-y-4">
                <WorkspaceRailCard
                  label="Studio pulse"
                  title={user ? "Generate first. Move fast after." : "Premium workspace"}
                  description={
                    user
                      ? "Move from generation to queue, assignments, and payout readiness without leaving the workspace."
                      : "Sign in to unlock saved runs, campaigns, wallet views, and queue state."
                  }
                >
                  <div className="mt-5 flex flex-wrap gap-2">
                    <StatPill tone="accent">{planSurface.name}</StatPill>
                    <StatPill tone="neutral">{readyQueue.length} in queue</StatPill>
                  </div>
                </WorkspaceRailCard>

                <WorkspaceRailCard label="Account" title={user ? user.email : "Guest mode"} description={user ? `Role ${user.role || "creator"}` : "Use account mode for uploads, history, campaigns, and wallet state."}>
                  <div className="mt-5 grid gap-3">
                    <MetricTile label="Clip packs" value={String(clipPacks.length)} detail="Saved history" />
                    <MetricTile label="Uploads" value={String(uploads.length)} detail="Reusable sources" />
                    <MetricTile label="Credits" value={typeof creditsRemaining === "number" ? String(creditsRemaining) : String(planLimits.generationsPerDay)} detail="Generation capacity" />
                  </div>
                </WorkspaceRailCard>

                <WorkspaceRailCard
                  label="Next move"
                  title="Use the system in order"
                  description="Generate first, queue the winners, then move them into campaign flow."
                />
              </div>
            </aside>

            <div className="space-y-6">

              {pageIntro ? (
                <section className="hero-card rounded-[34px] p-6 sm:p-8">
                  <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
                    <div className="max-w-3xl">
                      <p className="section-kicker">{pageIntro.label}</p>
                      <h1 className="page-title mt-3 text-4xl font-semibold text-ink sm:text-5xl">{pageIntro.title}</h1>
                      <p className="mt-4 max-w-3xl text-sm leading-7 text-subtext sm:text-base">{pageIntro.description}</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {user ? (
                        <>
                          <StatPill tone="accent">{planSurface.name}</StatPill>
                          <StatPill tone="neutral">{wallet ? `$${((wallet.available_cents || 0) / 100).toFixed(2)}` : "Wallet"}</StatPill>
                          <StatPill tone="neutral">{readyQueue.length} queued</StatPill>
                        </>
                      ) : (
                        <StatPill tone="neutral">Guest mode</StatPill>
                      )}
                    </div>
                  </div>
                </section>
              ) : null}

              {accountError ? (
                <section className="rounded-[24px] border border-amber-400/20 bg-amber-400/10 px-5 py-4 text-sm text-amber-100">
                  {accountError}
                </section>
              ) : null}

              {requiresAccount && !user ? (
                <section className="hero-card rounded-[34px] p-6 sm:p-8">
                  <p className="section-kicker">Authentication required</p>
                  <h2 className="mt-3 text-3xl font-semibold text-ink">Sign in to open the workspace</h2>
                  <p className="mt-4 max-w-3xl text-sm leading-7 text-ink/60">History, campaigns, wallet state, uploads, and queue all live in your account.</p>
                  <div className="mt-6 flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() => {
                        setAuthMode("signup");
                        setAuthOpen(true);
                      }}
                      className="primary-button rounded-full px-5 py-3 text-sm font-semibold"
                    >
                      Create account
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setAuthMode("login");
                        setAuthOpen(true);
                      }}
                      className="secondary-button rounded-full px-5 py-3 text-sm font-medium"
                    >
                      Sign in
                    </button>
                  </div>
                </section>
              ) : (
                <>
                  {showGenerator ? generatorSection : null}
                  {showGenerator ? emptyGeneratorState : null}
                  {resultsSection ? resultsSection : null}

                  {showDashboard && user ? (
                    <>
                      <ReadyQueuePanel items={readyQueue} onMove={handleMoveQueue} onRemove={handleRemoveQueue} onClear={handleClearQueue} />
                      <AccountWorkspace
                        user={user}
                        wallet={wallet}
                        clipPacks={clipPacks}
                        uploads={uploads}
                        batches={batches}
                        campaigns={campaigns}
                        readyQueueCount={readyQueue.length}
                        planLabel={planSurface.name}
                        onSignOut={onSignOut}
                        onOpenClipPack={openClipPack}
                        selectedClipPackId={selectedClipPackId}
                      />
                      {showPostingOnDashboard && postingQueueUnlocked ? (
                        <PostingPanel
                          connections={postingConnections}
                          scheduledPosts={scheduledPosts}
                          selectedClipPack={selectedClipPack}
                          onCreateConnection={handleCreatePostingConnection}
                          onCreateScheduledPost={handleCreateScheduledPost}
                          onUpdateScheduledPost={handleUpdateScheduledPost}
                        />
                      ) : showPostingOnDashboard ? (
                        <FeatureGatePanel
                          label="Posting queue"
                          title="Scale unlocks direct queue controls"
                          description="Keep using the ready queue locally, then upgrade when you want provider connections and scheduled posting inside the app."
                          requiredPlan="Scale"
                          bullets={[
                            "Provider connection records",
                            "Scheduled post state changes",
                            "Queue management inside the workspace",
                          ]}
                        />
                      ) : null}
                    </>
                  ) : null}

                  {showHistory && user ? (
                    <HistoryPanel
                      clipPacks={clipPacks}
                      selectedClipPackId={selectedClipPackId}
                      isLoading={isClipPackLoading}
                      onOpenClipPack={openClipPack}
                    />
                  ) : null}

                  {showBatches && user ? (
                    <BatchPanel
                      batches={batches}
                      uploads={uploads}
                      currentVideoUrl={videoUrl}
                      selectedUpload={selectedUpload}
                      platform={platform}
                      onCreate={handleBatchCreate}
                    />
                  ) : null}

                  {showCampaigns && user && campaignsUnlocked ? (
                    <CampaignPanel
                      userRole={(user.role as WorkspaceRole) || "creator"}
                      campaigns={campaigns}
                      clipPacks={clipPacks}
                      selectedClipPack={selectedClipPack}
                      selectedCampaign={selectedCampaign}
                      selectedCampaignId={selectedCampaignId}
                      isLoading={isCampaignLoading}
                      onCreate={handleCampaignCreate}
                      onOpenCampaign={openCampaign}
                      onUpdateStatus={handleCampaignStatusUpdate}
                      onAssign={handleCampaignAssignmentCreate}
                      onUpdateAssignment={handleCampaignAssignmentUpdate}
                    />
                  ) : showCampaigns && user ? (
                    <FeatureGatePanel
                      label="Campaigns"
                      title="Campaign workflows are locked on the current plan"
                      description="Upgrade when you need briefs, platform targets, requirements, and campaign-level coordination built into the workspace."
                      requiredPlan="Scale"
                      bullets={[
                        "Campaign briefs and angle targeting",
                        "Posting requirements for clippers and creators",
                        "Campaign-level payout scaffolding",
                      ]}
                    />
                  ) : null}

                  {showWallet && user && walletUnlocked ? (
                    <WalletPanel wallet={wallet} ledgerEntries={walletLedger} onRequestPayout={handlePayoutRequest} />
                  ) : showWallet && user ? (
                    <FeatureGatePanel
                      label="Wallet"
                      title="Wallet views unlock on paid plans"
                      description="Upgrade to track earnings, payout requests, and ledger movement from the same workspace."
                      requiredPlan="Pro"
                      bullets={[
                        "Ledger balance tracking",
                        "Payout request history",
                        "Future earnings and payout surfaces",
                      ]}
                    />
                  ) : null}

                  {showSettings && user ? (
                    <div className="space-y-10">
                      <SettingsPanel
                        user={user}
                        wallet={wallet}
                        featureFlags={activeFeatureFlags}
                        creditsRemaining={creditsRemaining}
                        planLabel={planSurface.name}
                        onSignOut={onSignOut}
                      />
                      <ReadyQueuePanel items={readyQueue} onMove={handleMoveQueue} onRemove={handleRemoveQueue} onClear={handleClearQueue} />
                      {postingQueueUnlocked ? (
                        <PostingPanel
                          connections={postingConnections}
                          scheduledPosts={scheduledPosts}
                          selectedClipPack={selectedClipPack}
                          onCreateConnection={handleCreatePostingConnection}
                          onCreateScheduledPost={handleCreateScheduledPost}
                          onUpdateScheduledPost={handleUpdateScheduledPost}
                        />
                      ) : (
                        <FeatureGatePanel
                          label="Posting queue"
                          title="Scheduled posting is not unlocked yet"
                          description="Use the ready queue today, then move to Scale when you want connection records and scheduled publishing inside the product."
                          requiredPlan="Scale"
                        />
                      )}
                    </div>
                  ) : null}
                </>
              )}

              {selectedClipPack && user ? (
                <ClipPackEditor
                  clipPack={selectedClipPack}
                  onSave={saveClipMetadata}
                  onClose={() => setSelectedClipPack(null)}
                  readOnly={!editorUnlocked}
                  lockedMessage="Upgrade to Pro to edit hooks, captions, packaging, and trims directly from saved history."
                />
              ) : null}

              {isAccountLoading && user ? (
                <section className="rounded-[24px] border border-white/10 bg-white/[0.03] px-5 py-4 text-sm text-ink/70">
                  Refreshing account data...
                </section>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

function StatPill({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "accent" | "signal" }) {
  return (
    <span
      className={[
        "rounded-full border px-3 py-1.5 text-xs font-semibold",
        tone === "accent"
          ? "border-neonPurple/25 bg-[linear-gradient(135deg,rgba(124,58,237,0.18),rgba(37,99,255,0.14))] text-white"
          : tone === "signal"
            ? "border-accentCrimson/28 bg-[linear-gradient(135deg,rgba(92,19,37,0.42),rgba(143,29,54,0.12))] text-white shadow-crimson"
            : "border-white/10 bg-white/[0.05] text-ink/72",
      ].join(" ")}
    >
      {children}
    </span>
  );
}

function MetricTile({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="metric-tile rounded-[24px] p-4">
      <p className="text-xs uppercase tracking-[0.24em] text-muted">{label}</p>
      <p className="mt-3 text-2xl font-semibold text-ink">{value}</p>
      <p className="mt-2 text-sm leading-6 text-ink/60">{detail}</p>
    </div>
  );
}

function MarketingPreview({ user }: { user: UserProfile | null }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[
        {
          title: "Ranked clip outputs",
          detail: "Score, fit, and post order come back structured.",
        },
        {
          title: "Caption-ready packaging",
          detail: "Hooks, caption styles, CTA, and thumbnail text come built in.",
        },
        {
          title: "Campaign workflow",
          detail: "Move strong assets into assignment and payout-ready flow.",
        },
        {
          title: "Ready queue",
          detail: "Build the next posting stack without leaving the workspace.",
        },
      ].map((item, index) => (
        <div key={item.title} className={index === 0 ? "hero-card rounded-[26px] p-5" : index === 2 ? "signal-card rounded-[26px] p-5" : "glass-panel rounded-[26px] p-5"}>
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              {index === 0 ? <img src="/brand/lwa-mark.svg" alt="LWA" className="h-7 w-7 opacity-90" /> : null}
              <p className="text-sm font-semibold text-ink">{item.title}</p>
            </div>
            {index === 0 ? <StatPill tone="accent">{user ? user.plan_code || "free" : "guest"}</StatPill> : null}
          </div>
          <p className="mt-3 text-sm leading-7 text-ink/62">{item.detail}</p>
        </div>
      ))}
    </div>
  );
}

function WorkspaceRailCard({
  label,
  title,
  description,
  children,
}: {
  label: string;
  title: string;
  description: string;
  children?: ReactNode;
}) {
  return (
    <div className="glass-panel rounded-[28px] p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="section-kicker">{label}</p>
          <h3 className="mt-3 text-xl font-semibold text-ink">{title}</h3>
        </div>
      </div>
      <p className="mt-3 text-sm leading-7 text-ink/60">{description}</p>
      {children}
    </div>
  );
}

function InlineState({ title, description }: { title: string; description: string }) {
  return (
    <div className="panel-subtle rounded-[24px] px-5 py-8 text-center">
      <div className="relative mx-auto mb-4 flex h-12 w-12 items-center justify-center">
        <div className="absolute inset-0 animate-spin rounded-full border-2 border-white/10 border-t-accent" />
        <img src="/brand/lwa-mark.svg" alt="LWA" className="relative h-7 w-7 opacity-90" />
      </div>
      <p className="text-lg font-medium text-ink">{title}</p>
      <p className="mt-2 text-sm text-ink/60">{description}</p>
    </div>
  );
}

function InlineAlert({
  children,
  tone,
  title,
}: {
  children: ReactNode;
  tone: "error" | "violet";
  title?: string;
}) {
  const toneClass =
    tone === "error"
      ? "border-red-400/20 bg-red-400/8 text-red-100"
      : "border-neonPurple/20 bg-neonPurple/10 text-ink";

  return (
    <div className={["rounded-[24px] border px-5 py-4 text-sm", toneClass].join(" ")}>
      {title ? <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">{title}</p> : null}
      {children}
    </div>
  );
}
