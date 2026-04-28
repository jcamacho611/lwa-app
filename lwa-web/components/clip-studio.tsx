"use client";

import Link from "next/link";
import { ChangeEvent, FormEvent, ReactNode, useEffect, useMemo, useRef, useState } from "react";
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
import { MoneyCtaPanel } from "./money-cta-panel";
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
  ExportBundleResponse,
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
  loadClipRenderStatus,
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
  retryClipRender,
  updateCampaign,
  updateCampaignAssignment,
  updateScheduledPost,
  uploadSource,
  normalizeUrl,
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
import { buildAllPackagesText, buildClipPackageText, getClipScore, isRenderedClip } from "../lib/clip-utils";
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
  return isRenderedClip(clip);
}

function clipHasShotPlan(clip: ClipResult) {
  return Boolean(clip.shot_plan?.length);
}

function getClipPreviewUrl(clip?: ClipResult | null) {
  if (!clip) {
    return null;
  }

  return (
    clip.preview_url ||
    clip.edited_clip_url ||
    clip.clip_url ||
    clip.raw_clip_url ||
    clip.download_url ||
    null
  );
}

function reconcileGenerateResponseMediaTruth(data: GenerateResponse): GenerateResponse {
  const clips = (data.clips || []).map((clip) => {
    const previewUrl = getClipPreviewUrl(clip);
    const hasRenderedMedia = Boolean(previewUrl);

    if (!hasRenderedMedia) {
      return {
        ...clip,
        is_rendered: clip.is_rendered === true ? true : false,
        rendered: clip.rendered === true ? true : false,
        is_strategy_only: clip.is_strategy_only === false ? false : true,
        strategy_only: clip.strategy_only === false ? false : true,
        render_status: clip.render_status || "strategy_only",
      };
    }

    return {
      ...clip,
      preview_url: clip.preview_url || previewUrl,
      clip_url: clip.clip_url || previewUrl,
      edited_clip_url: clip.edited_clip_url || previewUrl,
      is_rendered: true,
      rendered: true,
      is_strategy_only: false,
      strategy_only: false,
      render_status: clip.render_status === "strategy_only" ? "ready" : clip.render_status || "ready",
      rendered_status: clip.rendered_status || "ready",
      export_bundle: clip.export_bundle
        ? {
            ...clip.export_bundle,
            preview_ready: true,
          }
        : clip.export_bundle,
    };
  });

  const renderedClipCount = clips.filter((clip) => clipHasRenderedMedia(clip)).length;
  const strategyOnlyClipCount = Math.max(clips.length - renderedClipCount, 0);
  const firstRenderedClip = clips.find((clip) => clipHasRenderedMedia(clip));
  const firstRenderedPreviewUrl = getClipPreviewUrl(firstRenderedClip);

  return {
    ...data,
    clips,
    preview_asset_url: data.preview_asset_url || firstRenderedPreviewUrl || null,
    download_asset_url: data.download_asset_url || firstRenderedClip?.download_url || null,
    thumbnail_url: data.thumbnail_url || firstRenderedClip?.thumbnail_url || firstRenderedClip?.preview_image_url || null,
    processing_summary: data.processing_summary
      ? {
          ...data.processing_summary,
          rendered_clip_count: renderedClipCount,
          strategy_only_clip_count: strategyOnlyClipCount,
          raw_assets_created: Math.max(data.processing_summary.raw_assets_created || 0, renderedClipCount),
          edited_assets_created: Math.max(data.processing_summary.edited_assets_created || 0, renderedClipCount),
        }
      : data.processing_summary,
  };
}

function formatBundleBytes(value?: number | null) {
  if (typeof value !== "number" || !Number.isFinite(value) || value <= 0) {
    return null;
  }
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function bundleArtifactLabel(value: string) {
  switch (value) {
    case "package_json":
      return "Package JSON";
    case "caption_txt":
      return "Caption TXT";
    case "subtitle_srt":
      return "Subtitle SRT";
    case "subtitle_vtt":
      return "Subtitle VTT";
    default:
      return value.replace(/_/g, " ");
  }
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
  { href: "/campaigns", label: rewriteSurfaceLabel("Campaigns") },
] as const;

const VIDEO_LOADING_STAGES = ["Source ingest", "Moment scan", "Clip ranking", "Packaging", "Render/export", "Delivery"];

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
  initialUrl?: string;
  autoOpenAuth?: boolean;
  initialAuthMode?: "login" | "signup";
  pageLabel?: string;
  pageTitle?: string;
  pageDescription?: string;
};

