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
import { PostingPanel } from "./posting-panel";
import { ReadyQueuePanel } from "./ready-queue-panel";
import { SettingsPanel } from "./settings-panel";
import { WalletPanel } from "./wallet-panel";
import {
  BatchSummary,
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
} from "../lib/types";
import {
  ApiError,
  createBatch,
  createCampaign,
  createPayoutRequest,
  createPostingConnection,
  createScheduledPost,
  generateClips,
  loadBatches,
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
        title: pageTitle || "LWA Web Workspace",
        description: pageDescription || "Run the product from any browser.",
      };
    }

    switch (initialSection) {
      case "dashboard":
        return {
          label: "Dashboard",
          title: "Your creator control room",
          description: "See current output, saved runs, queue state, and the account surfaces that keep the system moving.",
        };
      case "generate":
        return {
          label: "Generate",
          title: "Create a ranked clip pack",
          description: "Paste a source, target the platform, and get hooks, captions, timestamps, and posting order back fast.",
        };
      case "upload":
        return {
          label: "Upload",
          title: "Bring your own source file",
          description: "Use the same pipeline against uploaded source files when you want more control than a public URL.",
        };
      case "history":
        return {
          label: "History",
          title: "Reopen saved work",
          description: "Review past runs, inspect what won, and make lightweight packaging edits without starting over.",
        };
      case "batches":
        return {
          label: "Batches",
          title: "Queue multiple sources",
          description: "Combine uploads and links into repeatable runs when one video at a time is too slow.",
        };
      case "campaigns":
        return {
          label: "Campaigns",
          title: "Build structured content pushes",
          description: "Set the angle, platform targets, and requirements for a campaign before clips go live.",
        };
      case "wallet":
        return {
          label: "Wallet",
          title: "Track value and payout state",
          description: "Keep a clear view of credits, ledger movement, and payout requests from the same workspace.",
        };
      case "settings":
        return {
          label: "Settings",
          title: "Manage account and workflow",
          description: "Review plan state, session status, and the connected surfaces that support your workflow.",
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
      setPostingConnections([]);
      setScheduledPosts([]);
      return;
    }
    void refreshAccount(token);
  }, [token]);

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
      setError("Paste a public video URL or upload a file to generate your clip pack.");
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
    await createCampaign(token, payload);
    await refreshAccount(token);
  }

  async function handleCampaignStatusUpdate(campaignId: string, status: string) {
    if (!token) {
      throw new Error("Authentication required.");
    }
    await updateCampaign(token, campaignId, { status });
    await refreshAccount(token);
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

  const generatorSection = (
    <section className="glass-panel rounded-[32px] p-5 sm:p-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-2xl">
          <p className="section-kicker">{initialSection === "upload" ? "Upload + Generate" : "Generate"}</p>
          <h2 className="page-title mt-3 text-3xl font-semibold text-ink sm:text-4xl">
            {isHome ? "Turn one source into a ranked clip pack" : "Create clips that are ready to post"}
          </h2>
          <p className="mt-4 text-sm leading-7 text-ink/64 sm:text-base">
            Hooks, captions, timestamps, reasons, and post order. Paste a source once, then move fast.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatPill tone="neutral">{result?.processing_summary?.ai_provider || "ready"} mode</StatPill>
          <StatPill tone="neutral">{platform}</StatPill>
        </div>
      </div>

      <form onSubmit={onSubmit} className="mt-8 space-y-5">
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr),260px]">
          <label className="block">
            <span className="mb-3 block text-sm font-medium text-ink/84">Video URL</span>
            <input
              type="url"
              value={videoUrl}
              onChange={(event) => setVideoUrl(event.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              className="input-surface w-full rounded-[24px] px-5 py-4 text-sm"
            />
          </label>

          <div>
            <span className="mb-3 block text-sm font-medium text-ink/84">Target platform</span>
            <div className="grid grid-cols-1 gap-2">
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
                        ? "border-accent/30 bg-accent/12 text-white shadow-glow"
                        : "border-white/10 bg-white/5 text-ink/72 hover:border-white/20 hover:bg-white/[0.07] hover:text-ink",
                    ].join(" ")}
                  >
                    {item}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <div className="grid gap-4 xl:grid-cols-3">
          <div className="panel-subtle rounded-[24px] p-4">
            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div>
                <p className="text-sm font-medium text-ink">Improve my results</p>
                <p className="mt-1 text-sm text-ink/60">
                  Learn from your taste locally, then bias future runs toward the angles you keep.
                </p>
                {preferenceProfile.topPackagingAngle || preferenceProfile.topHookStyle ? (
                  <p className="mt-3 text-sm text-accent">
                    Favoring {preferenceProfile.topPackagingAngle || "strong"} packaging
                    {preferenceProfile.topHookStyle ? ` and ${preferenceProfile.topHookStyle} hooks` : ""}.
                  </p>
                ) : (
                  <p className="mt-3 text-sm text-ink/46">Mark clips good or bad to train your browser-side preferences.</p>
                )}
              </div>
              <label className="secondary-button inline-flex items-center gap-3 rounded-full px-4 py-3 text-sm">
                <input
                  type="checkbox"
                  checked={improveResults}
                  onChange={(event) => setImproveResults(event.target.checked)}
                  className="h-4 w-4 accent-cyan-400"
                />
                Improve future results
              </label>
            </div>
          </div>

          <div className="panel-subtle rounded-[24px] p-4">
            <p className="text-sm font-medium text-ink">Upload a source</p>
            <p className="mt-1 text-sm text-ink/60">Signed-in users can run the same pipeline from a local file.</p>
            <p className="mt-3 text-sm text-accent">{uploadingFileName ? `Uploading ${uploadingFileName}...` : activeSourceLabel}</p>
            <label className="secondary-button mt-4 inline-flex w-full cursor-pointer items-center justify-center rounded-full px-5 py-3 text-sm font-medium">
              {token ? "Upload video" : "Sign in to upload"}
              <input
                type="file"
                accept=".mp4,.mov,.m4v,.webm,video/mp4,video/quicktime,video/webm"
                className="hidden"
                onChange={onUploadSelected}
              />
            </label>
          </div>

          <div className="panel-subtle rounded-[24px] p-4">
            <p className="text-sm font-medium text-ink">Plan and limits</p>
            <p className="mt-1 text-sm text-ink/60">See how much output the current tier unlocks before you run the next pack.</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <StatPill tone="accent">{planSurface.name}</StatPill>
              <StatPill tone="neutral">{planLimits.clipLimit} clips per run</StatPill>
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <div className="rounded-[20px] border border-white/10 bg-white/[0.04] p-3">
                <p className="text-xs uppercase tracking-[0.22em] text-muted">Credits</p>
                <p className="mt-2 text-base font-semibold text-ink">
                  {typeof creditsRemaining === "number" ? `${creditsRemaining} remaining today` : `${planLimits.generationsPerDay} daily`}
                </p>
              </div>
              <div className="rounded-[20px] border border-white/10 bg-white/[0.04] p-3">
                <p className="text-xs uppercase tracking-[0.22em] text-muted">Uploads</p>
                <p className="mt-2 text-base font-semibold text-ink">{planLimits.uploadsPerDay} per day</p>
              </div>
            </div>
            <p className="mt-4 text-sm text-ink/60">
              {planSurface.watermark
                ? "Free exports keep the watermark until you upgrade."
                : "This plan unlocks clean exports without a watermark."}
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <p className="text-sm text-ink/60">
            Use a public video URL or an uploaded source file. The system will return ranked clips with packaging guidance.
          </p>
          <button
            type="submit"
            disabled={isLoading}
            className="primary-button inline-flex min-w-[220px] items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? "Analyzing video..." : "Generate clip pack"}
          </button>
        </div>

        {isLoading ? (
          <div className="panel-subtle rounded-[24px] px-5 py-8 text-center">
            <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-white/10 border-t-accent" />
            <p className="text-lg font-medium text-ink">Compiling the strongest moments...</p>
            <p className="mt-2 text-sm text-ink/60">
              Ranking clips, writing hooks, and shaping the pack
              {improveResults && preferenceProfile.topPackagingAngle ? ` around ${preferenceProfile.topPackagingAngle}` : ""}.
            </p>
          </div>
        ) : null}

        {error ? (
          <div className="rounded-[24px] border border-red-400/20 bg-red-400/8 px-5 py-4 text-sm text-red-100">{error}</div>
        ) : null}

        {paywallMessage ? (
          <div className="rounded-[24px] border border-neonPurple/20 bg-neonPurple/10 p-5">
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Out of credits</p>
            <h4 className="mt-2 text-xl font-semibold text-ink">Your current plan has hit today’s limit</h4>
            <p className="mt-3 text-sm leading-7 text-ink/70">{paywallMessage}</p>
            <div className="mt-5 flex flex-wrap gap-3">
              <Link href="/settings" className="primary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold">
                Review plan
              </Link>
              <Link href="/wallet" className="secondary-button inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium">
                Open wallet
              </Link>
            </div>
          </div>
        ) : null}
      </form>
    </section>
  );

  const resultsSection = result ? (
    <section className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="section-kicker">Results</p>
          <h3 className="page-title mt-3 text-3xl font-semibold text-ink sm:text-4xl">Your ranked clip pack</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatPill tone="neutral">{displayedClips.length} clips</StatPill>
          <StatPill tone="neutral">{result.source_platform}</StatPill>
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr),320px]">
        <div className="space-y-5">
          {featuredClip ? (
            <div className="space-y-3">
              <p className="section-kicker">Best first post</p>
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
          ) : null}
        </div>

        <div className="space-y-5">
          <ReadyQueuePanel items={readyQueue} onMove={handleMoveQueue} onRemove={handleRemoveQueue} onClear={handleClearQueue} />

          <div className="glass-panel rounded-[28px] p-5">
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Top Performing Angles</p>
            <h4 className="mt-3 text-xl font-semibold text-ink">What your taste is favoring</h4>
            <div className="mt-4 flex flex-wrap gap-2">
              {(preferenceProfile.preferredAngles.length ? preferenceProfile.preferredAngles : ["value", "curiosity", "story"])
                .slice(0, 3)
                .map((angle) => (
                  <span key={angle} className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-sm text-ink/82">
                    {angle}
                  </span>
                ))}
            </div>
            <p className="mt-4 text-sm leading-7 text-ink/60">
              {preferenceProfile.preferredHookStyles.length
                ? `Preferred hook styles: ${preferenceProfile.preferredHookStyles.join(", ")}.`
                : "No strong hook preference yet. Mark clips good or bad to tighten future outputs."}
            </p>
          </div>

          <div className="glass-panel rounded-[28px] p-5">
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Move faster</p>
            <h4 className="mt-3 text-xl font-semibold text-ink">How to use this pack</h4>
            <div className="mt-4 space-y-3 text-sm text-ink/72">
              <p>1. Post the top clip first.</p>
              <p>2. Test multiple hooks before rewriting the edit.</p>
              <p>3. Keep marking good and bad clips so the system gets sharper around your taste.</p>
            </div>
            <p className="mt-4 text-sm text-accent">
              {improveResults ? "Preference learning is active." : "Turn on Improve my results to apply local learning."}
            </p>
          </div>
        </div>
      </div>
    </section>
  ) : null;

  const emptyGeneratorState = !result && !isLoading && showGenerator ? (
    <section className="glass-panel rounded-[28px] p-6">
      <p className="text-xs uppercase tracking-[0.24em] text-muted">Ready</p>
      <h3 className="mt-3 text-2xl font-semibold text-ink">Your next clip pack will appear here</h3>
      <p className="mt-3 max-w-2xl text-sm leading-7 text-ink/60">
        Expect ranked clips, hook variants, caption styles, reasons, and post order once the source is processed.
      </p>
    </section>
  ) : null;

  return (
    <main className="app-shell-grid min-h-screen bg-hero-radial">
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
          <header className="flex items-center justify-between gap-4 rounded-full border border-white/10 bg-black/20 px-4 py-3 backdrop-blur-xl">
            <Link href="/" className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-sm font-semibold text-white shadow-glow">
                IWA
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-[0.28em] text-muted">LWA Omega</p>
                <p className="text-sm font-medium text-ink">Creator operating system</p>
              </div>
            </Link>

            <nav className="hidden items-center gap-2 md:flex">
              {marketingNavItems.map((item) => (
                <Link key={item.href} href={item.href} className="nav-pill rounded-full px-4 py-2 text-sm">
                  {item.label}
                </Link>
              ))}
            </nav>

            <div className="flex items-center gap-2">
              {user ? (
                <>
                  <Link href="/dashboard" className="secondary-button rounded-full px-4 py-2 text-sm font-medium">
                    Open workspace
                  </Link>
                  <span className="hidden rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-ink/72 sm:inline-flex">
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
                    className="secondary-button rounded-full px-4 py-2 text-sm font-medium"
                  >
                    Sign in
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode("signup");
                      setAuthOpen(true);
                    }}
                    className="primary-button rounded-full px-4 py-2 text-sm font-semibold"
                  >
                    Start now
                  </button>
                </>
              )}
            </div>
          </header>

          <section className="grid gap-10 pb-10 pt-14 lg:grid-cols-[1.06fr,0.94fr] lg:items-start">
            <div className="space-y-7">
              <div className="space-y-5">
                <p className="section-kicker">Built for creators who move fast</p>
                <h1 className="page-title max-w-4xl text-5xl font-semibold leading-[1.02] text-ink sm:text-6xl lg:text-7xl">
                  Turn long videos into <span className="text-gradient">ranked, viral-ready clips.</span>
                </h1>
                <p className="max-w-2xl text-base leading-8 text-ink/64 sm:text-lg">
                  Paste once. Get hooks, captions, timestamps, post order, and reasons back in one clean pack.
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                <Link href="/generate" className="primary-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold">
                  Open generate workspace
                </Link>
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode(user ? "login" : "signup");
                    setAuthOpen(true);
                  }}
                  className="secondary-button inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-medium"
                >
                  {user ? "Switch account" : "Create account"}
                </button>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                <KpiCard label="Outputs" value="Hooks + captions" detail="Multiple variations per clip." />
                <KpiCard label="Ranking" value="Post first" detail="Best clip is obvious." />
                <KpiCard label="Workflow" value="Browser-first" detail="Works anywhere a URL opens." />
              </div>
            </div>

            <div className="space-y-5">
              {generatorSection}
              {!result && !isLoading ? <MarketingPreview user={user} /> : null}
            </div>
          </section>

          {resultsSection ? <div className="space-y-6">{resultsSection}</div> : null}
        </div>
      ) : (
        <div className="mx-auto w-full max-w-[1440px] px-4 py-6 sm:px-6 lg:px-8">
          <div className="grid gap-6 lg:grid-cols-[250px,minmax(0,1fr)]">
            <aside className="hidden lg:block">
              <div className="sticky top-6 space-y-4">
                <div className="glass-panel rounded-[28px] p-5">
                  <Link href="/" className="flex items-center gap-3">
                    <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-sm font-semibold text-white shadow-glow">
                      IWA
                    </div>
                    <div>
                      <p className="text-[11px] uppercase tracking-[0.28em] text-muted">LWA Omega</p>
                      <p className="text-sm font-medium text-ink">Creator workspace</p>
                    </div>
                  </Link>
                  <p className="mt-4 text-sm leading-7 text-ink/60">
                    Generate, review, queue, and refine without bouncing between tools.
                  </p>
                </div>

                <nav className="glass-panel rounded-[28px] p-3">
                  <div className="space-y-1.5">
                    {visibleAppNavItems.map((item) => {
                      const active = item.section === initialSection;
                      return (
                        <Link
                          key={item.href}
                          href={item.href}
                          className={[
                            "block rounded-2xl px-4 py-3 text-sm font-medium transition",
                            active ? "nav-pill-active" : "nav-pill",
                          ].join(" ")}
                        >
                          {item.label}
                        </Link>
                      );
                    })}
                  </div>
                </nav>

                <div className="glass-panel rounded-[28px] p-5">
                  <p className="text-xs uppercase tracking-[0.24em] text-muted">Account</p>
                  {user ? (
                    <>
                      <p className="mt-3 text-base font-semibold text-ink">{user.email}</p>
                      <p className="mt-1 text-sm text-ink/60">Plan {planSurface.name}</p>
                      <div className="mt-4 flex flex-wrap gap-2">
                        <StatPill tone="accent">{clipPacks.length} packs</StatPill>
                        <StatPill tone="neutral">{uploads.length} uploads</StatPill>
                      </div>
                      <button
                        type="button"
                        onClick={onSignOut}
                        className="secondary-button mt-5 inline-flex w-full items-center justify-center rounded-full px-4 py-3 text-sm font-medium"
                      >
                        Sign out
                      </button>
                    </>
                  ) : (
                    <>
                      <p className="mt-3 text-sm leading-7 text-ink/60">Sign in to unlock uploads, history, campaigns, wallet, and queue state.</p>
                      <button
                        type="button"
                        onClick={() => {
                          setAuthMode("login");
                          setAuthOpen(true);
                        }}
                        className="primary-button mt-5 inline-flex w-full items-center justify-center rounded-full px-4 py-3 text-sm font-semibold"
                      >
                        Sign in
                      </button>
                    </>
                  )}
                </div>
              </div>
            </aside>

            <div className="space-y-6">
              <div className="glass-panel rounded-[28px] p-4 lg:hidden">
                <div className="flex items-center justify-between gap-3">
                  <Link href="/" className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-sm font-semibold text-white shadow-glow">
                      IWA
                    </div>
                    <div>
                      <p className="text-[11px] uppercase tracking-[0.28em] text-muted">LWA Omega</p>
                      <p className="text-sm font-medium text-ink">Creator workspace</p>
                    </div>
                  </Link>
                  {user ? (
                    <button
                      type="button"
                      onClick={onSignOut}
                      className="secondary-button rounded-full px-4 py-2 text-sm font-medium"
                    >
                      Sign out
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => {
                        setAuthMode("login");
                        setAuthOpen(true);
                      }}
                      className="primary-button rounded-full px-4 py-2 text-sm font-semibold"
                    >
                      Sign in
                    </button>
                  )}
                </div>
                <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
                  {visibleAppNavItems.map((item) => {
                    const active = item.section === initialSection;
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        className={[
                          "whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition",
                          active ? "nav-pill-active" : "nav-pill",
                        ].join(" ")}
                      >
                        {item.label}
                      </Link>
                    );
                  })}
                </div>
              </div>

              {pageIntro ? (
                <section className="glass-panel rounded-[32px] p-6 sm:p-8">
                  <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                    <div className="max-w-3xl">
                      <p className="section-kicker">{pageIntro.label}</p>
                      <h1 className="page-title mt-3 text-4xl font-semibold text-ink sm:text-5xl">{pageIntro.title}</h1>
                      <p className="mt-4 text-sm leading-7 text-ink/64 sm:text-base">{pageIntro.description}</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {user ? (
                        <>
                          <StatPill tone="accent">{planSurface.name}</StatPill>
                          <StatPill tone="neutral">{wallet ? `$${((wallet.available_cents || 0) / 100).toFixed(2)}` : "Wallet"}</StatPill>
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
                <section className="glass-panel rounded-[32px] p-6 sm:p-8">
                  <p className="section-kicker">Authentication required</p>
                  <h2 className="mt-3 text-3xl font-semibold text-ink">Sign in to open this workspace</h2>
                  <p className="mt-4 max-w-3xl text-sm leading-7 text-ink/60">
                    History, campaigns, wallet state, uploads, and posting queue all live inside your account.
                  </p>
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
                      campaigns={campaigns}
                      onCreate={handleCampaignCreate}
                      onUpdateStatus={handleCampaignStatusUpdate}
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
                  lockedMessage="Upgrade to Pro to edit hooks, captions, and trims directly from saved history."
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

function StatPill({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "accent" }) {
  return (
    <span
      className={[
        "rounded-full border px-3 py-1.5 text-xs font-medium",
        tone === "accent" ? "border-accent/20 bg-accent/10 text-accent" : "border-white/10 bg-white/5 text-ink/72",
      ].join(" ")}
    >
      {children}
    </span>
  );
}

function KpiCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="glass-panel rounded-[24px] p-5">
      <p className="text-xs uppercase tracking-[0.24em] text-muted">{label}</p>
      <p className="mt-3 text-2xl font-semibold text-ink">{value}</p>
      <p className="mt-2 text-sm leading-6 text-ink/60">{detail}</p>
    </div>
  );
}

function MarketingPreview({ user }: { user: UserProfile | null }) {
  return (
    <div className="glass-panel rounded-[28px] p-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-muted">What comes back</p>
          <h3 className="mt-2 text-xl font-semibold text-ink">A pack you can act on fast</h3>
        </div>
        <StatPill tone="accent">{user ? user.plan_code || "free" : "guest"}</StatPill>
      </div>

      <div className="mt-5 space-y-3">
        {[
          {
            title: "Clip 01",
            detail: "Score 92 · Curiosity angle · Post first",
          },
          {
            title: "3 hook variants + 4 caption styles",
            detail: "Viral, story, educational, controversial",
          },
          {
            title: "Clear next step",
            detail: "CTA, platform fit, and packaging reason included",
          },
        ].map((item) => (
          <div key={item.title} className="panel-subtle rounded-[20px] p-4">
            <p className="text-sm font-medium text-ink">{item.title}</p>
            <p className="mt-1 text-sm text-ink/60">{item.detail}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
