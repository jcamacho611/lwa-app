"use client";

import Link from "next/link";
import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { AccountWorkspace } from "./account-workspace";
import { AuthPanel } from "./auth-panel";
import { BatchPanel } from "./batch-panel";
import { CampaignPanel } from "./campaign-panel";
import { ClipCard } from "./clip-card";
import { ClipPackEditor, ClipPatchPayload } from "./clip-pack-editor";
import { HistoryPanel } from "./history-panel";
import { PostingPanel } from "./posting-panel";
import { SettingsPanel } from "./settings-panel";
import { WalletPanel } from "./wallet-panel";
import {
  BatchSummary,
  CampaignSummary,
  ClipPackDetail,
  ClipPackSummary,
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

const platforms: PlatformOption[] = ["TikTok", "Instagram Reels", "YouTube Shorts"];
const navItems = [
  { href: "/", label: "Home", section: "home" },
  { href: "/generate", label: "Generate", section: "generate" },
  { href: "/history", label: "History", section: "history" },
  { href: "/batches", label: "Batches", section: "batches" },
  { href: "/campaigns", label: "Campaigns", section: "campaigns" },
  { href: "/wallet", label: "Wallet", section: "wallet" },
  { href: "/settings", label: "Settings", section: "settings" },
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
        description: pageDescription || "Operational web surfaces for generation, packaging, and account state.",
      };
    }

    switch (initialSection) {
      case "dashboard":
        return {
          label: "Dashboard",
          title: "Creator control room",
          description: "See account state, recent runs, posting scaffolding, and the operational surfaces that turn this into a real product.",
        };
      case "generate":
        return {
          label: "Generate",
          title: "Compile a new clip pack",
          description: "Run the same backend pipeline from the browser with ranked hooks, captions, timestamps, and packaging output.",
        };
      case "upload":
        return {
          label: "Upload",
          title: "Bring your own source file",
          description: "Signed-in users can upload source video files and run them through the same real generation pipeline.",
        };
      case "history":
        return {
          label: "History",
          title: "Reopen saved work",
          description: "Browse saved clip packs, reopen ranked results, and make lightweight metadata edits in the browser.",
        };
      case "batches":
        return {
          label: "Batches",
          title: "Queue multi-source runs",
          description: "Turn uploads and pasted URLs into repeatable batch workflows without replacing the current backend.",
        };
      case "campaigns":
        return {
          label: "Campaigns",
          title: "Create distribution briefs",
          description: "Define campaign angle, payout scaffolding, and platform targets for grouped clip workflows.",
        };
      case "wallet":
        return {
          label: "Wallet",
          title: "Track ledger state",
          description: "Review wallet summary, ledger entries, and payout request groundwork tied to your account.",
        };
      case "settings":
        return {
          label: "Settings",
          title: "Manage account state",
          description: "Review plan, session, connected workflow surfaces, and the current operational product state.",
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
  }, []);

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

    try {
      const data = await generateClips(
        {
          url: videoUrl.trim() || undefined,
          platform,
          uploadFileId: selectedUpload?.file_id || selectedUpload?.source_ref?.upload_id,
        },
        token,
      );
      setResult(data);
      if (token) {
        await refreshAccount(token);
      }
    } catch (submitError) {
      setResult(null);
      setError(submitError instanceof Error ? submitError.message : "Unable to generate clips right now.");
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

  const featuredClip = result?.clips?.[0] ?? null;
  const remainingClips = result?.clips?.slice(1) ?? [];
  const requiresAccount = !["home", "generate", "upload"].includes(initialSection);
  const showGenerator = ["home", "generate", "upload"].includes(initialSection);
  const showDashboard = ["home", "dashboard"].includes(initialSection);
  const showHistory = initialSection === "history";
  const showBatches = initialSection === "batches";
  const showCampaigns = initialSection === "campaigns";
  const showWallet = initialSection === "wallet";
  const showSettings = initialSection === "settings";
  const showPostingOnDashboard = initialSection === "dashboard";

  return (
    <main className="min-h-screen bg-hero-radial">
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

      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 pb-16 pt-8 sm:px-6 lg:px-8">
        <header className="mb-10 flex flex-col gap-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-sm font-semibold text-ink shadow-glow">
                IWA
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.28em] text-muted">LWA Web</p>
                <h1 className="text-base font-semibold text-ink">Clip Pack Studio</h1>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {user ? (
                <>
                  <div className="hidden rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-ink/70 md:block">
                    {user.email} · {user.plan_code || "free"}
                  </div>
                  <Link
                    href="/dashboard"
                    className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
                  >
                    Dashboard
                  </Link>
                </>
              ) : (
                <div className="hidden rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-ink/70 md:block">
                  Browser-first creator workflow
                </div>
              )}

              {!user ? (
                <>
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode("login");
                      setAuthOpen(true);
                    }}
                    className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
                  >
                    Sign In
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode("signup");
                      setAuthOpen(true);
                    }}
                    className="rounded-full bg-gradient-to-r from-accent to-accentSoft px-4 py-2 text-sm font-semibold text-white shadow-glow"
                  >
                    Create Account
                  </button>
                </>
              ) : null}
            </div>
          </div>

          <nav className="flex flex-wrap gap-2 rounded-[28px] border border-white/10 bg-white/[0.03] p-2">
            {navItems.map((item) => {
              const active = item.section === initialSection || (item.section === "home" && initialSection === "dashboard");
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={[
                    "rounded-full px-4 py-2 text-sm transition",
                    active ? "bg-accent/12 text-accent shadow-glow" : "text-ink/68 hover:bg-white/[0.05] hover:text-ink",
                  ].join(" ")}
                >
                  {item.label}
                </Link>
              );
            })}
            <Link
              href="/upload"
              className={[
                "rounded-full px-4 py-2 text-sm transition",
                initialSection === "upload" ? "bg-accent/12 text-accent shadow-glow" : "text-ink/68 hover:bg-white/[0.05] hover:text-ink",
              ].join(" ")}
            >
              Upload
            </Link>
          </nav>
        </header>

        {initialSection === "home" ? (
          <section className="mb-10 grid gap-8 lg:grid-cols-[1.15fr,0.85fr]">
            <div className="space-y-6">
              <div className="space-y-4">
                <p className="text-xs uppercase tracking-[0.34em] text-accent">AI Content Repurposer</p>
                <h2 className="max-w-3xl text-4xl font-semibold leading-tight text-ink sm:text-5xl lg:text-6xl">
                  Turn Videos Into <span className="text-gradient">Viral Clips</span>
                </h2>
                <p className="max-w-2xl text-base leading-7 text-ink/68 sm:text-lg">
                  AI-powered clip generation in seconds. Paste one source, choose a platform, and get ranked hooks,
                  captions, timestamps, and packaging-ready outputs back.
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                <a
                  href="#generator"
                  className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-accent to-accentSoft px-6 py-3 text-sm font-semibold text-white shadow-glow transition hover:scale-[1.01]"
                >
                  Start Generating
                </a>
                <div className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm text-ink/72">
                  Standalone web app for Railway
                </div>
              </div>
            </div>

            <div className="glass-panel rounded-[32px] p-6 sm:p-7">
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-muted">System Status</p>
                  <h3 className="mt-2 text-2xl font-semibold text-ink">Ready to compile clips</h3>
                </div>
                <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-300">
                  Live
                </div>
              </div>

              <div className="space-y-4">
                <Metric label="Backend" value="Railway connected" />
                <Metric label="Outputs" value="Hooks, captions, timestamps" />
                <Metric label="Works Anywhere" value="Whop, domain, Gumroad, Lemon Squeezy" />
                <Metric label="Account" value={user ? `${user.plan_code || "free"} plan active` : "Guest mode"} />
              </div>
            </div>
          </section>
        ) : pageIntro ? (
          <section className="mb-10 glass-panel rounded-[32px] p-6 sm:p-8">
            <p className="text-xs uppercase tracking-[0.28em] text-accent">{pageIntro.label}</p>
            <h2 className="mt-3 text-4xl font-semibold text-ink">{pageIntro.title}</h2>
            <p className="mt-4 max-w-3xl text-base leading-7 text-ink/68">{pageIntro.description}</p>
          </section>
        ) : null}

        {showGenerator ? (
          <section id="generator" className="glass-panel rounded-[32px] p-5 sm:p-8">
            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-muted">{initialSection === "upload" ? "Upload + Generate" : "Generate"}</p>
                <h3 className="mt-2 text-2xl font-semibold text-ink">
                  {initialSection === "upload" ? "Upload a source and build a clip pack" : "Paste a source and build a clip pack"}
                </h3>
              </div>
              {result?.processing_summary ? (
                <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink/70">
                  {result.processing_summary.ai_provider || "fallback"} · {result.processing_summary.target_platform || platform}
                </div>
              ) : null}
            </div>

            <form onSubmit={onSubmit} className="space-y-5">
              <div className="grid gap-5 lg:grid-cols-[1fr,auto]">
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-ink/80">Video URL</span>
                  <input
                    type="url"
                    value={videoUrl}
                    onChange={(event) => setVideoUrl(event.target.value)}
                    placeholder="https://www.youtube.com/watch?v=..."
                    className="w-full rounded-2xl border border-white/10 bg-white/5 px-5 py-4 text-sm text-ink outline-none transition placeholder:text-muted focus:border-accent/40 focus:bg-white/[0.07]"
                  />
                </label>

                <div className="min-w-[220px]">
                  <span className="mb-2 block text-sm font-medium text-ink/80">Platform</span>
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-3 lg:grid-cols-1">
                    {platforms.map((item) => {
                      const active = item === platform;
                      return (
                        <button
                          key={item}
                          type="button"
                          onClick={() => setPlatform(item)}
                          className={[
                            "rounded-2xl border px-4 py-3 text-sm font-medium transition",
                            active
                              ? "border-accent/30 bg-accent/12 text-accent shadow-glow"
                              : "border-white/10 bg-white/5 text-ink/72 hover:border-white/20 hover:bg-white/[0.07]",
                          ].join(" ")}
                        >
                          {item}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="text-sm text-ink/60">
                  Submit a public video URL or upload a file and get ranked clips with packaging suggestions back.
                </div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="inline-flex min-w-[210px] items-center justify-center rounded-full bg-gradient-to-r from-accent to-accentSoft px-6 py-3.5 text-sm font-semibold text-white shadow-glow transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isLoading ? "Analyzing video..." : "Generate Clips"}
                </button>
              </div>
            </form>

            <div className="mt-5 flex flex-col gap-4 rounded-[28px] border border-white/10 bg-white/[0.03] p-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-medium text-ink">Optional upload source</p>
                <p className="mt-1 text-sm text-ink/60">
                  Signed-in users can upload `mp4`, `mov`, `m4v`, or `webm` and run the same backend pipeline.
                </p>
                <p className="mt-2 text-sm text-accent">{uploadingFileName ? `Uploading ${uploadingFileName}...` : activeSourceLabel}</p>
              </div>
              <label className="inline-flex cursor-pointer items-center justify-center rounded-full border border-white/12 bg-white/6 px-5 py-3 text-sm font-medium text-ink transition hover:border-accent/30 hover:bg-accent/10 hover:text-accent">
                {token ? "Upload Video" : "Sign in to upload"}
                <input
                  type="file"
                  accept=".mp4,.mov,.m4v,.webm,video/mp4,video/quicktime,video/webm"
                  className="hidden"
                  onChange={onUploadSelected}
                />
              </label>
            </div>

            {isLoading ? (
              <div className="mt-6 rounded-[28px] border border-white/10 bg-white/[0.03] px-5 py-10 text-center">
                <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-white/10 border-t-accent" />
                <p className="text-lg font-medium text-ink">Analyzing video...</p>
                <p className="mt-2 text-sm text-ink/60">Scoring moments, generating hooks, and packaging your best clips.</p>
              </div>
            ) : null}

            {error ? (
              <div className="mt-6 rounded-[28px] border border-red-400/20 bg-red-400/8 px-5 py-4 text-sm text-red-100">
                {error}
              </div>
            ) : null}
          </section>
        ) : null}

        {!result && !isLoading && showGenerator ? (
          <section className="mt-10">
            <div className="glass-panel rounded-[32px] p-6 sm:p-8">
              <p className="text-xs uppercase tracking-[0.24em] text-muted">Ready State</p>
              <h3 className="mt-2 text-2xl font-semibold text-ink">Your generated clip pack will appear here</h3>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-ink/64">
                Paste a public video URL above to see ranked clips, packaging angles, captions, timestamps, and
                copy-ready output cards. This frontend is built to work on your own domain, marketplace links, and any
                browser-based flow.
              </p>
            </div>
          </section>
        ) : null}

        {result ? (
          <section className="mt-10 space-y-6">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-muted">Results</p>
                <h3 className="mt-2 text-3xl font-semibold text-ink">Generated clip pack</h3>
              </div>
              <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-ink/72">
                {result.clips.length} clips · {result.source_platform}
              </div>
            </div>

            {featuredClip ? (
              <div className="space-y-3">
                <p className="text-xs uppercase tracking-[0.24em] text-accent">Featured Clip</p>
                <ClipCard clip={featuredClip} featured />
              </div>
            ) : null}

            {remainingClips.length ? (
              <div className="grid gap-5 lg:grid-cols-2">
                {remainingClips.map((clip) => (
                  <ClipCard key={clip.id} clip={clip} />
                ))}
              </div>
            ) : null}
          </section>
        ) : null}

        {initialSection === "home" ? (
          <section className="mt-10 grid gap-5 lg:grid-cols-3">
            <FeatureCard
              title="Platform-agnostic"
              detail="Use the same app link from Whop, Gumroad, Lemon Squeezy, your own domain, or embedded browser flows."
            />
            <FeatureCard
              title="Future-ready"
              detail="The app is structured for auth, payments, and plan gating later without locking you to a single marketplace."
            />
            <FeatureCard
              title="Creator-friendly"
              detail="Hooks, captions, timestamps, and CTA suggestions stay readable, copyable, and fast to act on."
            />
          </section>
        ) : null}

        {accountError ? (
          <section className="mt-10">
            <div className="rounded-[28px] border border-amber-400/20 bg-amber-400/10 px-5 py-4 text-sm text-amber-100">
              {accountError}
            </div>
          </section>
        ) : null}

        {requiresAccount && !user ? (
          <section className="mt-10">
            <div className="glass-panel rounded-[32px] p-6 sm:p-8">
              <p className="text-xs uppercase tracking-[0.24em] text-muted">Authentication Required</p>
              <h3 className="mt-2 text-2xl font-semibold text-ink">Sign in to open this workspace surface</h3>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/64">
                These pages are backed by account-owned uploads, clip packs, campaigns, wallet data, and posting state.
              </p>
              <div className="mt-5 flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("signup");
                    setAuthOpen(true);
                  }}
                  className="rounded-full bg-gradient-to-r from-accent to-accentSoft px-5 py-3 text-sm font-semibold text-white shadow-glow"
                >
                  Create Account
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("login");
                    setAuthOpen(true);
                  }}
                  className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
                >
                  Sign In
                </button>
              </div>
            </div>
          </section>
        ) : null}

        {showDashboard && user ? (
          <>
            <AccountWorkspace
              user={user}
              wallet={wallet}
              clipPacks={clipPacks}
              uploads={uploads}
              batches={batches}
              campaigns={campaigns}
              onSignOut={onSignOut}
              onOpenClipPack={openClipPack}
              selectedClipPackId={selectedClipPackId}
            />
            {showPostingOnDashboard ? (
              <section className="mt-10">
                <PostingPanel
                  connections={postingConnections}
                  scheduledPosts={scheduledPosts}
                  selectedClipPack={selectedClipPack}
                  onCreateConnection={handleCreatePostingConnection}
                  onCreateScheduledPost={handleCreateScheduledPost}
                  onUpdateScheduledPost={handleUpdateScheduledPost}
                />
              </section>
            ) : null}
          </>
        ) : null}

        {showHistory && user ? (
          <section className="mt-10">
            <HistoryPanel
              clipPacks={clipPacks}
              selectedClipPackId={selectedClipPackId}
              isLoading={isClipPackLoading}
              onOpenClipPack={openClipPack}
            />
          </section>
        ) : null}

        {showBatches && user ? (
          <section className="mt-10">
            <BatchPanel
              batches={batches}
              uploads={uploads}
              currentVideoUrl={videoUrl}
              selectedUpload={selectedUpload}
              platform={platform}
              onCreate={handleBatchCreate}
            />
          </section>
        ) : null}

        {showCampaigns && user ? (
          <section className="mt-10">
            <CampaignPanel
              campaigns={campaigns}
              onCreate={handleCampaignCreate}
              onUpdateStatus={handleCampaignStatusUpdate}
            />
          </section>
        ) : null}

        {showWallet && user ? (
          <section className="mt-10">
            <WalletPanel wallet={wallet} ledgerEntries={walletLedger} onRequestPayout={handlePayoutRequest} />
          </section>
        ) : null}

        {showSettings && user ? (
          <section className="mt-10 space-y-10">
            <SettingsPanel user={user} wallet={wallet} onSignOut={onSignOut} />
            <PostingPanel
              connections={postingConnections}
              scheduledPosts={scheduledPosts}
              selectedClipPack={selectedClipPack}
              onCreateConnection={handleCreatePostingConnection}
              onCreateScheduledPost={handleCreateScheduledPost}
              onUpdateScheduledPost={handleUpdateScheduledPost}
            />
          </section>
        ) : null}

        {selectedClipPack && user ? (
          <ClipPackEditor clipPack={selectedClipPack} onSave={saveClipMetadata} onClose={() => setSelectedClipPack(null)} />
        ) : null}

        {!user && initialSection === "home" ? (
          <section className="mt-10">
            <div className="glass-panel rounded-[32px] p-6 sm:p-8">
              <p className="text-xs uppercase tracking-[0.24em] text-muted">Account Layer</p>
              <h3 className="mt-2 text-2xl font-semibold text-ink">Sign in to unlock uploads, history, wallet, and workflow state</h3>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/64">
                Guest mode is enough to try the generator. Accounts add saved clip packs, upload-backed generation,
                wallet visibility, and future-ready campaign and batch workflows on top of the same backend.
              </p>
              <div className="mt-5 flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("signup");
                    setAuthOpen(true);
                  }}
                  className="rounded-full bg-gradient-to-r from-accent to-accentSoft px-5 py-3 text-sm font-semibold text-white shadow-glow"
                >
                  Create Account
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("login");
                    setAuthOpen(true);
                  }}
                  className="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
                >
                  Sign In
                </button>
              </div>
            </div>
          </section>
        ) : null}

        {isAccountLoading && user ? (
          <section className="mt-10">
            <div className="rounded-[28px] border border-white/10 bg-white/[0.03] px-5 py-4 text-sm text-ink/70">
              Refreshing account data...
            </div>
          </section>
        ) : null}
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm">
      <span className="text-ink/55">{label}</span>
      <span className="font-medium text-ink">{value}</span>
    </div>
  );
}

function FeatureCard({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="glass-panel rounded-[28px] p-5">
      <p className="text-base font-semibold text-ink">{title}</p>
      <p className="mt-3 text-sm leading-7 text-ink/64">{detail}</p>
    </div>
  );
}
