"use client";

import Link from "next/link";
import { ChangeEvent, FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { AccountWorkspace } from "./account-workspace";
import { AuthPanel } from "./auth-panel";
import { BatchPanel } from "./batch-panel";
import { AIBackground } from "./AIBackground";
import { CampaignPanel } from "./campaign-panel";
import CharacterLayer from "./characters/CharacterLayer";
import { ClipCard } from "./clip-card";
import { ClipPackEditor, ClipPatchPayload } from "./clip-pack-editor";
import { FeatureGatePanel } from "./feature-gate-panel";
import HeroClip from "./HeroClip";
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
  ClipRecoveryStatus,
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
  exportClipBundle,
  generateClips,
  loadClipRecoveryJob,
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
  recoverClip,
  updateCampaign,
  updateCampaignAssignment,
  updateScheduledPost,
  uploadSource,
} from "../lib/api";
import { clearStoredToken, readStoredToken, storeToken } from "../lib/auth";
import { fireGodTrigger } from "../lib/character-ai";
import { emitLWACharacterEvent } from "../lib/character-controller";
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
import { GENERATOR_COPY, HERO_COPY, RESULTS_COPY, rewriteSurfaceLabel } from "../lib/brand-voice";
import { hasPreviewAsset } from "../lib/clip-utils";
import type { CharacterActionId } from "../lib/character-intelligence";
import { getPlanSurface } from "../lib/plans";
import { RESULT_COPY } from "../lib/result-copy";
import { resolveWorldPhase, resolveWorldState, type WorldSignal } from "../lib/world-state";
import { useStableResults } from "../hooks/useStableResults";

const platforms: PlatformOption[] = ["TikTok", "Instagram Reels", "YouTube Shorts"];
type SourceMode = "video" | "image" | "idea";

const sourceModeOptions: Array<{ value: SourceMode; label: string; detail: string }> = [
  { value: "video", label: "Video", detail: "Clip a source" },
  { value: "image", label: "Image", detail: "Generate motion" },
  { value: "idea", label: "Idea", detail: "Create from prompt" },
];

function clipHasRenderedMedia(clip: ClipResult) {
  return hasPreviewAsset(clip);
}

type ClipRecoveryState = {
  jobId?: string;
  status: "queued" | "processing" | "recovered" | "failed";
  message: string;
  error?: string | null;
};

const appNavItems = [
  { href: "/dashboard", label: rewriteSurfaceLabel("Dashboard"), section: "dashboard" },
  { href: "/generate", label: rewriteSurfaceLabel("Generate"), section: "generate" },
  { href: "/upload", label: rewriteSurfaceLabel("Upload"), section: "upload" },
  { href: "/history", label: rewriteSurfaceLabel("History"), section: "history" },
  { href: "/batches", label: rewriteSurfaceLabel("Batches"), section: "batches" },
  { href: "/campaigns", label: rewriteSurfaceLabel("Campaigns"), section: "campaigns" },
  { href: "/wallet", label: rewriteSurfaceLabel("Wallet"), section: "wallet" },
  { href: "/settings", label: rewriteSurfaceLabel("Settings"), section: "settings" },
] as const;