export function ClipStudio({
  initialSection = "home",
  initialUrl = "",
  autoOpenAuth = false,
  initialAuthMode = "login",
  pageLabel,
  pageTitle,
  pageDescription,
}: ClipStudioProps) {
  const generationControllerRef = useRef<AbortController | null>(null);
  const [videoUrl, setVideoUrl] = useState(initialUrl);
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
  const [latestBundleExport, setLatestBundleExport] = useState<ExportBundleResponse | null>(null);
  const [copiedPackageAction, setCopiedPackageAction] = useState<"lead" | "rendered" | "strategy" | "all" | null>(null);
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

  useEffect(() => {
    setLatestBundleExport(null);
    setBundleExportState("idle");
    setBundleExportMessage(null);
  }, [activeResult?.request_id]);

  const loadingStages =
    sourceMode === "idea"
      ? ["Source ingest", "Moment scan", "Clip ranking", "Packaging", "Render/export", "Delivery"]
      : sourceMode === "image"
        ? ["Source ingest", "Moment scan", "Clip ranking", "Packaging", "Render/export", "Delivery"]
        : VIDEO_LOADING_STAGES;

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
          title: "Track value readiness",
          description: "See balance and manual payout readiness.",
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
      setLoadingStageIndex((current) => (current + 1) % Math.max(loadingStages.length, 1));
    }, 1400);

    return () => window.clearInterval(interval);
  }, [isLoading, loadingStages.length]);

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
    if (sourceMode === "video" && !videoUrl.trim() && !selectedUploadId) {
      setError(isGuest ? "Paste a public source URL to generate your clip pack." : "Paste a public source URL or upload a file to generate your clip pack.");
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

    const normalizedVideoUrl = sourceMode === "video" ? normalizeUrl(videoUrl) : "";
    if (sourceMode === "video" && normalizedVideoUrl && normalizedVideoUrl !== videoUrl) {
      setVideoUrl(normalizedVideoUrl);
    }

    generationControllerRef.current?.abort();
    const controller = new AbortController();
    generationControllerRef.current = controller;
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
          url: sourceMode === "video" ? normalizedVideoUrl || undefined : undefined,
          platform: useManualPlatform ? platform : undefined,
          uploadFileId: sourceMode === "idea" ? undefined : selectedUploadId || undefined,
          contentAngle: improveResults ? preferenceProfile.topPackagingAngle : undefined,
          ideaPrompt: sourceMode === "idea" || sourceMode === "image" ? ideaPrompt.trim() || undefined : undefined,
        },
        token,
        { signal: controller.signal },
      );
      const reconciledData = reconcileGenerateResponseMediaTruth(data);
      setResult(reconciledData);
      setClipRecoveryStates({});
      setPaywallMessage(null);
      const allStrategyOnly =
        reconciledData.clips.length > 0 && reconciledData.clips.every((clip) => !clipHasRenderedMedia(clip));
      const fallbackReason = (reconciledData.processing_summary as { fallback_reason?: string } | undefined)?.fallback_reason;

      if (allStrategyOnly && fallbackReason) {
        setError(`Could not process this source: ${fallbackReason}. Try a different public link, upload, or prompt.`);
        return;
      }
      setError(null);
      const leadClip = reconciledData.clips?.find((clip) => clipHasRenderedMedia(clip)) || reconciledData.clips?.[0];
      void fireGodTrigger("generation_complete", {
        route: window.location.pathname,
        lastClipScore: leadClip?.score,
        lastClipHook: leadClip?.hook,
        creditsRemaining: reconciledData.processing_summary?.credits_remaining,
        platform: reconciledData.processing_summary?.target_platform || platform,
      });
      if (token) {
        await refreshAccount(token);
      }
    } catch (submitError) {
      if (submitError instanceof DOMException && submitError.name === "AbortError") {
        setError("Generation cancelled. Try another URL.");
        return;
      }
      setResult(null);
      if (submitError instanceof ApiError && submitError.status === 402) {
        setError(null);
        setPaywallMessage(user ? submitError.message : "guest_limit");
      } else {
        const raw = submitError instanceof Error ? submitError.message : "Unable to generate clips.";
        const lower = raw.toLowerCase();
        const isBot = lower.includes("sign in to confirm") || lower.includes("not a bot") || lower.includes("bot") || lower.includes("yt-dlp") || lower.includes("cookie") || lower.includes("blocked");
        const isLive = lower.includes("live") || lower.includes("premiere");
        const isTimeout = lower.includes("timeout") || lower.includes("too long") || lower.includes("504");
        const isUnavailable = lower.includes("unavailable") || lower.includes("private") || lower.includes("removed");

        if (isBot) setError("This platform blocked server access. Upload the video/audio file directly, try another public source, or use prompt mode to generate the package.");
        else if (isLive) setError("Live streams can't be clipped yet. Upload the stream later as a file, or use prompt mode.");
        else if (isTimeout) setError("Video took too long. Try a shorter source under 10 minutes, or upload a pre-trimmed file.");
        else if (isUnavailable) setError("This video is private, removed, or region-locked. Upload your own file, try another URL, or use prompt mode.");
        else setError(raw === "Unable to generate clips." ? "Could not process that source. Try a different file, URL, or use prompt mode to generate content." : raw);
      }
    } finally {
      if (generationControllerRef.current === controller) {
        generationControllerRef.current = null;
      }
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

  function handleCancelGeneration() {
    generationControllerRef.current?.abort();
    generationControllerRef.current = null;
    setIsLoading(false);
    setLoadingStageIndex(0);
    emitLWACharacterEvent({ state: "breathe", trigger: "generation_cancelled" });
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
      const renderedDelta = Number(clipHasRenderedMedia(right)) - Number(clipHasRenderedMedia(left));
      if (renderedDelta !== 0) {
        return renderedDelta;
      }

      if (Boolean(left.is_best_clip) !== Boolean(right.is_best_clip)) {
        return Number(Boolean(right.is_best_clip)) - Number(Boolean(left.is_best_clip));
      }

      const leftOrder = left.post_rank || left.best_post_order || left.rank || Number.MAX_SAFE_INTEGER;
      const rightOrder = right.post_rank || right.best_post_order || right.rank || Number.MAX_SAFE_INTEGER;

      if (leftOrder !== rightOrder) {
        return leftOrder - rightOrder;
      }

      const scoreDelta = getClipScore(right) - getClipScore(left);
      if (scoreDelta !== 0) {
        return scoreDelta;
      }

      return String(left.id).localeCompare(String(right.id));
    });
  }, [displayedClips]);

  const isHome = initialSection === "home";
  const hasSourceSelected =
    sourceMode === "idea"
      ? Boolean(ideaPrompt.trim())
      : sourceMode === "image"
        ? Boolean(selectedUploadId)
        : Boolean(videoUrl.trim() || selectedUploadId);
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
  const showPageIntro = Boolean(pageIntro) && !(isGuest && initialSection === "generate");
  const featureProof = ["Best clip first", "Hooks that hit", "Export-ready"];
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
    () => orderedClips.filter((clip) => clipHasRenderedMedia(clip)).length,
    [orderedClips],
  );
  const leadClip =
    orderedClips.find((clip) => clip.is_best_clip && clipHasRenderedMedia(clip)) ||
    orderedClips.find((clip) => clipHasRenderedMedia(clip)) ||
    orderedClips.find((clip) => clip.is_best_clip) ||
    orderedClips[0] ||
    null;
  const leadClipId = leadClip ? resolveClipQueueId(leadClip) : null;
  const renderedClips = useMemo(() => orderedClips.filter((clip) => clipHasRenderedMedia(clip)), [orderedClips]);
  const strategyOnlyClips = useMemo(() => orderedClips.filter((clip) => !clipHasRenderedMedia(clip)), [orderedClips]);
  const renderedLaneClips = useMemo(
    () => renderedClips.filter((clip) => resolveClipQueueId(clip) !== leadClipId),
    [leadClipId, renderedClips],
  );
  const strategyLaneClips = useMemo(
    () => strategyOnlyClips.filter((clip) => resolveClipQueueId(clip) !== leadClipId),
    [leadClipId, strategyOnlyClips],
  );
  const leadClipIsRendered = leadClip ? clipHasRenderedMedia(leadClip) : false;
  const effectiveTargetPlatform = activeResult?.processing_summary?.target_platform || (useManualPlatform ? platform : "Auto");
  const recommendedPlatform = activeResult?.processing_summary?.recommended_platform || activeResult?.processing_summary?.target_platform || null;
  const platformDecision = activeResult?.processing_summary?.platform_decision || (useManualPlatform ? "manual" : "auto");
  const platformRecommendationReason = activeResult?.processing_summary?.platform_recommendation_reason || null;
  const renderedClipCount = renderedClips.length;
  const strategyOnlyClipCount = strategyOnlyClips.length;
  const shotPlanReadyCount = orderedClips.filter((clip) => clipHasShotPlan(clip)).length;
  const requestedClipCount = activeResult?.processing_summary?.requested_clip_count ?? null;
  const generatedClipCount = activeResult?.processing_summary?.generated_clip_count ?? orderedClips.length;
  const bulkExportReady = Boolean(activeResult?.processing_summary?.bulk_export_ready);
  const manifestUrl = activeResult?.processing_summary?.manifest_url || null;
  const latestManifestUrl = latestBundleExport?.manifest_url || null;
  const visibleManifestUrl = latestManifestUrl || manifestUrl;
  const exportArtifactTypes = latestBundleExport?.artifact_types?.length
    ? latestBundleExport.artifact_types
    : leadClip?.export_bundle?.artifact_types || [];
  const exportArtifactCount = exportArtifactTypes.length;
  const exportBundleFormat = (latestBundleExport?.bundle_format || leadClip?.export_bundle?.bundle_format || null)?.toUpperCase() || null;
  const exportBundleSize = formatBundleBytes(latestBundleExport?.size_bytes || null);
  const campaignName = activeResult?.processing_summary?.campaign_name || null;
  const hasStrategyOnlyWithoutPreview = strategyOnlyClips.some(
    (clip) => Boolean(clip.is_strategy_only) && !clip.preview_url && !clipHasRenderedMedia(clip),
  );
  const recoveryActive = useMemo(
    () => Object.values(clipRecoveryStates).some((recovery) => recovery.status === "queued" || recovery.status === "processing"),
    [clipRecoveryStates],
  );
  const exportReadyCount = useMemo(() => orderedClips.filter((clip) => clip.download_url).length, [orderedClips]);
  const leadPreviewUrl = activeResult?.preview_asset_url || getClipPreviewUrl(leadClip);
  const leadExportUrl = activeResult?.download_asset_url || leadClip?.download_url || null;
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
  const paywallCard = paywallMessage ? (
    <div className="rounded-[18px] border border-[var(--gold-border)] bg-[var(--gold-dim)] px-5 py-4">
      <p className="text-sm font-semibold text-[var(--gold)]">
        Out of credits.
      </p>
      <p className="mt-1 text-sm text-white/55">
        {user
          ? "Choose a checkout path, request a demo, or wait for reset."
          : "Sign in free to keep generating and save your clips."}
      </p>
      <div className="mt-3">
        {!user ? (
          <button
            type="button"
            onClick={() => {
              setAuthMode("login");
              setAuthOpen(true);
            }}
            className="rounded-full bg-[var(--gold)] px-5 py-2.5 text-sm font-semibold text-black hover:opacity-90"
          >
            Sign in free
          </button>
        ) : (
          <MoneyCtaPanel variant="compact" source="clip_studio_quota" title="Choose how to keep generating" />
        )}
      </div>
    </div>
  ) : null;
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
      link.download = bundle.file_name || "lwa-bundle.zip";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setLatestBundleExport(bundle);
      setBundleExportState("ready");
      setBundleExportMessage(
        bundle.manifest_url
          ? "Bundle downloaded with manifest, caption text, and subtitle files."
          : "Bundle downloaded.",
      );
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

  async function handleCopyPackages(action: "lead" | "rendered" | "strategy" | "all") {
    if (!activeResult?.clips?.length) {
      return;
    }

    const fallbackPlatform = effectiveTargetPlatform === "Auto" ? undefined : effectiveTargetPlatform;
    const clips =
      action === "lead"
        ? leadClip
          ? [leadClip]
          : []
        : action === "rendered"
          ? renderedClips
          : action === "strategy"
            ? strategyOnlyClips
            : orderedClips;

    const text =
      action === "lead" && leadClip
        ? buildClipPackageText(leadClip, fallbackPlatform)
        : buildAllPackagesText(clips, fallbackPlatform);

    if (!text.trim()) {
      return;
    }

    try {
      await navigator.clipboard?.writeText(text);
      setCopiedPackageAction(action);
      window.setTimeout(() => {
        setCopiedPackageAction((current) => (current === action ? null : current));
      }, 1600);
    } catch {
      setCopiedPackageAction(null);
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

  async function pollGuestRenderStatus(clipId: string, requestId: string, attempt = 0) {
    try {
      const status = await loadClipRenderStatus(clipId, requestId, token);
      if (isRenderedClip(status)) {
        replaceClipInResult(status);
        setClipRecoveryStates((current) => ({
          ...current,
          [clipId]: {
            status: "recovered",
            message: "Preview is ready.",
            error: null,
          },
        }));
        return;
      }

      if (status.render_status === "failed") {
        setClipRecoveryStates((current) => ({
          ...current,
          [clipId]: {
            status: "failed",
            message: status.render_error || "Unable to render preview.",
            error: status.render_error || "Unable to render preview.",
          },
        }));
        return;
      }

      if (attempt >= 11) {
        setClipRecoveryStates((current) => ({
          ...current,
          [clipId]: {
            status: "failed",
            message: "Preview is still pending. Try again in a moment.",
            error: "Preview is still pending.",
          },
        }));
        return;
      }

      setClipRecoveryStates((current) => ({
        ...current,
        [clipId]: {
          status: "processing",
          message: "Rendering preview...",
          error: null,
        },
      }));

      window.setTimeout(() => {
        void pollGuestRenderStatus(clipId, requestId, attempt + 1);
      }, 1800);
    } catch (recoveryError) {
      setClipRecoveryStates((current) => ({
        ...current,
        [clipId]: {
          status: "failed",
          message: recoveryError instanceof Error ? recoveryError.message : "Unable to load preview status.",
          error: recoveryError instanceof Error ? recoveryError.message : "Unable to load preview status.",
        },
      }));
    }
  }

  async function handleRecoverClip(clip: ClipResult) {
    const clipId = clip.record_id || clip.clip_id || clip.id;
    const requestId = clip.request_id || activeResult?.request_id || null;

    if (!token) {
      if (!requestId) {
        setClipRecoveryStates((current) => ({
          ...current,
          [clipId]: {
            status: "failed",
            message: "Missing request context for preview retry.",
            error: "Missing request context for preview retry.",
          },
        }));
        return;
      }

      setClipRecoveryStates((current) => ({
        ...current,
        [clipId]: {
          status: "queued",
          message: "Preview retry queued.",
        },
      }));
      try {
        const status = await retryClipRender(clipId, requestId, token);
        if (isRenderedClip(status)) {
          replaceClipInResult(status);
          setClipRecoveryStates((current) => ({
            ...current,
            [clipId]: {
              status: "recovered",
              message: "Preview is ready.",
              error: null,
            },
          }));
          return;
        }
        if (status.render_status === "failed") {
          setClipRecoveryStates((current) => ({
            ...current,
            [clipId]: {
              status: "failed",
              message: status.render_error || "Unable to render preview.",
              error: status.render_error || "Unable to render preview.",
            },
          }));
          return;
        }
        setClipRecoveryStates((current) => ({
          ...current,
          [clipId]: {
            status: "processing",
            message: "Rendering preview...",
            error: null,
          },
        }));
        void pollGuestRenderStatus(clipId, requestId);
      } catch (recoveryError) {
        setClipRecoveryStates((current) => ({
          ...current,
          [clipId]: {
            status: "failed",
            message: recoveryError instanceof Error ? recoveryError.message : "Unable to start preview retry.",
            error: recoveryError instanceof Error ? recoveryError.message : "Unable to start preview retry.",
          },
        }));
      }
      return;
    }

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
          type="text"
          inputMode="url"
          autoCapitalize="off"
          autoCorrect="off"
          spellCheck={false}
          data-lwa-source-input="true"
          value={videoUrl}
          onChange={(event) => setVideoUrl(event.target.value)}
          onFocus={() => setInputFocused(true)}
          onBlur={() => setInputFocused(false)}
          placeholder="Drop a video, audio file, stream link, Twitch VOD, music idea, campaign, or prompt..."
          className="source-command-input input-surface input-command w-full rounded-[28px] px-5 py-5 text-base"
        />
      </label>
    );
  }

  const advancedGeneratorControls = !isGuest ? (
    <details className="operator-tile rounded-[24px] p-4">
      <summary className="cursor-pointer list-none text-sm font-medium text-ink">
        Advanced controls
      </summary>
      <div className="mt-4 space-y-4">
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

        {renderSourceModeControls()}

        <div className="space-y-3">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm font-medium text-ink">Destination</p>
              <p className="mt-2 text-sm leading-7 text-ink/72">
                {useManualPlatform
                  ? `Manual override is on for ${platform}.`
                  : "Auto stays on unless you already know the feed."}
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

          {useManualPlatform ? (
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
          ) : null}
        </div>

        {generationMode === "pro" ? (
          <label className="secondary-button inline-flex items-center gap-3 rounded-full px-4 py-2.5 text-sm font-medium">
            <input
              type="checkbox"
              checked={improveResults}
              onChange={(event) => setImproveResults(event.target.checked)}
              className="h-4 w-4 accent-[var(--gold)]"
            />
            Improve results
          </label>
        ) : null}
      </div>
    </details>
  ) : null;

  const generatorSupportRow = (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-sm font-medium text-ink">Source</p>
        <p className="mt-1 text-sm text-ink/60">{activeSourceLabel}</p>
      </div>
      <label className="secondary-button inline-flex cursor-pointer items-center justify-center rounded-full px-4 py-2 text-sm font-medium">
        Upload file
        <input
          type="file"
          accept=".mp4,.mov,.m4v,.webm,.mp3,.wav,.m4a,.aac,.ogg,.oga,.flac,.jpg,.jpeg,.png,.webp,.heic,.heif,video/*,audio/*,image/*"
          className="hidden"
          onChange={onUploadSelected}
        />
      </label>
    </div>
  );

  const homeGeneratorSection = (
    <section
      className="generator-command-card source-command-card rounded-[38px] p-6 sm:p-8"
      onMouseEnter={() => setGeneratorHovered(true)}
      onMouseLeave={() => setGeneratorHovered(false)}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="section-kicker">Source command</p>
          <h2 className="mt-3 text-2xl font-semibold text-ink sm:text-[2rem]">Drop any source. Build the creator-ready package.</h2>
          <p className="mt-3 max-w-xl text-sm leading-7 text-subtext/82">
            {generationMode === "quick"
              ? "Rendered clips first. Strategy ideas stay separate."
              : "Best clip first, with hooks, captions, timestamps, score, and post order."}
          </p>
        </div>
        <StatPill tone="accent">{useManualPlatform ? platform : "Auto recommend"}</StatPill>
      </div>

      <form onSubmit={onSubmit} className="mt-7 space-y-5">
        {renderSourceInput()}
        {generatorSupportRow}
        {advancedGeneratorControls}

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          {!isGuest ? (
          <p className="text-sm text-ink/60">
            {isLoading ? `${loadingStages[loadingStageIndex]}. ${GENERATOR_COPY.loading}` : idleRunSummary}
          </p>
          ) : null}
          <button
            type="submit"
            onClick={(event) => {
              if (sourceMode === "video" && !videoUrl.trim() && !selectedUploadId) {
                event.preventDefault();
                setError("Drop a video, audio file, stream link, Twitch VOD, campaign, or prompt to get started.");
              }
            }}
            disabled={isLoading}
            className={
              isGuest
                ? "primary-button w-full rounded-full px-6 py-4 text-base font-semibold disabled:opacity-50"
                : "primary-button inline-flex w-full items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60 md:min-w-[220px] md:w-auto"
            }
          >
            {isGuest ? (isLoading ? "Finding clips..." : "Generate clip pack") : isLoading ? GENERATOR_COPY.submitting : "Generate clip pack"}
          </button>
        </div>

        {isLoading ? <LoadingSequence stages={loadingStages} activeIndex={loadingStageIndex} onCancel={handleCancelGeneration} /> : null}

        {error ? <InlineAlert tone="error">{error}</InlineAlert> : null}
        {paywallCard}
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
                  ? "Rendered clips first. Strategy ideas stay separate."
                  : "Best clip first, with hooks, captions, timestamps, score, and post order."}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              {!isGuest ? (
                <>
                  <StatPill tone="accent">{planSurface.name}</StatPill>
                  <StatPill tone="signal">{activeResult ? "Live output" : "Premium review"}</StatPill>
                </>
              ) : null}
            </div>
          </div>

          <form onSubmit={onSubmit} className="mt-8 space-y-6">
            {renderSourceInput()}
            {generatorSupportRow}
            {advancedGeneratorControls}

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
              <button
                type="submit"
                onClick={(event) => {
                  if (sourceMode === "video" && !videoUrl.trim() && !selectedUploadId) {
                    event.preventDefault();
                    setError("Drop a video, audio file, stream link, Twitch VOD, campaign, or prompt to get started.");
                  }
                }}
                disabled={isLoading}
                className={
                  isGuest
                  ? "primary-button w-full rounded-full px-6 py-4 text-base font-semibold disabled:opacity-50"
                    : "primary-button inline-flex w-full items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60 md:min-w-[240px] md:w-auto"
                }
              >
                {isGuest ? (isLoading ? "Finding clips..." : "Generate clip pack") : isLoading ? GENERATOR_COPY.submitting : "Generate clip pack"}
              </button>
            </div>

            {isLoading ? <LoadingSequence stages={loadingStages} activeIndex={loadingStageIndex} onCancel={handleCancelGeneration} /> : null}

            {error ? <InlineAlert tone="error">{error}</InlineAlert> : null}

            {paywallCard}
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
              Video keeps the clipping flow. Image moves through generation. Upload when you want full source control.
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
        </aside>
        ) : null}
      </div>
    </section>
  );

  const resultsSection = activeResult ? (
    <section id="lwa-results-section" className={["result-screen space-y-6", motionLocked ? "result-screen--locked" : ""].join(" ")}>
      <div className="hero-card rounded-[32px] p-6 sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="section-kicker">{RESULTS_COPY.kicker}</p>
            <h3 className="page-title mt-3 text-3xl font-semibold text-ink sm:text-[2.4rem]">Best clip first. Then move the stack.</h3>
            <p className="mt-4 text-sm leading-7 text-subtext">
              LWA separates playable outputs from strategy-only ideas so you know what to post now, what to rerun, and why the lead clip is on top.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <StatPill tone="accent">{effectiveTargetPlatform}</StatPill>
            <StatPill tone="signal">{renderedClipCount} rendered</StatPill>
            {strategyOnlyClipCount ? <StatPill tone="neutral">{strategyOnlyClipCount} strategy only</StatPill> : null}
            {shotPlanReadyCount ? <StatPill tone="neutral">{shotPlanReadyCount} shot plans</StatPill> : null}
          </div>
        </div>

        <div className="mt-5 flex flex-col gap-3 border-t border-white/8 pt-5 sm:flex-row sm:flex-wrap sm:items-center">
          {recommendedPlatform ? <StatPill tone="accent">Recommended: {recommendedPlatform}</StatPill> : null}
          {platformDecision === "manual" ? <StatPill tone="neutral">Manual destination</StatPill> : <StatPill tone="signal">Auto recommendation</StatPill>}
          {leadClipIsRendered ? <StatPill tone="signal">Lead clip is playable</StatPill> : <StatPill tone="neutral">Lead clip is strategy only</StatPill>}
          {activeResult.processing_summary?.recommended_next_step ? (
            <span className="text-sm text-ink/62">{activeResult.processing_summary.recommended_next_step}</span>
          ) : null}
        </div>
      </div>

      {isGuest && hasStrategyOnlyWithoutPreview ? (
        <InlineAlert tone="violet" title="Strategy-only package ready">
          To get playable clips, upload your source file directly or try a different public source. Strategy shot plans are ready for manual production.
        </InlineAlert>
      ) : !renderedClipCount ? (
        <InlineAlert tone="violet" title="Strategy-only package ready">
          Strategy package ready. To get playable clips, upload the source file directly or try a different public source.
        </InlineAlert>
      ) : !previewReadyCount ? (
        <InlineAlert tone="violet" title="Rendered lane is partial">
          Some clips came back without a playable preview. Export the ready cuts first, then use the strategy lane to decide what is worth recovering.
        </InlineAlert>
      ) : null}

      {leadClip ? (
        <div className="space-y-3">
          <p className="section-kicker">Lead clip</p>
          <HeroClip
            clip={leadClip}
            compact={isGuest}
            feedbackVote={!isGuest ? feedbackByClipId[leadClip.record_id || leadClip.clip_id || leadClip.id] || null : null}
            onVote={!isGuest ? handleFeedbackVote : undefined}
            queued={isQueued(leadClip)}
            onToggleQueue={handleToggleQueue}
            recoveryState={clipRecoveryStates[resolveClipQueueId(leadClip)] || null}
            onRecover={handleRecoverClip}
          />
        </div>
      ) : null}

      <div className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="section-kicker">Rendered</p>
            <h4 className="mt-2 text-2xl font-semibold text-ink">Playable clips ready now</h4>
            <p className="mt-2 max-w-2xl text-sm leading-7 text-ink/60">
              Use this lane when you need something you can preview, export, and move immediately.
            </p>
          </div>
          <StatPill tone="signal">{renderedClipCount} rendered</StatPill>
        </div>

        {renderedLaneClips.length ? (
          <div className={["grid gap-5 md:grid-cols-2", isGuest ? "" : "xl:grid-cols-3"].join(" ")}>
            {renderedLaneClips.map((clip) => (
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
        ) : (
          <div className="glass-panel rounded-[28px] p-5 text-sm leading-7 text-ink/60">
            {leadClipIsRendered
              ? "The lead clip is the only rendered asset in this pack right now."
              : "No additional rendered clips are ready yet."}
          </div>
        )}
      </div>

      <div className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="section-kicker">Strategy only</p>
            <h4 className="mt-2 text-2xl font-semibold text-ink">Hooks and packaging worth testing</h4>
            <p className="mt-2 max-w-2xl text-sm leading-7 text-ink/60">
              These cuts are useful ideas, not fake previews. Review the hook variants, why it matters, and recovery path before rerendering.
            </p>
          </div>
          <StatPill tone="neutral">{strategyOnlyClipCount} strategy only</StatPill>
        </div>

        {strategyLaneClips.length ? (
          <div className={["grid gap-5 md:grid-cols-2", isGuest ? "" : "xl:grid-cols-3"].join(" ")}>
            {strategyLaneClips.map((clip) => (
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
        ) : (
          <div className="glass-panel rounded-[28px] p-5 text-sm leading-7 text-ink/60">
            {!leadClipIsRendered && leadClip
              ? "The lead clip is currently the only strategy-only idea in this pack."
              : "No extra strategy-only clips were returned in this run."}
          </div>
        )}
      </div>

      <div className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="section-kicker">Packaging + export</p>
            <h4 className="mt-2 text-2xl font-semibold text-ink">What to post next and how to package it</h4>
            <p className="mt-2 max-w-2xl text-sm leading-7 text-ink/60">
              Use the lead hook, caption, thumbnail text, CTA, and post order together. Export rendered media first, then queue or recover the rest.
            </p>
            {campaignName ? (
              <p className="mt-3 text-sm font-medium text-ink/72">Campaign: {campaignName}</p>
            ) : null}
            {bulkExportReady ? (
              <p className="mt-2 text-sm text-[var(--gold)]">
                Bulk export ready{manifestUrl ? " with batch manifest." : "."}
              </p>
            ) : null}
            {exportArtifactTypes.length ? (
              <div className="mt-3 flex flex-wrap gap-2">
                {exportArtifactTypes.map((artifact) => (
                  <span
                    key={artifact}
                    className="rounded-full border border-[var(--divider)] bg-[var(--surface-soft)] px-3 py-1 text-[11px] font-medium text-ink/72"
                  >
                    {bundleArtifactLabel(artifact)}
                  </span>
                ))}
              </div>
            ) : null}
          </div>
          <div className="flex flex-wrap gap-2">
            {leadClip ? (
              <button
                type="button"
                onClick={() => void handleCopyPackages("lead")}
                className="primary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-semibold sm:w-auto"
              >
                {copiedPackageAction === "lead" ? "Lead package copied" : "Copy lead package"}
              </button>
            ) : null}
            {renderedClips.length ? (
              <button
                type="button"
                onClick={() => void handleCopyPackages("rendered")}
                className="secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium sm:w-auto"
              >
                {copiedPackageAction === "rendered" ? "Rendered copied" : "Copy rendered packages"}
              </button>
            ) : null}
            {strategyOnlyClips.length ? (
              <button
                type="button"
                onClick={() => void handleCopyPackages("strategy")}
                className="secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium sm:w-auto"
              >
                {copiedPackageAction === "strategy" ? "Strategy copied" : "Copy strategy packages"}
              </button>
            ) : null}
            {orderedClips.length > 1 ? (
              <button
                type="button"
                onClick={() => void handleCopyPackages("all")}
                className="secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium sm:w-auto"
              >
                {copiedPackageAction === "all" ? "All packages copied" : "Copy all packages"}
              </button>
            ) : null}
            {leadPreviewReady ? (
              <a
                href={leadPreviewUrl || undefined}
                target="_blank"
                rel="noreferrer"
                className="secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium sm:w-auto"
              >
                Open lead preview
              </a>
            ) : null}
            {leadExportReady ? (
              <a
                href={leadExportUrl || undefined}
                download
                className="primary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-semibold sm:w-auto"
              >
                Export lead clip
              </a>
            ) : null}
            <button
              type="button"
              onClick={() => void handleExportBundle()}
              disabled={bundleExportState === "exporting" || !activeResult?.clips?.length}
              className="secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
            >
              {bundleExportState === "exporting" ? "Building bundle..." : "Export full bundle"}
            </button>
            {visibleManifestUrl ? (
              <a
                href={visibleManifestUrl}
                target="_blank"
                rel="noreferrer"
                className="secondary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-medium sm:w-auto"
              >
                {latestManifestUrl ? "Open bundle manifest" : "Open batch manifest"}
              </a>
            ) : null}
          </div>
        </div>

        <div className={["grid gap-6", !isGuest ? "xl:grid-cols-[minmax(0,0.58fr),minmax(320px,0.42fr)]" : ""].join(" ")}>
          <div className="space-y-6">
            {leadClip ? (
              <div className="glass-panel rounded-[28px] p-5">
                <p className="section-kicker">Lead package</p>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  <MetricTile
                    label="Hook"
                    value={leadClip.hook || leadClip.title}
                    detail={leadClip.why_this_matters || leadClip.reason || "This is the best opening move in the current stack."}
                  />
                  <MetricTile
                    label="Thumbnail"
                    value={leadClip.thumbnail_text || leadClip.title}
                    detail="Use this line on the cover or opening frame."
                  />
                  <MetricTile
                    label="CTA"
                    value={leadClip.cta_suggestion || "Ask viewers what they want next."}
                    detail="Keep the action simple and immediate."
                  />
                  <MetricTile
                    label="Post order"
                    value={`#${leadClip.post_rank || leadClip.best_post_order || leadClip.rank || 1}`}
                    detail="Lead with this before moving into the rest of the stack."
                  />
                </div>
                <div className="mt-4 rounded-[22px] border border-[var(--divider)] bg-[var(--surface-soft)] p-4">
                  <p className="text-xs uppercase tracking-[0.22em] text-muted">Caption</p>
                  <p className="mt-3 text-sm leading-7 text-ink/76">{leadClip.caption}</p>
                </div>
              </div>
            ) : null}

            {orderedClips.length ? <ReviewOrderPanel clips={orderedClips} /> : null}
          </div>

          {!isGuest ? (
            <div className="space-y-5">
              <ReadyQueuePanel items={readyQueue} onMove={handleMoveQueue} onRemove={handleRemoveQueue} onClear={handleClearQueue} />

              <div className="glass-panel rounded-[28px] p-5">
                <p className="section-kicker">Export state</p>
                <div className="mt-4 grid gap-3">
                  <MetricTile
                    label="Clips"
                    value={String(generatedClipCount)}
                    detail={
                      requestedClipCount && requestedClipCount !== generatedClipCount
                        ? `Requested ${requestedClipCount} for this run.`
                        : "Total clips returned in this pack."
                    }
                  />
                  <MetricTile
                    label="Rendered"
                    value={String(renderedClipCount)}
                    detail={renderedClipCount ? "Playable clips you can move right now." : "No playable clips were returned."}
                  />
                  <MetricTile
                    label="Strategy"
                    value={String(strategyOnlyClipCount)}
                    detail={strategyOnlyClipCount ? "Ideas that need review or recovery." : "Everything visible is rendered."}
                  />
                  <MetricTile
                    label="Downloads"
                    value={String(exportReadyCount)}
                    detail={exportReadyCount ? "Direct clip files are ready now." : "Use bundle export or recover clips first."}
                  />
                  <MetricTile
                    label="Shot plans"
                    value={String(shotPlanReadyCount)}
                    detail="Director Brain guidance returned with this pack."
                  />
                  <MetricTile
                    label="Manifest"
                    value={visibleManifestUrl ? "Ready" : "Pending"}
                    detail={latestManifestUrl ? "The latest bundle manifest is available now." : manifestUrl ? "Batch manifest is ready for export planning." : "Manifest appears after packaging metadata is prepared."}
                  />
                  <MetricTile
                    label="Bundle"
                    value={exportBundleFormat || "Pending"}
                    detail={
                      latestBundleExport
                        ? `Latest bundle includes ${exportArtifactCount || 0} artifact types${exportBundleSize ? ` and weighs ${exportBundleSize}` : ""}.`
                        : "Build the full bundle to package captions, subtitles, and metadata together."
                    }
                  />
                </div>
                {bundleExportMessage ? (
                  <p className={["mt-4 text-sm", bundleExportState === "failed" ? "text-red-200" : "text-[var(--gold)]"].join(" ")}>
                    {bundleExportMessage}
                  </p>
                ) : null}
              </div>
            </div>
          ) : null}
        </div>
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
    <section className={["app-shell-grid min-h-screen", motionLocked ? "results-motion-locked" : ""].join(" ")}>
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
                {!isGuest ? (
                  <>
                    <WorkspaceRailCard
                      label="Studio pulse"
                      title="Generate first. Move fast."
                      description="Move from generation to queue, assignments, and manual payout readiness."
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
                ) : null}
              </div>
            </aside>

            <div className="space-y-6">

              {showPageIntro && pageIntro ? (
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
                        "Campaign-level payout readiness",
                      ]}
                    />
                  ) : null}

                  {showWallet && user && walletUnlocked ? (
                    <WalletPanel wallet={wallet} ledgerEntries={walletLedger} onRequestPayout={handlePayoutRequest} />
                  ) : showWallet && user ? (
                    <FeatureGatePanel
                      label="Wallet"
                      title="Wallet views unlock on paid plans"
                      description="Upgrade to review earnings readiness, payout review requests, and ledger movement from the same workspace."
                      requiredPlan="Pro"
                      bullets={[
                        "Ledger balance tracking",
                        "Payout review request history",
                        "Future earnings readiness surfaces",
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
    </section>
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

function LoadingSequence({
  stages,
  activeIndex,
  onCancel,
}: {
  stages: string[];
  activeIndex: number;
  onCancel?: () => void;
}) {
  const safeLength = Math.max(stages.length, 1);
  const progress = Math.min(((activeIndex + 1) / safeLength) * 100, 100);
  const etaSeconds = Math.max((safeLength - activeIndex - 1) * 8, 6);
  const stageDetails: Record<string, string> = {
    "Source ingest": "Reading source and validating access.",
    "Moment scan": "Scanning replay-worthy moments.",
    "Clip ranking": "Ranking hooks and post order.",
    Packaging: "Building captions, thumbnail lines, and CTA package.",
    "Render/export": "Preparing vertical assets when available.",
    Delivery: "Returning the clip pack to the studio.",
  };

  return (
    <div className="panel-subtle rounded-[24px] px-5 py-6">
      <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="relative flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-white/[0.04]">
            <div className="absolute inset-0 animate-spin rounded-full border-2 border-white/10 border-t-accent" />
            <img src="/brand/lwa-mark.svg" alt="LWA" className="relative h-6 w-6 opacity-90" />
          </div>
          <div>
            <p className="text-lg font-medium text-ink">LWA is building the clip pack</p>
            <p className="text-sm text-ink/60">{stageDetails[stages[activeIndex]] || stages[activeIndex] || "Preparing outputs."}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <p className="text-sm text-ink/60">ETA ~{etaSeconds}s</p>
          {onCancel ? (
            <button
              type="button"
              onClick={onCancel}
              className="secondary-button inline-flex min-h-[44px] items-center justify-center rounded-full px-4 py-2.5 text-sm font-medium"
            >
              Cancel
            </button>
          ) : null}
        </div>
      </div>

      <div className="mb-5 h-2 overflow-hidden rounded-full bg-white/[0.08]">
        <div
          className="h-full rounded-full bg-[linear-gradient(90deg,var(--accent-soft),var(--gold))] transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
        {stages.map((stage, index) => (
          <div
            key={stage}
            className={[
              "loading-stage rounded-[20px] px-4 py-4",
              index < activeIndex ? "border-emerald-300/20 bg-emerald-300/10" : "",
              index === activeIndex ? "loading-stage-active" : "",
            ].join(" ")}
          >
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Step {index + 1}</p>
            <p className="mt-2 text-sm font-medium text-ink">{stage}</p>
            <p className="mt-2 text-xs leading-5 text-ink/48">{stageDetails[stage] || "Preparing outputs."}</p>
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
      ? "border-[var(--danger)] bg-[var(--surface-danger)] text-[var(--danger)]"
      : "border-[var(--gold-border)] bg-[var(--gold-dim)] text-ink";

  return (
    <div className={["rounded-[24px] border px-5 py-4 text-sm", toneClass].join(" ")}>
      {title ? <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">{title}</p> : null}
      {children}
    </div>
  );
}
