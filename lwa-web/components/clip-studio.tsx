"use client";

import Link from "next/link";
import { ChangeEvent, FormEvent, PointerEvent as ReactPointerEvent, ReactNode, useEffect, useMemo, useRef, useState } from "react";
import { AIBackground } from "./AIBackground";
import { AccountWorkspace } from "./account-workspace";
import { AuthPanel } from "./auth-panel";
import { BatchPanel } from "./batch-panel";
import { CampaignPanel } from "./campaign-panel";
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
import { GENERATOR_COPY, HERO_COPY, RESULTS_COPY, rewriteSurfaceLabel } from "../lib/brand-voice";
import { getPlanSurface } from "../lib/plans";

const platforms: PlatformOption[] = ["TikTok", "Instagram Reels", "YouTube Shorts"];

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
  const [generationMode, setGenerationMode] = useState<"quick" | "pro">("quick");
  const [readyQueue, setReadyQueue] = useState<ReadyQueueItem[]>([]);
  const [paywallMessage, setPaywallMessage] = useState<string | null>(null);
  const [loadingStageIndex, setLoadingStageIndex] = useState(0);
  const [reduceMotion, setReduceMotion] = useState(false);
  const homeStageRef = useRef<HTMLElement | null>(null);

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
      setLoadingStageIndex((current) => (current + 1) % 3);
    }, 1400);

    return () => window.clearInterval(interval);
  }, [isLoading]);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const sync = () => setReduceMotion(media.matches);
    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, []);

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
  const featuredClip = orderedClips[0] ?? null;
  const remainingClips = orderedClips.slice(1);
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
  const featureProof = ["Best clip first", "Hooks + captions", "Queue-ready"];
  const loadingStages = ["Analyzing video", "Finding viral moments", "Generating clips"];
  const deliveryMoments = [
    {
      label: "Paste once",
      detail: "Start with one source and one target platform.",
    },
    {
      label: "Review first",
      detail: "See ranked clips, hooks, and captions before you export.",
    },
    {
      label: "Move fast",
      detail: "Queue the winners and keep the rest for later.",
    },
  ] as const;
  const idleRunSummary =
    generationMode === "quick"
      ? "Paste a public link, get ranked clips back, then review the best option first."
      : "Turn on local learning when you want the next pack to lean toward what you keep.";
  const homeDiscoverySections = [
    {
      id: "why-lwa",
      kicker: "Why LWA",
      title: "Built for source-to-post speed, not random clip dumps.",
      body: "LWA is strongest when you need the best cut first, cleaner packaging, and a workflow that still holds together after generation.",
      bullets: [
        "Lead clip authority with post order and packaging attached",
        "Hooks, captions, timestamps, and previews in one review layer",
        "Queue, archive, campaigns, and wallet surfaces already in the product",
      ],
      links: [
        { href: "/generate", label: "Forge clips" },
        { href: "/dashboard", label: "Open Control Room" },
      ],
    },
    {
      id: "how-it-works",
      kicker: "How it works",
      title: "One source in. Ranked stack out.",
      body: "Drop a public link or upload a file. LWA processes the source, ranks the strongest cuts, and returns copy and output signals that help you move faster.",
      bullets: [
        "Analyze source media and candidate moments",
        "Rank clips, packaging, and post order",
        "Review, queue, export, and reopen from history",
      ],
    },
    {
      id: "who-its-for",
      kicker: "Who it’s for",
      title: "Creators, clippers, agencies, and operator-heavy teams.",
      body: "This is for people already making long-form content and trying to turn one source into more chances to win without stacking more editing overhead.",
      bullets: [
        "Podcasters, streamers, interview shows, and creator brands",
        "Clippers and agencies running throughput instead of one-off edits",
        "Teams that care about ranking, packaging, and workflow trust",
      ],
    },
    {
      id: "compare",
      kicker: "Compare",
      title: "Use LWA when you want ranking and workflow, not just a clip pull.",
      body: "The right comparison is not blog fluff. It is whether the product helps you decide what to post first and move the stack after generation.",
      bullets: [
        "Stronger review hierarchy than noisy clip dumps",
        "More operator-ready than basic AI clipping tools",
        "Built to sit between source ingest and posting workflow",
      ],
      links: [
        { href: "/compare/opus-clip-alternative", label: "Opus Clip alternative" },
        { href: "/compare/capcut-alternative", label: "CapCut alternative" },
      ],
    },
    {
      id: "faq",
      kicker: "FAQ",
      title: "Real product questions, not filler.",
      body: "Use the product for faster output, better packaging, and clearer post order. It helps operators and creators move with more confidence, not with fake promises.",
      bullets: [
        "Free stays useful, but premium unlocks cleaner export and deeper workflow leverage",
        "Uploads, history, queue, campaigns, and wallet surfaces stay in the same workspace",
        "The goal is more clips worth posting from content you already own",
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
  const exportReadyCount = useMemo(() => orderedClips.filter((clip) => clip.download_url).length, [orderedClips]);
  const leadPreviewReady = Boolean(result?.preview_asset_url);
  const leadExportReady = Boolean(result?.download_asset_url);
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

  function handleHomePointerMove(event: ReactPointerEvent<HTMLElement>) {
    if (reduceMotion || !homeStageRef.current) {
      return;
    }

    const bounds = homeStageRef.current.getBoundingClientRect();
    const offsetX = event.clientX - bounds.left;
    const offsetY = event.clientY - bounds.top;
    const normalizedX = (offsetX / bounds.width) * 2 - 1;
    const normalizedY = (offsetY / bounds.height) * 2 - 1;

    homeStageRef.current.style.setProperty("--home-pointer-x", `${offsetX}px`);
    homeStageRef.current.style.setProperty("--home-pointer-y", `${offsetY}px`);
    homeStageRef.current.style.setProperty("--home-tilt-x", `${normalizedX * 16}px`);
    homeStageRef.current.style.setProperty("--home-tilt-y", `${normalizedY * 12}px`);
  }

  function handleHomePointerLeave() {
    if (!homeStageRef.current) {
      return;
    }

    homeStageRef.current.style.setProperty("--home-pointer-x", "50%");
    homeStageRef.current.style.setProperty("--home-pointer-y", "36%");
    homeStageRef.current.style.setProperty("--home-tilt-x", "0px");
    homeStageRef.current.style.setProperty("--home-tilt-y", "0px");
  }

  const homeGeneratorSection = (
    <section className="hero-card rounded-[34px] p-6 sm:p-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="section-kicker">Generate first</p>
          <h2 className="mt-3 text-2xl font-semibold text-ink sm:text-[2rem]">Drop one source. Leave with ranked clips.</h2>
          <p className="mt-3 max-w-xl text-sm leading-7 text-subtext/90">
            {generationMode === "quick"
              ? "One link in. Ranked clips, hooks, captions, and previews back."
              : "Stay in the same workflow while LWA learns what you keep and tightens the next pack."}
          </p>
        </div>
        <StatPill tone="accent">{platform}</StatPill>
      </div>

      <form onSubmit={onSubmit} className="mt-7 space-y-5">
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

        <label className="block">
          <span className="mb-3 block text-sm font-medium text-ink/84">Source link</span>
          <input
            type="url"
            value={videoUrl}
            onChange={(event) => setVideoUrl(event.target.value)}
            placeholder="Paste YouTube, MP4, or any public video URL"
            className="input-surface w-full rounded-[24px] px-5 py-4 text-sm"
          />
        </label>

        <div>
          <span className="mb-3 block text-sm font-medium text-ink/84">Post for</span>
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
                      ? "border-accentCrimson/35 bg-[linear-gradient(135deg,rgba(255,0,60,0.2),rgba(255,45,166,0.14),rgba(0,231,255,0.08))] text-white shadow-crimson"
                      : "border-white/10 bg-white/[0.04] text-ink/72 hover:border-white/20 hover:bg-white/[0.06] hover:text-ink",
                  ].join(" ")}
                >
                  {item}
                </button>
              );
            })}
          </div>
        </div>

        <div className={["grid gap-4", generationMode === "pro" ? "md:grid-cols-2" : ""].join(" ")}>
          <div className="metric-tile rounded-[24px] p-4">
            <p className="text-sm font-medium text-ink">What happens first</p>
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
                    className="h-4 w-4 accent-cyan-400"
                  />
                  Improve results
                </label>
              </div>
            </div>
          ) : null}
        </div>

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-ink/60">
            {isLoading ? `${loadingStages[loadingStageIndex]}. ${GENERATOR_COPY.loading}` : idleRunSummary}
          </p>
          <button
            type="submit"
            disabled={isLoading}
            className="primary-button inline-flex min-w-[220px] items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? GENERATOR_COPY.submitting : GENERATOR_COPY.submit}
          </button>
        </div>

        {isLoading ? <LoadingSequence stages={loadingStages} activeIndex={loadingStageIndex} /> : null}

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
              <p className="section-kicker">{initialSection === "upload" ? "Upload + Generate" : rewriteSurfaceLabel("Generate")}</p>
              <h2 className="page-title mt-3 text-3xl font-semibold text-ink sm:text-[2.4rem]">
                {GENERATOR_COPY.title}
              </h2>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-subtext">
                {generationMode === "quick"
                  ? "Keep the first run simple: paste a source, get the ranked pack, then decide what to post."
                  : GENERATOR_COPY.subhead}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <StatPill tone="accent">{planSurface.name}</StatPill>
              <StatPill tone="signal">{result ? "Live output" : "Premium review"}</StatPill>
            </div>
          </div>

          <form onSubmit={onSubmit} className="mt-8 space-y-6">
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

            <label className="block">
              <span className="mb-3 block text-sm font-medium text-ink/84">Source link</span>
              <input
                type="url"
                value={videoUrl}
                onChange={(event) => setVideoUrl(event.target.value)}
                placeholder="Paste YouTube, MP4, or any public video URL"
                className="input-surface w-full rounded-[24px] px-5 py-4 text-sm"
              />
            </label>

            <div>
              <span className="mb-3 block text-sm font-medium text-ink/84">Post for</span>
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
                          ? "border-accentCrimson/35 bg-[linear-gradient(135deg,rgba(255,0,60,0.2),rgba(255,45,166,0.14),rgba(0,231,255,0.08))] text-white shadow-crimson"
                          : "border-white/10 bg-white/[0.04] text-ink/72 hover:border-white/20 hover:bg-white/[0.06] hover:text-ink",
                      ].join(" ")}
                    >
                      {item}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className={["grid gap-4", generationMode === "pro" ? "md:grid-cols-2" : ""].join(" ")}>
              <div className="metric-tile rounded-[24px] p-4">
                <p className="text-sm font-medium text-ink">What happens first</p>
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
                      <p className="mt-1 text-sm text-ink/60">Bias new runs toward what you keep.</p>
                      {preferenceProfile.topPackagingAngle || preferenceProfile.topHookStyle ? (
                        <p className="mt-3 text-sm text-accent">
                          Favoring {preferenceProfile.topPackagingAngle || "strong"} packaging
                          {preferenceProfile.topHookStyle ? ` and ${preferenceProfile.topHookStyle} hooks` : ""}.
                        </p>
                      ) : (
                        <p className="mt-3 text-sm text-ink/46">Mark what lands. The browser remembers.</p>
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
              ) : null}
            </div>

            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <p className="text-sm text-ink/60">
                {isLoading
                  ? `${loadingStages[loadingStageIndex]}. ${GENERATOR_COPY.loading}`
                  : result
                    ? "Clip pack ready. Review first, queue next, export when it fits."
                    : idleRunSummary}
              </p>
              <button
                type="submit"
                disabled={isLoading}
                className="primary-button inline-flex min-w-[240px] items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isLoading ? GENERATOR_COPY.submitting : GENERATOR_COPY.submit}
              </button>
            </div>

            {isLoading ? <LoadingSequence stages={loadingStages} activeIndex={loadingStageIndex} /> : null}

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
            <p className="section-kicker">Plan status</p>
            <h3 className="mt-3 text-2xl font-semibold text-ink">{planSurface.name}</h3>
            <div className="mt-5 grid gap-3">
              <MetricTile
                label="Credits left"
                value={typeof creditsRemaining === "number" ? String(creditsRemaining) : String(planLimits.generationsPerDay)}
                detail={typeof creditsRemaining === "number" ? "Available today" : "Daily run limit"}
              />
              <MetricTile label="Clip access" value={String(planLimits.clipLimit)} detail="Visible ranked clips per run" />
              <MetricTile label="Uploads" value={String(planLimits.uploadsPerDay)} detail="Local source uploads today" />
            </div>
            <div className="mt-4 space-y-3">
              {!activeFeatureFlags.premium_exports ? (
                <div className="metric-tile rounded-[24px] px-4 py-3 text-sm text-ink/72">
                  Pro unlocks clean exports, 20 ranked clips, stronger hook coverage, and wallet visibility.
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
            <p className="mt-3 text-sm leading-7 text-ink/60">{token ? "Video, audio, or image. Same ranking flow." : "Sign in to unlock uploads and saved source reuse."}</p>
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
            <p className="section-kicker">Flow</p>
            <div className="mt-4 space-y-3 text-sm leading-7 text-ink/68">
              <p>1. LWA finds the moments worth cutting.</p>
              <p>2. Review the previews before you export.</p>
              <p>3. Queue the winners and move them fast.</p>
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
            <p className="section-kicker">{RESULTS_COPY.kicker}</p>
            <h3 className="page-title mt-3 text-3xl font-semibold text-ink sm:text-[2.4rem]">{RESULTS_COPY.title}</h3>
            <p className="mt-4 text-sm leading-7 text-subtext">{RESULTS_COPY.subhead}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <StatPill tone="accent">{displayedClips.length} clips</StatPill>
            <StatPill tone="neutral">{result.source_platform || "Upload"}</StatPill>
            {result.source_type ? <StatPill tone="neutral">{result.source_type.replace("_", " ")}</StatPill> : null}
            {result.processing_summary?.recommended_next_step ? <StatPill tone="signal">AI ranked</StatPill> : null}
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr),340px]">
        <div className="space-y-6">
          <div className="glass-panel rounded-[28px] p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-3xl">
                <p className="section-kicker">Lead asset</p>
                <h4 className="mt-3 text-2xl font-semibold text-ink">{result.source_title || "Processed source"}</h4>
                <p className="mt-3 text-sm leading-7 text-ink/70">{sourceTruthSummary}</p>
              </div>
              <div className="flex flex-wrap gap-3">
                {leadPreviewReady ? (
                  <a
                    href={result.preview_asset_url || undefined}
                    target="_blank"
                    rel="noreferrer"
                    className="secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium"
                  >
                    Open lead preview
                  </a>
                ) : null}
                {leadExportReady ? (
                  <a
                    href={result.download_asset_url || undefined}
                    download
                    className="primary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold"
                  >
                    Export lead asset
                  </a>
                ) : (
                  <span className="rounded-full border border-accentCrimson/24 bg-[linear-gradient(135deg,rgba(255,0,60,0.14),rgba(255,45,166,0.1))] px-4 py-2 text-sm text-[#ffe4eb]">
                    Upgrade for export
                  </span>
                )}
              </div>
            </div>
          </div>

          {!previewReadyCount ? (
            <InlineAlert tone="violet" title="Preview pending">
              The intelligence pack is ready, but no playable preview asset came back from this source. Review the copy and ranking now, then retry with a longer or cleaner source if you need a rendered cut.
            </InlineAlert>
          ) : null}

          {featuredClip ? (
            <div className="space-y-3">
              <p className="section-kicker">{RESULTS_COPY.topClip}</p>
              <HeroClip
                clip={featuredClip}
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
                  <p className="section-kicker">{RESULTS_COPY.gridTitle}</p>
                  <h4 className="mt-2 text-2xl font-semibold text-ink">{RESULTS_COPY.gridTitle}</h4>
                </div>
              </div>
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
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

          {orderedClips.length ? <ReviewOrderPanel clips={orderedClips} /> : null}

          <div className="glass-panel rounded-[28px] p-5">
            <p className="section-kicker">{RESULTS_COPY.outputTrust}</p>
            <h4 className="mt-3 text-xl font-semibold text-ink">What is ready now</h4>
            <div className="mt-4 grid gap-3">
              <MetricTile
                label="Playable clips"
                value={String(previewReadyCount)}
                detail={previewReadyCount ? "Playable previews are live in this pack" : "No playable previews came back yet"}
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
                detail={leadPreviewReady ? "Open the lead asset beside the ranked cuts" : "No lead preview asset came back yet"}
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
            <h4 className="mt-3 text-xl font-semibold text-ink">Move this pack fast</h4>
            <div className="mt-4 space-y-3 text-sm text-ink/72">
              <p>1. Post the lead clip first.</p>
              <p>2. Test the alternate hooks before recutting.</p>
              <p>3. Mark what lands so the next pack tightens.</p>
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
      <p className="mt-3 max-w-2xl text-sm leading-7 text-ink/60">{GENERATOR_COPY.outputIdle}</p>
    </section>
  ) : null;

  return (
    <main className="app-shell-grid min-h-screen">
      <AIBackground variant={isHome ? "home" : "workspace"} />
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
                      Forge the stack
                    </button>
                  </>
                )}
              </div>
            }
          />

          <section
            ref={homeStageRef}
            onPointerMove={handleHomePointerMove}
            onPointerLeave={handleHomePointerLeave}
            className="home-stage grid gap-12 pb-10 pt-16 lg:grid-cols-[1.06fr,0.94fr] lg:items-start"
          >
            <div className="space-y-7">
              <div className="home-stage-grid" aria-hidden="true">
                <div className="home-stage-sigil" />
                <div className="home-stage-constellation" />
                <div className="home-stage-fog" />
              </div>

              <div className="space-y-5">
                <div className="inline-flex items-center gap-3">
                  <span className="home-brand-mark flex h-11 w-11 items-center justify-center rounded-2xl border border-accentCrimson/24 bg-[rgba(255,255,255,0.03)] shadow-crimson">
                    <img src="/brand/lwa-mark.svg" alt="LWA omega mark" className="h-7 w-7" />
                  </span>
                  <p className="section-kicker">{HERO_COPY.kicker}</p>
                </div>
                <h1 className="page-title max-w-5xl text-5xl font-semibold leading-[0.98] text-ink sm:text-6xl lg:text-7xl">
                  Turn one source into the <span className="text-gradient">clips people actually replay.</span>
                </h1>
                <p className="max-w-3xl text-base leading-8 text-subtext sm:text-lg">
                  {HERO_COPY.subhead}
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
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

              <p className="text-sm uppercase tracking-[0.24em] text-ink/56">Built for creators, clippers, and operators</p>

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
            </div>
          </section>

          {!result && !isLoading ? <HomeDiscoveryAccordion sections={homeDiscoverySections} /> : null}
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
                <section className="rounded-[24px] border border-accentCrimson/24 bg-accentCrimson/10 px-5 py-4 text-sm text-rose-100">
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
          ? "border-accentCrimson/35 bg-[linear-gradient(135deg,rgba(255,0,60,0.2),rgba(255,45,166,0.14),rgba(0,231,255,0.08))] text-white shadow-crimson"
          : tone === "signal"
            ? "border-cyan-400/25 bg-[linear-gradient(135deg,rgba(0,231,255,0.16),rgba(255,0,60,0.08))] text-white"
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