const marketingNavItems = [
  { href: "/generate", label: rewriteSurfaceLabel("Generate") },
  { href: "/history", label: rewriteSurfaceLabel("History") },
  { href: "/campaigns", label: rewriteSurfaceLabel("Campaigns") },
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
  const [sourceMode, setSourceMode] = useState<SourceMode>("video");
  const [ideaPrompt, setIdeaPrompt] = useState("");
  const [platform, setPlatform] = useState<PlatformOption>("TikTok");
  const [useManualPlatform, setUseManualPlatform] = useState(false);
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
  const [clipRecoveryStates, setClipRecoveryStates] = useState<Record<string, ClipRecoveryState>>({});
  const [generationMode, setGenerationMode] = useState<"quick" | "pro">("quick");
  const [readyQueue, setReadyQueue] = useState<ReadyQueueItem[]>([]);
  const [paywallMessage, setPaywallMessage] = useState<string | null>(null);
  const [loadingStageIndex, setLoadingStageIndex] = useState(0);
  const [motionLocked, setMotionLocked] = useState(false);
  const [bundleExportState, setBundleExportState] = useState<"idle" | "exporting" | "ready" | "failed">("idle");
  const [bundleExportMessage, setBundleExportMessage] = useState<string | null>(null);
  const [inputFocused, setInputFocused] = useState(false);
  const [generatorHovered, setGeneratorHovered] = useState(false);
  const stableResult = useStableResults(result);
  const activeResult = stableResult ?? result;
  const selectedUploadId = selectedUpload?.file_id || selectedUpload?.source_ref?.upload_id || selectedUpload?.id || "";
  const selectedUploadName = selectedUpload?.file_name || selectedUpload?.filename || "";
  const selectedUploadType = (selectedUpload?.content_type || "").toLowerCase();
  const selectedUploadIsImage =
    selectedUploadType.startsWith("image/") || /\.(jpg|jpeg|png|webp|heic|heif)$/i.test(selectedUploadName);
  const isGuest = !user;

  const activeSourceLabel = useMemo(() => {
    if (sourceMode === "idea") {
      return ideaPrompt.trim() ? "Using idea prompt" : "No idea entered";
    }
    if (selectedUploadName) {
      return `Using upload: ${selectedUploadName}`;
    }
    if (videoUrl.trim()) {
      return "Using pasted URL";
    }
    return "No source selected";
  }, [ideaPrompt, selectedUploadName, sourceMode, videoUrl]);

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
          description: "Runs, queue, campaigns, and account state.",
        };
      case "generate":
        return {
          label: "Generate",
          title: "Build your clip stack",
          description: "Paste a source. Get clips worth posting.",
        };
      case "upload":
        return {
          label: "Upload",
          title: "Bring your own file",
          description: "Run the same flow with local files.",
        };
      case "history":
        return {
          label: "History",
          title: "Reopen saved work",
          description: "Reopen past packs.",
        };
      case "batches":
        return {
          label: "Batches",
          title: "Queue multiple sources",
          description: "Group sources into repeatable runs.",
        };
      case "campaigns":
        return {
          label: "Campaigns",
          title: "Run content pushes",
          description: "Assign clips and track status.",
        };
      case "wallet":
        return {
          label: "Wallet",
          title: "Track value and payout state",
          description: "See balance and payout state.",
        };
      case "settings":
        return {
          label: "Settings",
          title: "Manage account and workflow",
          description: "Plan, credits, and account controls.",
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
      setLoadingStageIndex((current) => (current + 1) % 3);
    }, 1400);

    return () => window.clearInterval(interval);
  }, [isLoading]);

  useEffect(() => {
    if (!activeResult) {
      setMotionLocked(false);
      return;
    }

    setMotionLocked(false);
    const timer = window.setTimeout(() => setMotionLocked(true), 900);
    return () => window.clearTimeout(timer);
  }, [activeResult?.request_id]);

  useEffect(() => {
    if (!result || !isGuest) {
      return undefined;
    }

    const timer = window.setTimeout(() => {
      document.getElementById("lwa-results-section")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 400);
    return () => window.clearTimeout(timer);
  }, [result, isGuest]);

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
    if (isLiveStreamUrl) {
      setError("Live streams can't be clipped. Paste a regular YouTube video URL instead.");
      return;
    }
    if (sourceMode === "video" && !videoUrl.trim() && !selectedUploadId) {
      setError("Paste a public source URL or upload a file to generate your clip pack.");
      return;
    }
    if (sourceMode === "image" && !selectedUploadId) {
      setError("Upload an image before running Image mode.");
      return;
    }
    if (sourceMode === "image" && !selectedUploadIsImage) {
      setError("Image mode needs a JPG, PNG, WebP, HEIC, or HEIF upload.");
      return;
    }
    if (sourceMode === "idea" && ideaPrompt.trim().length < 10) {
      setError("Give LWA a clearer idea prompt before generating.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setPaywallMessage(null);
    emitLWACharacterEvent({ state: "react", trigger: "generation_start" });
    void fireGodTrigger("generation_start", {
      route: window.location.pathname,
      platform: useManualPlatform ? platform : "Auto",
      creditsRemaining,
    });

    try {
      const data = await generateClips(
        {
          mode: sourceMode,
          url: sourceMode === "video" ? videoUrl.trim() || undefined : undefined,
          platform: useManualPlatform ? platform : undefined,
          uploadFileId: sourceMode === "idea" ? undefined : selectedUploadId || undefined,
          contentAngle: improveResults ? preferenceProfile.topPackagingAngle : undefined,
          ideaPrompt: sourceMode === "idea" || sourceMode === "image" ? ideaPrompt.trim() || undefined : undefined,
        },
        token,
      );
      setResult(data);
      setClipRecoveryStates({});
      setPaywallMessage(null);
      const leadClip = data.clips?.[0];
      void fireGodTrigger("generation_complete", {
        route: window.location.pathname,
        lastClipScore: leadClip?.score,
        lastClipHook: leadClip?.hook,
        creditsRemaining: data.processing_summary?.credits_remaining,
        platform: data.processing_summary?.target_platform || platform,
      });
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
    setUploadingFileName(file.name);
    setError(null);
    try {
      const upload = await uploadSource(file, token);
      setSelectedUpload(upload);
      if (file.type.startsWith("image/")) {
        setSourceMode("image");
      } else {
        setSourceMode("video");
      }
      if (token) {
        await refreshAccount(token);
      }
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
    () => applyPreferenceBoost(activeResult?.clips || [], preferenceProfile, improveResults),
    [activeResult?.clips, improveResults, preferenceProfile],
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
    () => getPlanSurface(user?.plan_code, activeResult?.processing_summary?.feature_flags as FeatureFlags | undefined),
    [activeResult?.processing_summary?.feature_flags, user?.plan_code],
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
  const creditsRemaining = activeResult?.processing_summary?.credits_remaining;
  const editorUnlocked = Boolean(activeFeatureFlags.caption_editor || activeFeatureFlags.timeline_editor);
  const campaignsUnlocked = Boolean(activeFeatureFlags.campaign_mode);
  const walletUnlocked = Boolean(activeFeatureFlags.wallet_view);
  const postingQueueUnlocked = Boolean(activeFeatureFlags.posting_queue);
  const activeFeedbackPlatform = useMemo<PlatformOption>(() => {
    const candidate = activeResult?.processing_summary?.target_platform || platform;
    return platforms.includes(candidate as PlatformOption) ? (candidate as PlatformOption) : "TikTok";
  }, [activeResult?.processing_summary?.target_platform, platform]);
  const orderedClips = useMemo(() => {
    return [...displayedClips].sort((left, right) => {
      const leftOrder = left.post_rank || left.best_post_order || left.rank || Number.MAX_SAFE_INTEGER;
      const rightOrder = right.post_rank || right.best_post_order || right.rank || Number.MAX_SAFE_INTEGER;

      if (leftOrder !== rightOrder) {
        return leftOrder - rightOrder;
      }

      return (right.virality_score ?? right.score ?? 0) - (left.virality_score ?? left.score ?? 0);
    });
  }, [displayedClips]);

  const isHome = initialSection === "home";
  const hasSourceSelected =
    sourceMode === "idea"
      ? Boolean(ideaPrompt.trim())
      : sourceMode === "image"
        ? Boolean(selectedUploadId)
        : Boolean(videoUrl.trim() || selectedUploadId);
  const isLiveStreamUrl = Boolean(videoUrl) && (
    /youtube\.com\/live\//i.test(videoUrl) ||
    /youtu\.be\/.*live/i.test(videoUrl)
  );
  useEffect(() => {
    if (isGuest && generationMode !== "quick") {
      setGenerationMode("quick");
    }
  }, [generationMode, isGuest]);

  useEffect(() => {
    if (!hasSourceSelected) {
      return;
    }

    emitLWACharacterEvent({ state: "alert", trigger: "user_action" });
    void fireGodTrigger("url_pasted", {
      route: window.location.pathname,
      platform: useManualPlatform ? platform : "Auto",
    });
  }, [hasSourceSelected, platform, useManualPlatform]);

  useEffect(() => {
    if (typeof creditsRemaining === "number" && creditsRemaining <= 1) {
      void fireGodTrigger("low_credits", {
        route: window.location.pathname,
        creditsRemaining,
        platform: activeResult?.processing_summary?.target_platform || platform,
      });
    }
  }, [activeResult?.processing_summary?.target_platform, creditsRemaining, platform]);
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
    : orderedClips.map((clip) => clip.packaging_angle).filter(Boolean)) as string[];
  const featureProof = ["Best clip first", "Hooks that hit", "Export-ready"];
  const loadingStages =
    sourceMode === "idea"
      ? ["Reading idea", "Generating motion", "Preparing output"]
      : sourceMode === "image"
        ? ["Reading image", "Generating motion", "Preparing output"]
        : ["Reading source", "Finding clips", "Preparing outputs"];
  const deliveryMoments = [
      {
        label: "Source in",
        detail: "Paste or upload once.",
    },
    {
      label: "Best first",
      detail: "LWA puts the lead cut on top.",
    },
    {
      label: "Post faster",
      detail: "Queue or export ready clips.",
    },
  ] as const;
  const idleRunSummary =
    sourceMode === "idea"
      ? "Describe the asset. LWA generates a short-form starting point."
      : sourceMode === "image"
        ? "Upload an image. LWA turns it into a motion-ready asset."
        : generationMode === "quick"
      ? "Paste one source. LWA picks the first move."
      : "Keep auto on. Use learning for tighter future packs.";
  const homeDiscoverySections = [
    {
      id: "why-lwa",
      kicker: "Why LWA",
      title: "Built for source-to-post speed.",
      body: "LWA picks the next clip, packages it, and keeps the workflow moving.",
      bullets: [
        "Lead clip authority",
        "Hooks, captions, previews",
        "Queue, archive, campaigns, wallet",
      ],
      links: [
        { href: "/generate", label: "Generate clips" },
        { href: "/dashboard", label: "Open workspace" },
      ],
    },
    {
      id: "how-it-works",
      kicker: "How it works",
      title: "One source in. Post order out.",
      body: "Drop a link or file. LWA chooses what to post first.",
      bullets: [
        "Read source media",
        "Choose the posting stack",
        "Review, queue, export",
      ],
    },
    {
      id: "who-its-for",
      kicker: "Who it’s for",
      title: "For creators, clippers, and teams.",
      body: "Turn long-form into more clips without adding editing overhead.",
      bullets: [
        "Podcasts, streams, interviews",
        "Clippers and agencies",
        "Teams that need output trust",
      ],
    },
    {
      id: "compare",
      kicker: "Compare",
      title: "Use LWA when the decision matters.",
      body: "The value is knowing what to post first and moving it fast.",
      bullets: [
        "Clear review hierarchy",
        "Operator-ready workspace",
        "Built between ingest and posting",
      ],
      links: [
        { href: "/compare/opus-clip-alternative", label: "Opus Clip alternative" },
        { href: "/compare/capcut-alternative", label: "CapCut alternative" },
      ],
    },
    {
      id: "faq",
      kicker: "FAQ",
      title: "Built for real output.",
      body: "Use LWA for faster clips, better packaging, and clearer post order.",
      bullets: [
        "Free proves value",
        "Premium unlocks leverage",
        "Everything stays in one workspace",
      ],
      links: [
        { href: "/use-cases/podcast-clipping", label: "Podcast clipping" },
        { href: "/use-cases/whop-clipping", label: "Clipping workflows" },
        { href: "/settings", label: "Review plans" },
      ],
    },
  ] as const;
  const previewReadyCount = useMemo(
    () =>
      orderedClips.filter((clip) => clip.preview_url || clip.edited_clip_url || clip.clip_url || clip.raw_clip_url).length,
    [orderedClips],
  );
  const renderedClips = useMemo(() => orderedClips.filter((clip) => clipHasRenderedMedia(clip)), [orderedClips]);
  const strategyOnlyClips = useMemo(() => orderedClips.filter((clip) => !clipHasRenderedMedia(clip)), [orderedClips]);
  const renderedHeroClip = renderedClips[0] ?? null;
  const renderedGridClips = renderedHeroClip ? renderedClips.slice(1) : renderedClips;
  const strategyHeroClip = !renderedHeroClip ? strategyOnlyClips[0] ?? null : null;
  const strategyGridClips = strategyHeroClip ? strategyOnlyClips.slice(1) : strategyOnlyClips;
  const effectiveTargetPlatform = activeResult?.processing_summary?.target_platform || (useManualPlatform ? platform : "Auto");
  const recommendedPlatform = activeResult?.processing_summary?.recommended_platform || activeResult?.processing_summary?.target_platform || null;
  const recommendedContentType = activeResult?.processing_summary?.recommended_content_type || null;
  const recommendedOutputStyle = activeResult?.processing_summary?.recommended_output_style || null;
  const platformDecision = activeResult?.processing_summary?.platform_decision || (useManualPlatform ? "manual" : "auto");
  const platformRecommendationReason = activeResult?.processing_summary?.platform_recommendation_reason || null;
  const renderedClipCount = renderedClips.length;
  const strategyOnlyClipCount = strategyOnlyClips.length;
  const hasStrategyOnlyWithoutPreview = strategyOnlyClips.some(
    (clip) => Boolean(clip.is_strategy_only) && !clip.preview_url && !clipHasRenderedMedia(clip),
  );
  const recoveryActive = useMemo(
    () => Object.values(clipRecoveryStates).some((recovery) => recovery.status === "queued" || recovery.status === "processing"),
    [clipRecoveryStates],
  );
  const exportReadyCount = useMemo(() => orderedClips.filter((clip) => clip.download_url).length, [orderedClips]);
  const leadPreviewUrl =
    activeResult?.preview_asset_url ||
      renderedHeroClip?.preview_url ||
      renderedHeroClip?.edited_clip_url ||
      renderedHeroClip?.clip_url ||
      renderedHeroClip?.raw_clip_url ||
      null;
  const leadExportUrl = activeResult?.download_asset_url || renderedHeroClip?.download_url || null;
  const leadPreviewReady = Boolean(leadPreviewUrl);
  const leadExportReady = Boolean(leadExportUrl);
  const worldPhase = resolveWorldPhase({
    isLoading,
    loadingStageIndex,
    hasResult: Boolean(activeResult),
    hasSource: hasSourceSelected,
  });
  const worldState = resolveWorldState({
    variant: isHome ? "home" : "workspace",
    generationMode,
    inputFocused,
    generatorHovered,
    isLoading,
    loadingStageIndex,
    hasResult: Boolean(activeResult),
    hasSource: hasSourceSelected,
  });
  const worldSignal: WorldSignal = isLoading
    ? "generating"
    : activeResult
      ? "complete"
      : inputFocused
        ? "focus"
        : generatorHovered
          ? "hover"
          : "idle";
  function handleFeedbackVote(clip: GenerateResponse["clips"][number], vote: "good" | "bad") {
    setFeedbackRecords((current) => upsertFeedbackRecord(current, createFeedbackRecord(clip, vote, activeFeedbackPlatform)));
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
        : upsertReadyQueueItem(current, createReadyQueueItem(clip, activeResult?.processing_summary?.target_platform || platform)),
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

  // Active first-use export contract:
  // ClipStudio generate results currently export through /api/export-bundle
  // because the live generate flow returns req_* packs from /api/generate.
  // Do not swap this directly to /api/video-export/[videoId] unless the export
  // identifier mapping is updated and verified end-to-end.
  async function handleExportBundle() {
    if (!activeResult?.clips?.length) {
      return;
    }

    setBundleExportState("exporting");
    setBundleExportMessage(null);

    try {
      const bundle = await exportClipBundle(
        {
          source_url: activeResult.video_url,
          clips: activeResult.clips,
        },
        token,
      );
      const link = document.createElement("a");
      link.href = bundle.download_url;
      link.download = bundle.file_name || "lwa-bundle.json";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setBundleExportState("ready");
      setBundleExportMessage("Bundle downloaded.");
      void fireGodTrigger("first_download", {
        route: window.location.pathname,
        lastClipScore: orderedClips[0]?.score,
        lastClipHook: orderedClips[0]?.hook,
        creditsRemaining,
        platform: activeResult.processing_summary?.target_platform || platform,
      });
    } catch (bundleError) {
      setBundleExportState("failed");
      setBundleExportMessage(bundleError instanceof Error ? bundleError.message : "Export failed. Try again.");
    }
  }

  function replaceClipInResult(updatedClip: ClipResult) {
    setResult((current) => {
      if (!current) {
        return current;
      }
      const nextClips = current.clips.map((clip) => {
        const currentId = clip.record_id || clip.clip_id || clip.id;
        const updatedId = updatedClip.record_id || updatedClip.clip_id || updatedClip.id;
        return currentId === updatedId ? { ...clip, ...updatedClip } : clip;
      });
      const nextRenderedClipCount = nextClips.filter((clip) => clipHasRenderedMedia(clip)).length;
      const nextStrategyOnlyClipCount = Math.max(nextClips.length - nextRenderedClipCount, 0);
      return {
        ...current,
        clips: nextClips,
        preview_asset_url:
          current.preview_asset_url ||
          updatedClip.preview_url ||
          updatedClip.edited_clip_url ||
          updatedClip.clip_url ||
          updatedClip.raw_clip_url ||
          null,
        download_asset_url: current.download_asset_url || updatedClip.download_url || null,
        thumbnail_url: current.thumbnail_url || updatedClip.preview_image_url || updatedClip.thumbnail_url || null,
        processing_summary: current.processing_summary
          ? {
              ...current.processing_summary,
              rendered_clip_count: nextRenderedClipCount,
              strategy_only_clip_count: nextStrategyOnlyClipCount,
            }
          : current.processing_summary,
      };
    });
  }

  function applyRecoveryStatus(clipId: string, status: ClipRecoveryStatus) {
    setClipRecoveryStates((current) => ({
      ...current,
      [clipId]: {
        jobId: status.job_id,
        status:
          status.status === "recovered" || status.status === "failed"
            ? status.status
            : status.status === "processing"
              ? "processing"
              : "queued",
        message: status.message,
        error: status.error || null,
      },
    }));

    if (status.status === "recovered" && status.recovered_clip) {
      replaceClipInResult(status.recovered_clip);
      setClipRecoveryStates((current) => ({
        ...current,
        [clipId]: {
          jobId: status.job_id,
          status: "recovered",
          message: status.message,
          error: null,
        },
      }));
    }
  }

  async function pollRecoveryJob(clipId: string, jobId: string) {
    if (!token) {
      return;
    }
    try {
      const status = await loadClipRecoveryJob(token, jobId);
      applyRecoveryStatus(clipId, status);
      if (status.status === "queued" || status.status === "processing") {
        window.setTimeout(() => {
          void pollRecoveryJob(clipId, jobId);
        }, 1600);
      }
    } catch (recoveryError) {
      setClipRecoveryStates((current) => ({
        ...current,
        [clipId]: {
          jobId,
          status: "failed",
          message: recoveryError instanceof Error ? recoveryError.message : "Unable to poll recovery status.",
          error: recoveryError instanceof Error ? recoveryError.message : "Unable to poll recovery status.",
        },
      }));
    }
  }

  async function handleRecoverClip(clip: ClipResult) {
    if (!token) {
      setAuthMode("login");
      setAuthOpen(true);
      return;
    }
    const clipId = clip.record_id || clip.clip_id || clip.id;
    setClipRecoveryStates((current) => ({
      ...current,
      [clipId]: {
        status: "queued",
        message: "Recovery queued. Retrying media generation for this clip.",
      },
    }));
    try {
      const job = await recoverClip(token, clipId);
      setClipRecoveryStates((current) => ({
        ...current,
        [clipId]: {
          jobId: job.job_id,
          status: "queued",
          message: job.message,
        },
      }));
      void pollRecoveryJob(clipId, job.job_id);
    } catch (recoveryError) {
      setClipRecoveryStates((current) => ({
        ...current,
        [clipId]: {
          status: "failed",
          message: recoveryError instanceof Error ? recoveryError.message : "Unable to start recovery.",
          error: recoveryError instanceof Error ? recoveryError.message : "Unable to start recovery.",
        },
      }));
    }
  }

  function handleCharacterAction(action: CharacterActionId) {
    if (action === "focus_source") {
      const input = document.querySelector<HTMLInputElement>("[data-lwa-source-input='true']");
      input?.scrollIntoView({ behavior: "smooth", block: "center" });
      input?.focus();
      return;
    }

    if (action === "review_lead") {
      document.getElementById("lead-clip")?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }

    if (action === "queue_lead") {
      const lead = orderedClips[0];
      if (lead && !isQueued(lead)) {
        handleToggleQueue(lead);
      }
      return;
    }

    if (action === "recover_strategy") {
      const firstStrategyClip = strategyOnlyClips[0];
      if (firstStrategyClip) {
        void handleRecoverClip(firstStrategyClip);
      }
      return;
    }

    if (action === "copy_script" && activeResult?.scripts?.main) {
      void navigator.clipboard?.writeText(activeResult.scripts.main);
    }
  }

  function renderSourceModeControls() {
    return (
      <div className="source-mode-controls">
        <span className="source-command-label mb-3 block">Mode</span>
        <div className="grid gap-2 sm:grid-cols-3">
          {sourceModeOptions.map((option) => {
            const active = sourceMode === option.value;
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => setSourceMode(option.value)}
                className={[
                  "source-mode-option rounded-[20px] border px-4 py-3 text-left transition",
                  active ? "source-mode-option-active" : "",
                ].join(" ")}
              >
                <span className="block text-sm font-semibold">{option.label}</span>
                <span className="mt-1 block text-xs text-ink/52">{option.detail}</span>
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  function renderSourceInput() {
    if (sourceMode === "idea") {
      return (
        <label className="source-command-field block">
          <span className="source-command-label mb-3 block">Idea</span>
          <textarea
            data-lwa-source-input="true"
            value={ideaPrompt}
            onChange={(event) => setIdeaPrompt(event.target.value)}
            onFocus={() => setInputFocused(true)}
            onBlur={() => setInputFocused(false)}
            placeholder="Describe the clip angle..."
            rows={4}
            className="source-command-input input-surface input-command w-full resize-none rounded-[28px] px-5 py-5 text-base"
          />
        </label>
      );
    }

    if (sourceMode === "image") {
      return (
        <div className="operator-tile rounded-[24px] p-4">
          <p className="text-sm font-medium text-ink">Image source</p>
          <p className="mt-2 text-sm leading-7 text-ink/68">
            {selectedUploadIsImage
              ? `Ready: ${selectedUploadName}`
              : "Upload an image first."}
          </p>
          <label className="mt-4 block">
            <span className="source-command-label mb-3 block">Angle</span>
            <textarea
              value={ideaPrompt}
              onChange={(event) => setIdeaPrompt(event.target.value)}
              placeholder="Motion, style, or platform..."
              rows={3}
              className="source-command-input input-surface input-command w-full resize-none rounded-[24px] px-5 py-4 text-base"
            />
          </label>
        </div>
      );
    }

    return (
      <label className="source-command-field block">
        <span className="source-command-label mb-3 block">Source</span>
        <input
          type="url"
          data-lwa-source-input="true"
          value={videoUrl}
          onChange={(event) => setVideoUrl(event.target.value)}
          onFocus={() => setInputFocused(true)}
          onBlur={() => setInputFocused(false)}
          placeholder="Paste a video URL..."
          className="source-command-input input-surface input-command w-full rounded-[28px] px-5 py-5 text-base"
        />
      </label>
    );
  }

  const homeGeneratorSection = (
    <section
      className="generator-command-card source-command-card rounded-[38px] p-6 sm:p-8"
      onMouseEnter={() => setGeneratorHovered(true)}
      onMouseLeave={() => setGeneratorHovered(false)}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="section-kicker">Source command</p>
          <h2 className="mt-3 text-2xl font-semibold text-ink sm:text-[2rem]">Drop in. Get clips.</h2>
          <p className="mt-3 max-w-xl text-sm leading-7 text-subtext/82">
            {generationMode === "quick"
              ? "Paste once. Post-ready stack."
              : "Learn what you keep."}
          </p>
        </div>
        <StatPill tone="accent">{useManualPlatform ? platform : "Auto recommend"}</StatPill>
      </div>

      <form onSubmit={onSubmit} className="mt-7 space-y-5">
        {!isGuest ? (
          <div className="mode-switch inline-flex rounded-full p-1">
            {[
              { value: "quick", label: "Quick mode" },
              { value: "pro", label: "Pro mode" },
            ].map((option) => {
              const active = generationMode === option.value;
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setGenerationMode(option.value as "quick" | "pro")}
                  className={["mode-pill rounded-full px-4 py-2 text-sm font-medium", active ? "mode-pill-active" : ""].join(" ")}
                >
                  {option.label}
                </button>
              );
            })}
          </div>
        ) : null}

        {!isGuest ? renderSourceModeControls() : null}

        {renderSourceInput()}

        {!isGuest ? (
        <div className="space-y-3">
          <div className="operator-tile rounded-[24px] p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm font-medium text-ink">Destination</p>
                <p className="mt-2 text-sm leading-7 text-ink/72">
                  {useManualPlatform
                    ? `Manual override is on for ${platform}.`
                    : "Auto stays on unless you already know the feed."}
                </p>
                <p className="mt-1 text-sm text-ink/50">
                  {useManualPlatform ? "Use this for fixed campaigns." : "Manual override is secondary."}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setUseManualPlatform((current) => !current)}
                className="secondary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium"
              >
                {useManualPlatform ? "Use auto recommendation" : "Set manual override"}
              </button>
            </div>
          </div>

          {useManualPlatform ? (
            <div>
              <span className="mb-3 block text-sm font-medium text-ink/84">Manual destination override</span>
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
                          ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]"
                          : "border-white/10 bg-white/[0.04] text-ink/72 hover:border-white/20 hover:bg-white/[0.06] hover:text-ink",
                      ].join(" ")}
                    >
                      {item}
                    </button>
                  );
                })}
              </div>
            </div>
          ) : null}
        </div>
        ) : null}

        {!isGuest ? (
        <div className={["grid gap-4", generationMode === "pro" ? "md:grid-cols-2" : ""].join(" ")}>
          <div className="operator-tile rounded-[24px] p-4">
            <p className="text-sm font-medium text-ink">Flow</p>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              {deliveryMoments.map((item) => (
                <div key={item.label} className="rounded-[18px] border border-white/10 bg-white/[0.04] px-3 py-3 text-sm text-ink/76">
                  <span className="block font-medium text-ink">{item.label}</span>
                  <span className="mt-2 block leading-6 text-ink/56">{item.detail}</span>
                </div>
              ))}
            </div>
          </div>

          {generationMode === "pro" ? (
            <div className="metric-tile rounded-[24px] p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-medium text-ink">Tighten future packs</p>
                  <p className="mt-1 text-sm text-ink/60">Bias new runs toward what you keep.</p>
                </div>
                <label className="secondary-button inline-flex items-center gap-3 rounded-full px-4 py-2.5 text-sm font-medium">
                  <input
                    type="checkbox"
                    checked={improveResults}
                    onChange={(event) => setImproveResults(event.target.checked)}
                    className="h-4 w-4 accent-[var(--gold)]"
                  />
                  Improve results
                </label>
              </div>
            </div>
          ) : null}
        </div>
        ) : null}

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          {!isGuest ? (
          <p className="text-sm text-ink/60">
            {isLoading ? `${loadingStages[loadingStageIndex]}. ${GENERATOR_COPY.loading}` : idleRunSummary}
          </p>
          ) : null}
          {isLiveStreamUrl ? (
            <div className="rounded-[14px] border border-red-400/25 bg-red-400/8 px-4 py-3">
              <p className="text-sm font-medium text-red-300">Live streams can't be clipped.</p>
              <p className="mt-1 text-xs text-red-300/60">Paste a regular uploaded YouTube video URL.</p>
            </div>
          ) : null}
          <button
            type="submit"
            onClick={(event) => {
              if (sourceMode === "video" && !videoUrl.trim() && !selectedUploadId) {
                event.preventDefault();
                setError("Paste a YouTube or TikTok URL to get started.");
              }
            }}
            disabled={isLoading || isLiveStreamUrl}
            className={
              isGuest
                ? "primary-button w-full rounded-full px-6 py-4 text-base font-semibold disabled:opacity-50"
                : "primary-button inline-flex min-w-[220px] items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
            }
          >
            {isGuest ? (isLoading ? "Finding clips..." : "Generate clips") : isLoading ? GENERATOR_COPY.submitting : GENERATOR_COPY.submit}
          </button>
        </div>

        {isLoading ? <LoadingSequence stages={loadingStages} activeIndex={loadingStageIndex} /> : null}

        {error ? <InlineAlert tone="error">{error}</InlineAlert> : null}
        {paywallMessage ? (
          <div className="rounded-[18px] border border-[var(--gold-border)] bg-[var(--gold-dim)] px-5 py-4">
            <p className="text-sm font-semibold text-[var(--gold)]">Out of credits.</p>
            <p className="mt-1 text-sm text-white/55">
              {user ? "Upgrade your plan to keep generating." : "Sign in to keep generating and save your clips."}
            </p>
            <div className="mt-3 flex gap-3">
              {!user ? (
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("login");
                    setAuthOpen(true);
                  }}
                  className="rounded-full bg-[var(--gold)] px-5 py-2.5 text-sm font-semibold text-black"
                >
                  Sign in free
                </button>
              ) : (
                <Link href="/settings" className="rounded-full bg-[var(--gold)] px-5 py-2.5 text-sm font-semibold text-black">
                  Upgrade plan
                </Link>
              )}
            </div>
          </div>
        ) : null}
      </form>
    </section>
  );

  const generatorSection = (
    <section className="space-y-6">
      <div className={["grid gap-6", isGuest ? "" : "xl:grid-cols-[minmax(0,1fr),320px]"].join(" ")}>
        <section
          className="generator-command-card source-command-card rounded-[38px] p-6 sm:p-8"
          onMouseEnter={() => setGeneratorHovered(true)}
          onMouseLeave={() => setGeneratorHovered(false)}
        >
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-2xl">
              <p className="section-kicker">{initialSection === "upload" ? "Upload + Generate" : rewriteSurfaceLabel("Generate")}</p>
              <h2 className="page-title mt-3 text-3xl font-semibold text-ink sm:text-[2.4rem]">
                {GENERATOR_COPY.title}
              </h2>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-subtext">
                {generationMode === "quick"
                  ? "Paste source. Get ranked clips."
                  : GENERATOR_COPY.subhead}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <StatPill tone="accent">{planSurface.name}</StatPill>
              <StatPill tone="signal">{activeResult ? "Live output" : "Premium review"}</StatPill>
            </div>
          </div>

          <form onSubmit={onSubmit} className="mt-8 space-y-6">
            {!isGuest ? (
              <div className="mode-switch inline-flex rounded-full p-1">
                {[
                  { value: "quick", label: "Quick mode" },
                  { value: "pro", label: "Pro mode" },
                ].map((option) => {
                  const active = generationMode === option.value;
                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => setGenerationMode(option.value as "quick" | "pro")}
                      className={["mode-pill rounded-full px-4 py-2 text-sm font-medium", active ? "mode-pill-active" : ""].join(" ")}
                    >
                      {option.label}
                    </button>
                  );
                })}
              </div>
            ) : null}

            {!isGuest ? renderSourceModeControls() : null}

            {renderSourceInput()}

            {!isGuest ? (
            <div className="space-y-3">
              <div className="operator-tile rounded-[24px] p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-sm font-medium text-ink">Destination</p>
                    <p className="mt-2 text-sm leading-7 text-ink/72">
                      {useManualPlatform
                      ? `Manual override is on for ${platform}.`
                      : "Auto stays on unless you already know the feed."}
                    </p>
                    <p className="mt-1 text-sm text-ink/50">
                      {useManualPlatform ? "Use this for fixed campaigns." : "Manual override is secondary."}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setUseManualPlatform((current) => !current)}
                    className="secondary-button inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium"
                  >
                    {useManualPlatform ? "Use auto recommendation" : "Set manual override"}
                  </button>
                </div>
              </div>

              {useManualPlatform ? (
                <div>
                  <span className="mb-3 block text-sm font-medium text-ink/84">Manual destination override</span>
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
                              ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]"
                              : "border-white/10 bg-white/[0.04] text-ink/72 hover:border-white/20 hover:bg-white/[0.06] hover:text-ink",
                          ].join(" ")}
                        >
                          {item}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ) : null}
            </div>
            ) : null}

            {!isGuest ? (
            <div className={["grid gap-4", generationMode === "pro" ? "md:grid-cols-2" : ""].join(" ")}>
              <div className="operator-tile rounded-[24px] p-4">
                <p className="text-sm font-medium text-ink">Flow</p>
                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                  {deliveryMoments.map((item) => (
                    <div key={item.label} className="rounded-[18px] border border-white/10 bg-white/[0.04] px-3 py-3 text-sm text-ink/76">
                      <span className="block font-medium text-ink">{item.label}</span>
                      <span className="mt-2 block leading-6 text-ink/56">{item.detail}</span>
                    </div>
                  ))}
                </div>
              </div>

              {generationMode === "pro" ? (
                <div className="metric-tile rounded-[24px] p-4">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <p className="text-sm font-medium text-ink">Tighten future packs</p>
                      <p className="mt-1 text-sm text-ink/60">Learn from what you keep.</p>
                      {preferenceProfile.topPackagingAngle || preferenceProfile.topHookStyle ? (
                        <p className="mt-3 text-sm text-accent">
                          Favoring {preferenceProfile.topPackagingAngle || "strong"} packaging
                          {preferenceProfile.topHookStyle ? ` and ${preferenceProfile.topHookStyle} hooks` : ""}.
                        </p>
                      ) : (
                        <p className="mt-3 text-sm text-ink/46">Mark what lands.</p>
                      )}
                    </div>
                    <label className="secondary-button inline-flex items-center gap-3 rounded-full px-4 py-2.5 text-sm font-medium">
                      <input
                        type="checkbox"
                        checked={improveResults}
                        onChange={(event) => setImproveResults(event.target.checked)}
                        className="h-4 w-4 accent-[var(--gold)]"
                      />
                      Improve results
                    </label>
                  </div>
                </div>
              ) : null}
            </div>
            ) : null}

            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              {!isGuest ? (
              <p className="text-sm text-ink/60">
                {isLoading
                  ? `${loadingStages[loadingStageIndex]}. ${GENERATOR_COPY.loading}`
                  : activeResult
                    ? "Clip pack ready. Review first, queue next, export when it fits."
                    : idleRunSummary}
              </p>
              ) : null}
              {isLiveStreamUrl ? (
                <div className="rounded-[14px] border border-red-400/25 bg-red-400/8 px-4 py-3">
                  <p className="text-sm font-medium text-red-300">Live streams can't be clipped.</p>
                  <p className="mt-1 text-xs text-red-300/60">Paste a regular uploaded YouTube video URL.</p>
                </div>
              ) : null}
              <button
                type="submit"
                onClick={(event) => {
                  if (sourceMode === "video" && !videoUrl.trim() && !selectedUploadId) {
                    event.preventDefault();
                    setError("Paste a YouTube or TikTok URL to get started.");
                  }
                }}
                disabled={isLoading || isLiveStreamUrl}
                className={
                  isGuest
                    ? "primary-button w-full rounded-full px-6 py-4 text-base font-semibold disabled:opacity-50"
                    : "primary-button inline-flex min-w-[240px] items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
                }
              >
                {isGuest ? (isLoading ? "Finding clips..." : "Generate clips") : isLoading ? GENERATOR_COPY.submitting : GENERATOR_COPY.submit}
              </button>
            </div>

            {isLoading ? <LoadingSequence stages={loadingStages} activeIndex={loadingStageIndex} /> : null}

            {error ? <InlineAlert tone="error">{error}</InlineAlert> : null}

            {paywallMessage ? (
              <div className="rounded-[18px] border border-[var(--gold-border)] bg-[var(--gold-dim)] px-5 py-4">
                <p className="text-sm font-semibold text-[var(--gold)]">Out of credits.</p>
                <p className="mt-1 text-sm text-white/55">
                  {user ? "Upgrade your plan to keep generating." : "Sign in to keep generating and save your clips."}
                </p>
                <div className="mt-3 flex gap-3">
                  {!user ? (
                    <button
                      type="button"
                      onClick={() => {
                        setAuthMode("login");
                        setAuthOpen(true);
                      }}
                      className="rounded-full bg-[var(--gold)] px-5 py-2.5 text-sm font-semibold text-black"
                    >
                      Sign in free
                    </button>
                  ) : (
                    <Link href="/settings" className="rounded-full bg-[var(--gold)] px-5 py-2.5 text-sm font-semibold text-black">
                      Upgrade plan
                    </Link>
                  )}
                </div>
              </div>
            ) : null}
          </form>
        </section>

        {!isGuest ? (
        <aside className="space-y-4">
          <div className="glass-panel rounded-[28px] p-5">
            <p className="section-kicker">Plan status</p>
            <h3 className="mt-3 text-2xl font-semibold text-ink">{planSurface.name}</h3>
            <div className="mt-5 grid gap-3">
              <MetricTile
                label="Credits left"
                value={typeof creditsRemaining === "number" ? String(creditsRemaining) : String(planLimits.generationsPerDay)}
                detail={typeof creditsRemaining === "number" ? "Available today" : "Daily run limit"}
              />
              <MetricTile label="Clip access" value={String(planLimits.clipLimit)} detail="Visible clips per run" />
              <MetricTile label="Uploads" value={String(planLimits.uploadsPerDay)} detail="Local source uploads today" />
            </div>
            <div className="mt-4 space-y-3">
              {!activeFeatureFlags.premium_exports ? (
                <div className="metric-tile rounded-[24px] px-4 py-3 text-sm text-ink/72">
                  Pro unlocks clean exports, 20 clips, stronger hook coverage, and wallet visibility.
                </div>
              ) : null}
              {!activeFeatureFlags.campaign_mode || !activeFeatureFlags.posting_queue ? (
                <div className="signal-card rounded-[24px] px-4 py-3 text-sm text-ink/78">
                  Scale adds campaign coordination, posting queue controls, and the deeper operator layer.
                </div>
              ) : null}
            </div>
            <p className="mt-4 text-sm leading-7 text-ink/60">{planSurface.watermark ? "Free exports keep the watermark." : "Clean exports are unlocked."}</p>
          </div>

          <div className="glass-panel rounded-[28px] p-5">
            <p className="section-kicker">Upload a source</p>
            <h3 className="mt-3 text-xl font-semibold text-ink">Run it from your own file</h3>
            <p className="mt-3 text-sm leading-7 text-ink/60">
              Video keeps the clipping flow. Image moves through generation. Your first upload works before signup.
            </p>
            <p className="mt-4 text-sm text-accent">{uploadingFileName ? `Uploading ${uploadingFileName}...` : activeSourceLabel}</p>
            <label className="secondary-button mt-5 inline-flex w-full cursor-pointer items-center justify-center rounded-full px-5 py-3 text-sm font-medium">
              Upload source file
              <input
                type="file"
                accept=".mp4,.mov,.m4v,.webm,.mp3,.wav,.m4a,.aac,.ogg,.oga,.flac,.jpg,.jpeg,.png,.webp,.heic,.heif,video/*,audio/*,image/*"
                className="hidden"
                onChange={onUploadSelected}
              />
            </label>
          </div>

          <div className="glass-panel rounded-[28px] p-5">
            <p className="section-kicker">Flow</p>
            <div className="mt-4 space-y-3 text-sm leading-7 text-ink/68">
              <p>1. LWA finds the moments worth cutting and recommends the first destination.</p>
              <p>2. Review finished previews before you spend time on ideas-only cuts.</p>
              <p>3. Queue the winners and export the assets that are already ready.</p>
            </div>
          </div>
        </aside>
        ) : null}
      </div>
    </section>
  );

  const resultsSection = activeResult ? (
    <section id="lwa-results-section" className={["result-screen space-y-6", motionLocked ? "result-screen--locked" : ""].join(" ")}>
      <div className="hero-card rounded-[32px] p-6 sm:p-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="section-kicker">{RESULTS_COPY.kicker}</p>
            <h3 className="page-title mt-3 text-3xl font-semibold text-ink sm:text-[2.4rem]">{RESULTS_COPY.title}</h3>
            <p className="mt-4 text-sm leading-7 text-subtext">{RESULTS_COPY.subhead}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <StatPill tone="signal">{renderedClipCount} finished previews</StatPill>
            {strategyOnlyClipCount ? <StatPill tone="neutral">{strategyOnlyClipCount} ideas only</StatPill> : null}
            <StatPill tone="accent">{effectiveTargetPlatform}</StatPill>
            {platformDecision === "manual" ? <StatPill tone="neutral">Manual</StatPill> : <StatPill tone="signal">Auto</StatPill>}
          </div>
        </div>
      </div>

      <div className={["grid gap-6", isGuest ? "" : "xl:grid-cols-[minmax(0,1fr),340px]"].join(" ")}>
        <div className="space-y-6">
          <div className="glass-panel rounded-[28px] p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-3xl">
                <p className="section-kicker">LWA recommendation</p>
                <h4 className="mt-3 text-2xl font-semibold text-ink">Post this first. Then move the stack.</h4>
                <div className="mt-4 flex flex-wrap gap-2">
                  {recommendedPlatform ? <StatPill tone="accent">Recommended: {recommendedPlatform}</StatPill> : null}
                  {recommendedContentType ? <StatPill tone="signal">{recommendedContentType}</StatPill> : null}
                  {recommendedOutputStyle ? <StatPill tone="neutral">{recommendedOutputStyle}</StatPill> : null}
                </div>
                {platformRecommendationReason ? (
                  <p className="mt-4 max-w-2xl text-sm leading-7 text-ink/58">{platformRecommendationReason}</p>
                ) : null}
                {activeResult.processing_summary?.recommended_next_step ? (
                  <p className="mt-3 text-sm font-medium text-ink/82">{activeResult.processing_summary.recommended_next_step}</p>
                ) : null}
              </div>
              <div className="flex flex-wrap gap-3">
                {leadPreviewReady ? (
                  <a
                    href={leadPreviewUrl || undefined}
                    target="_blank"
                    rel="noreferrer"
                    className="secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium"
                  >
                    Open lead preview
                  </a>
                ) : null}
                {leadExportReady ? (
                  <a
                    href={leadExportUrl || undefined}
                    download
                    className="primary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold"
                  >
                    Export lead asset
                  </a>
                ) : isGuest ? (
                  <button
                    type="button"
                    onClick={() => void handleExportBundle()}
                    disabled={bundleExportState === "exporting" || !activeResult?.clips?.length}
                    className="primary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {bundleExportState === "exporting" ? "Building bundle..." : "Export bundle"}
                  </button>
                ) : (
                  <span className="rounded-full border border-accentCrimson/22 bg-[linear-gradient(135deg,rgba(122,16,42,0.24),rgba(124,58,237,0.1))] px-4 py-2 text-sm text-[#ffe4eb]">
                    Bundle export available below
                  </span>
                )}
              </div>
              {isGuest && bundleExportMessage ? (
                <p className={["mt-3 text-sm", bundleExportState === "failed" ? "text-red-200" : "text-[var(--gold)]"].join(" ")}>
                  {bundleExportMessage}
                </p>
              ) : null}
            </div>
          </div>

          {isGuest && hasStrategyOnlyWithoutPreview ? (
            <InlineAlert tone="violet">
              Hooks and packaging are ready. Preview video requires a standard uploaded YouTube video — not a live stream.
            </InlineAlert>
          ) : !renderedClipCount ? (
            <InlineAlert tone="violet" title="Ideas ready">
              LWA returned the package, hooks, captions, and posting order, but this run did not produce preview media. Review the ideas now, then retry with a longer or cleaner source if you need playable output.
            </InlineAlert>
          ) : !previewReadyCount ? (
            <InlineAlert tone="violet" title="Playable preview pending">
              This run returned media, but not a playable preview for every cut. Review the ready clips first, then use the ideas-only stack to decide what is worth rerunning.
            </InlineAlert>
          ) : null}

          {renderedHeroClip ? (
            <div className="space-y-3">
              {!isGuest ? <p className="section-kicker">Lead answer</p> : null}
              <HeroClip
                clip={renderedHeroClip}
                compact={isGuest}
                feedbackVote={!isGuest ? feedbackByClipId[renderedHeroClip.record_id || renderedHeroClip.clip_id || renderedHeroClip.id] || null : null}
                onVote={!isGuest ? handleFeedbackVote : undefined}
                queued={isQueued(renderedHeroClip)}
                onToggleQueue={handleToggleQueue}
                recoveryState={clipRecoveryStates[resolveClipQueueId(renderedHeroClip)] || null}
                onRecover={handleRecoverClip}
              />
            </div>
          ) : null}

          {renderedGridClips.length ? (
            <div className="space-y-4">
              {!isGuest ? (
              <div className="flex items-end justify-between gap-4">
                <div>
                  <p className="section-kicker">{RESULT_COPY.finishedPreviews}</p>
                  <h4 className="mt-2 text-2xl font-semibold text-ink">READY TO POST NOW</h4>
                  <p className="mt-3 max-w-2xl text-sm leading-7 text-ink/60">
                    Finished previews ready for distribution.
                  </p>
                </div>
              </div>
              ) : null}
              <div className={["grid gap-5 md:grid-cols-2", isGuest ? "" : "xl:grid-cols-3"].join(" ")}>
                {renderedGridClips.map((clip) => (
                  <ClipCard
                    key={clip.id}
                    clip={clip}
                    compact={isGuest}
                    feedbackVote={!isGuest ? feedbackByClipId[clip.record_id || clip.clip_id || clip.id] || null : null}
                    onVote={!isGuest ? handleFeedbackVote : undefined}
                    queued={isQueued(clip)}
                    onToggleQueue={handleToggleQueue}
                    recoveryState={clipRecoveryStates[resolveClipQueueId(clip)] || null}
                    onRecover={handleRecoverClip}
                  />
                ))}
              </div>
            </div>
          ) : null}

          {strategyHeroClip ? (
            <div className="space-y-3">
              {!isGuest ? <p className="section-kicker">Top high-leverage idea</p> : null}
              <HeroClip
                clip={strategyHeroClip}
                compact={isGuest}
                feedbackVote={!isGuest ? feedbackByClipId[strategyHeroClip.record_id || strategyHeroClip.clip_id || strategyHeroClip.id] || null : null}
                onVote={!isGuest ? handleFeedbackVote : undefined}
                queued={isQueued(strategyHeroClip)}
                onToggleQueue={handleToggleQueue}
                recoveryState={clipRecoveryStates[resolveClipQueueId(strategyHeroClip)] || null}
                onRecover={handleRecoverClip}
              />
            </div>
          ) : null}

          {strategyGridClips.length ? (
            <div className="space-y-4">
              {!isGuest ? (
              <div className="flex items-end justify-between gap-4">
                <div>
                  <p className="section-kicker">{RESULT_COPY.ideasOnly}</p>
                  <h4 className="mt-2 text-2xl font-semibold text-ink">HIGH-LEVERAGE IDEAS</h4>
                  <p className="mt-3 max-w-2xl text-sm leading-7 text-ink/60">
                    Strong angles waiting on preview.
                  </p>
                </div>
              </div>
              ) : null}
              <div className={["grid gap-5 md:grid-cols-2", isGuest ? "" : "xl:grid-cols-3"].join(" ")}>
                {strategyGridClips.map((clip) => (
                  <ClipCard
                    key={clip.id}
                    clip={clip}
                    compact={isGuest}
                    feedbackVote={!isGuest ? feedbackByClipId[clip.record_id || clip.clip_id || clip.id] || null : null}
                    onVote={!isGuest ? handleFeedbackVote : undefined}
                    queued={isQueued(clip)}
                    onToggleQueue={handleToggleQueue}
                    recoveryState={clipRecoveryStates[resolveClipQueueId(clip)] || null}
                    onRecover={handleRecoverClip}
                  />
                ))}
              </div>
            </div>
          ) : null}
        </div>

        {!isGuest ? (
        <div className="space-y-5">
          <ReadyQueuePanel items={readyQueue} onMove={handleMoveQueue} onRemove={handleRemoveQueue} onClear={handleClearQueue} />

          {orderedClips.length ? <ReviewOrderPanel clips={orderedClips} /> : null}

          <div className="glass-panel rounded-[28px] p-5">
            <p className="section-kicker">Packaging + export rail</p>
            <h4 className="mt-3 text-xl font-semibold text-ink">What is ready to move now</h4>
            <button
              type="button"
              onClick={() => void handleExportBundle()}
              disabled={bundleExportState === "exporting" || !activeResult?.clips?.length}
              className="secondary-button mt-4 inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-60"
            >
              {bundleExportState === "exporting" ? "Building bundle..." : "Export bundle"}
            </button>
            {bundleExportMessage ? (
              <p className={["mt-3 text-sm", bundleExportState === "failed" ? "text-red-200" : "text-[var(--gold)]"].join(" ")}>
                {bundleExportMessage}
              </p>
            ) : null}
            <div className="mt-4 grid gap-3">
              <MetricTile
                label={RESULT_COPY.finishedPreviews}
                value={String(renderedClipCount)}
                detail={renderedClipCount ? "These are ready to distribute right now" : "No finished preview came back yet"}
              />
              <MetricTile
                label={RESULT_COPY.ideasOnly}
                value={String(strategyOnlyClipCount)}
                detail={strategyOnlyClipCount ? "Retry preview when you want media generated" : "Every visible clip has a preview"}
              />
              <MetricTile
                label="Export unlocked"
                value={String(exportReadyCount)}
                detail={
                  exportReadyCount
                    ? "Downloads are live now"
                    : activeFeatureFlags.premium_exports
                      ? "No clip export came back yet"
                      : "Upgrade unlocks direct clip export"
                }
              />
              <MetricTile
                label="Lead preview"
                value={leadPreviewReady ? "Yes" : "No"}
                detail={leadPreviewReady ? "Open the lead asset and move immediately" : "No lead preview asset came back yet"}
              />
            </div>
          </div>

          <div className="glass-panel rounded-[28px] p-5">
            <p className="section-kicker">Signals</p>
            <h4 className="mt-3 text-xl font-semibold text-ink">What this workspace is learning</h4>
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
            <p className="section-kicker">{RESULTS_COPY.executionGuide}</p>
            <h4 className="mt-3 text-xl font-semibold text-ink">Decision rail</h4>
            <div className="mt-4 space-y-3 text-sm text-ink/72">
              <p>1. Post the lead clip first.</p>
              <p>2. Export the ready-now cuts before you spend time on ideas-only cuts.</p>
              <p>3. Use the high-leverage lane for testing and rerender decisions.</p>
            </div>
            <p className="mt-4 text-sm text-accent">
              {improveResults ? "Preference learning is on." : "Turn on Improve results to apply local learning."}
            </p>
          </div>
        </div>
        ) : null}
      </div>
    </section>
  ) : null;

  const emptyGeneratorState = !activeResult && !isLoading && showGenerator ? (
    <section className="glass-panel rounded-[28px] p-6 sm:p-8">
      <p className="section-kicker">Ready</p>
      <h3 className="mt-3 text-2xl font-semibold text-ink sm:text-3xl">Your next pack lands here</h3>
      <p className="mt-3 max-w-2xl text-sm leading-7 text-ink/60">{GENERATOR_COPY.outputIdle}</p>
    </section>
  ) : null;

  return (
    <main className={["app-shell-grid min-h-screen", motionLocked ? "results-motion-locked" : ""].join(" ")}>
      <AIBackground
        variant={isHome ? "home" : "workspace"}
        worldState={worldState}
        worldPhase={worldPhase}
        generationMode={generationMode}
        signal={worldSignal}
      />
      <CharacterLayer
        isLoading={isLoading}
        loadingStageIndex={loadingStageIndex}
        hasSource={hasSourceSelected}
        hasResult={Boolean(activeResult)}
        renderedClipCount={renderedClipCount}
        strategyOnlyClipCount={strategyOnlyClipCount}
        recoveryActive={recoveryActive}
        result={activeResult}
        orderedClips={orderedClips}
        renderedClips={renderedClips}
        strategyOnlyClips={strategyOnlyClips}
        readyQueue={readyQueue}
        scripts={activeResult?.scripts}
        onAction={handleCharacterAction}
      />
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
            variant="home"
            showTagline
            rightSlot={
              <div className="flex items-center gap-2">
                {user ? (
                  <>
                    <Link href="/dashboard" className="secondary-button inline-flex rounded-full px-4 py-2.5 text-sm font-medium">
                      {HERO_COPY.secondaryCta}
                    </Link>
                    <span className="credits-bar hidden sm:inline-flex">
                      <span className="credits-count">{typeof creditsRemaining === "number" ? creditsRemaining : planLimits.generationsPerDay}</span>
                      credits
                    </span>
                  </>
                ) : (
                  <>
                    <span className="credits-bar hidden sm:inline-flex">
                      <span className="credits-count">{planLimits.generationsPerDay || 1}</span>
                      credits
                    </span>
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
                      Generate clips
                    </button>
                  </>
                )}
              </div>
            }
          />

          <section className="home-stage mx-auto grid max-w-5xl gap-8 pb-10 pt-14 lg:items-start">
            <div className="space-y-6 text-center">
              <div className="home-stage-grid" aria-hidden="true">
                <div className="home-stage-sigil" />
                <div className="home-stage-constellation" />
                <div className="home-stage-fog" />
              </div>

              <div className="space-y-5">
                <div className="inline-flex items-center justify-center gap-3">
                  <span className="home-brand-mark flex h-11 w-11 items-center justify-center rounded-2xl border border-[var(--gold-border)] bg-[var(--gold-dim)]">
                    <img src="/brand-source/omega-mark.png" alt="LWA omega mark" className="h-7 w-7 object-contain" />
                  </span>
                  <p className="section-kicker">{HERO_COPY.kicker}</p>
                </div>
                <h1 className="hero-headline mx-auto max-w-5xl text-5xl font-semibold leading-[0.92] text-ink sm:text-7xl lg:text-[5.9rem]">
                  <span className="text-gradient">{HERO_COPY.headline}</span>
                </h1>
                <p className="mx-auto max-w-2xl text-base leading-8 text-subtext sm:text-lg">
                  {HERO_COPY.subhead}
                </p>
              </div>

              <div className="flex flex-wrap justify-center gap-3">
                <Link href="/generate" className="primary-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold">
                  {HERO_COPY.primaryCta}
                </Link>
                <Link
                  href={user ? "/dashboard" : "/signup"}
                  className="secondary-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-medium"
                >
                  {HERO_COPY.secondaryCta}
                </Link>
              </div>

              <div className="world-identity-card mx-auto max-w-2xl rounded-[32px] p-5 text-left">
                <p className="section-kicker">Live system</p>
                <h2 className="mt-3 text-2xl font-semibold text-ink">A clip engine with a world around it.</h2>
                <p className="mt-3 text-sm leading-7 text-ink/62">
                  Edge entities react to source, processing, and results without blocking the product.
                </p>
              </div>

              <div className="flex flex-wrap justify-center gap-2">
                {featureProof.map((item, index) => (
                  <StatPill key={item} tone={index === 1 ? "signal" : "neutral"}>
                    {item}
                  </StatPill>
                ))}
              </div>
            </div>

            <div className="home-command-wrap space-y-5">
              {homeGeneratorSection}
            </div>
          </section>

          {!activeResult && !isLoading ? <HomeDiscoveryGrid sections={homeDiscoverySections.slice(0, 3)} /> : null}
          {resultsSection ? <div className="space-y-6 pb-8">{resultsSection}</div> : null}
        </div>
      ) : (
        <div className="mx-auto w-full max-w-[1480px] px-4 py-6 sm:px-6 lg:px-8">
          <Navbar
            items={visibleAppNavItems.map((item) => ({ href: item.href, label: item.label }))}
            variant="workspace"
            compactLogo
            rightSlot={
              user ? (
                <div className="flex items-center gap-2">
                  <span className="credits-bar hidden lg:inline-flex">
                    <span className="credits-count">{typeof creditsRemaining === "number" ? creditsRemaining : planLimits.generationsPerDay}</span>
                    credits
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
                {isGuest ? (
                  <div className="glass-panel rounded-[28px] p-5">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-[var(--gold-border)] bg-[var(--gold-dim)]">
                      <img src="/brand-source/omega-mark.png" alt="LWA" className="h-8 w-8 object-contain" />
                    </div>
                    <h3 className="mt-5 text-2xl font-semibold text-ink">Generate clips.</h3>
                    <p className="mt-3 text-sm leading-7 text-ink/62">Drop a source. Get what to post first.</p>
                    <button
                      type="button"
                      onClick={() => {
                        setAuthMode("login");
                        setAuthOpen(true);
                      }}
                      className="secondary-button mt-5 inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium"
                    >
                      Sign in for history, queue, and campaigns
                    </button>
                  </div>
                ) : (
                  <>
                    <WorkspaceRailCard
                      label="Studio pulse"
                      title="Generate first. Move fast."
                      description="Move from generation to queue, assignments, and payout readiness."
                    >
                      <div className="mt-5 flex flex-wrap gap-2">
                        <StatPill tone="accent">{planSurface.name}</StatPill>
                        <StatPill tone="neutral">{readyQueue.length} in queue</StatPill>
                      </div>
                    </WorkspaceRailCard>

                    <WorkspaceRailCard label="Account" title={user?.email || "Account"} description={`Role ${user?.role || "creator"}`}>
                      <div className="mt-5 grid gap-3">
                        <MetricTile label="Clip packs" value={String(clipPacks.length)} detail="Saved history" />
                        <MetricTile label="Uploads" value={String(uploads.length)} detail="Reusable sources" />
                        <MetricTile label="Credits" value={typeof creditsRemaining === "number" ? String(creditsRemaining) : String(planLimits.generationsPerDay)} detail="Generation capacity" />
                      </div>
                    </WorkspaceRailCard>

                    <WorkspaceRailCard
                      label="Next move"
                      title="Use the system in order"
                      description="Generate, queue winners, then move into campaign flow."
                    />
                  </>
                )}
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
                <section className="rounded-[24px] border border-accentCrimson/22 bg-accentCrimson/8 px-5 py-4 text-sm text-rose-100">
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
          ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]"
          : tone === "signal"
            ? "border-[var(--gold-border)] bg-black/30 text-[var(--text-primary)]"
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
          title: "Viral-ready outputs",
          detail: "Fit and post order come back structured.",
        },
        {
          title: "Packaging intelligence",
          detail: "Hooks, thumbnail lines, CTAs, and caption styles come back together.",
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

function HomeDiscoveryGrid({
  sections,
}: {
  sections: ReadonlyArray<{
    id: string;
    kicker: string;
    title: string;
    body: string;
    bullets: readonly string[];
    links?: readonly { href: string; label: string }[];
  }>;
}) {
  return (
    <section className="pb-10">
      <div className="grid gap-4 lg:grid-cols-3">
        {sections.map((section, index) => (
          <article
            key={section.id}
            className={index === 0 ? "home-proof-card home-proof-card-lead rounded-[30px] p-5" : "glass-panel rounded-[30px] p-5"}
          >
            <p className="section-kicker">{section.kicker}</p>
            <h3 className="mt-3 text-xl font-semibold text-ink" dir="auto">
              {section.title}
            </h3>
            <p className="mt-3 text-sm leading-7 text-subtext" dir="auto">
              {section.body}
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              {section.bullets.slice(0, 2).map((bullet) => (
                <span key={bullet} className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-2 text-xs font-medium text-ink/78" dir="auto">
                  {bullet}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function ReviewOrderPanel({ clips }: { clips: ClipResult[] }) {
  const ordered = clips.slice(0, 4);

  return (
    <div className="glass-panel rounded-[28px] p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="section-kicker">Post order</p>
          <h4 className="mt-3 text-xl font-semibold text-ink">Move this stack</h4>
        </div>
        <StatPill tone="accent">{ordered.length} clips</StatPill>
      </div>

      <div className="mt-5 space-y-3">
        {ordered.map((clip, index) => {
          const order = clip.post_rank || clip.best_post_order || clip.rank || index + 1;
          const detail = clip.thumbnail_text || clip.cta_suggestion || clip.packaging_angle || "Ready for review";
          const active = index === 0;
          const authority = order === 1 ? "POST FIRST" : order === 2 ? "POST SECOND" : order === 3 ? "TEST THIRD" : "MOVE LATER";

          return (
            <div
              key={clip.record_id || clip.clip_id || clip.id}
              className={[
                "review-order-card rounded-[22px] p-4",
                active ? "review-order-card-active" : "panel-subtle",
              ].join(" ")}
            >
              <div className="flex items-start gap-3">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-white/10 bg-white/[0.05] text-sm font-semibold text-ink/84">
                  {order}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="line-clamp-1 text-sm font-semibold text-ink">{clip.hook}</p>
                    {active ? <StatPill tone="signal">Lead</StatPill> : null}
                    <StatPill tone={active ? "accent" : "neutral"}>{authority}</StatPill>
                  </div>
                  <p className="mt-2 line-clamp-2 text-xs leading-6 text-ink/62">{detail}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
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

function LoadingSequence({ stages, activeIndex }: { stages: string[]; activeIndex: number }) {
  return (
    <div className="panel-subtle rounded-[24px] px-5 py-6">
      <div className="mb-5 flex items-center gap-3">
        <div className="relative flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-white/[0.04]">
          <div className="absolute inset-0 animate-spin rounded-full border-2 border-white/10 border-t-accent" />
          <img src="/brand/lwa-mark.svg" alt="LWA" className="relative h-6 w-6 opacity-90" />
        </div>
        <div>
          <p className="text-lg font-medium text-ink">LWA is building outputs</p>
          <p className="text-sm text-ink/60">Real media in. Clips, copy, and previews out.</p>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        {stages.map((stage, index) => (
          <div
            key={stage}
            className={[
              "loading-stage rounded-[20px] px-4 py-4",
              index === activeIndex ? "loading-stage-active" : "",
            ].join(" ")}
          >
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Step {index + 1}</p>
            <p className="mt-2 text-sm font-medium text-ink">{stage}</p>
          </div>
        ))}
      </div>
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
      ? "border-[rgba(139,0,0,0.35)] bg-[var(--crimson-dim)] text-red-100"
      : "border-[var(--gold-border)] bg-[var(--gold-dim)] text-ink";

  return (
    <div className={["rounded-[24px] border px-5 py-4 text-sm", toneClass].join(" ")}>
      {title ? <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">{title}</p> : null}
      {children}
    </div>
  );
}