function HomeDiscoveryAccordion({
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
    <section className="space-y-4 pb-10">
      <div className="hero-card rounded-[30px] p-6 sm:p-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="section-kicker">Learn more</p>
            <h2 className="mt-3 text-3xl font-semibold text-ink">Open the full breakdown when you want it.</h2>
            <p className="mt-4 text-sm leading-7 text-subtext">
              The hero stays clean. The deeper workflow, comparison, and FAQ layers stay one tap away and fully readable.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <StatPill tone="neutral">Compare</StatPill>
            <StatPill tone="signal">Workflow</StatPill>
            <StatPill tone="neutral">FAQ</StatPill>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {sections.map((section, index) => (
          <details
            key={section.id}
            className={index === 0 ? "home-proof-card home-proof-card-lead rounded-[26px] p-0" : "glass-panel rounded-[26px] p-0"}
            open={index === 0}
          >
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 px-5 py-5 marker:content-none">
              <div className="min-w-0">
                <p className="section-kicker">{section.kicker}</p>
                <h3 className="mt-2 text-xl font-semibold text-ink" dir="auto">
                  {section.title}
                </h3>
              </div>
              <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-xs font-semibold text-ink/72">
                Open
              </span>
            </summary>

            <div className="border-t border-white/8 px-5 pb-5 pt-4">
              <p className="max-w-3xl text-sm leading-7 text-subtext" dir="auto">
                {section.body}
              </p>
              <div className="mt-4 grid gap-3">
                {section.bullets.map((bullet) => (
                  <div key={bullet} className="metric-tile rounded-[22px] px-4 py-3 text-sm text-ink/78" dir="auto">
                    {bullet}
                  </div>
                ))}
              </div>
              {section.links?.length ? (
                <div className="mt-4 flex flex-wrap gap-3">
                  {section.links.map((link) => (
                    <Link
                      key={link.href}
                      href={link.href}
                      className="secondary-button inline-flex items-center justify-center rounded-full px-4 py-2.5 text-sm font-medium"
                    >
                      {link.label}
                    </Link>
                  ))}
                </div>
              ) : null}
            </div>
          </details>
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
          <h4 className="mt-3 text-xl font-semibold text-ink">Best clip first</h4>
        </div>
        <StatPill tone="accent">{ordered.length} ranked</StatPill>
      </div>

      <div className="mt-5 space-y-3">
        {ordered.map((clip, index) => {
          const order = clip.post_rank || clip.best_post_order || clip.rank || index + 1;
          const detail = clip.thumbnail_text || clip.cta_suggestion || clip.packaging_angle || "Ready for review";
          const active = index === 0;

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
          <p className="text-lg font-medium text-ink">LWA is compiling the pack</p>
          <p className="text-sm text-ink/60">Real media in. Ranked clips, copy, and previews out.</p>
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
      ? "border-red-400/20 bg-red-400/8 text-red-100"
      : "border-neonPurple/20 bg-neonPurple/10 text-ink";

  return (
    <div className={["rounded-[24px] border px-5 py-4 text-sm", toneClass].join(" ")}>
      {title ? <p className="mb-2 text-xs uppercase tracking-[0.24em] text-muted">{title}</p> : null}
      {children}
    </div>
  );
}
