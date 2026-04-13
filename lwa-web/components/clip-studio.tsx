"use client";

import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { AccountWorkspace } from "./account-workspace";
import { AuthPanel } from "./auth-panel";
import { ClipCard } from "./clip-card";
import { ClipPackEditor, ClipPatchPayload } from "./clip-pack-editor";
import {
  BatchSummary,
  CampaignSummary,
  ClipPackDetail,
  ClipPackSummary,
  GenerateResponse,
  PlatformOption,
  UploadAsset,
  UserProfile,
  WalletSummary,
} from "../lib/types";
import {
  generateClips,
  loadBatches,
  loadCampaigns,
  loadClipPack,
  loadClipPacks,
  loadMe,
  loadUploads,
  loadWallet,
  logOut,
  patchClip,
  uploadSource,
} from "../lib/api";
import { clearStoredToken, readStoredToken, storeToken } from "../lib/auth";

const platforms: PlatformOption[] = ["TikTok", "Instagram Reels", "YouTube Shorts"];

export function ClipStudio() {
  const [videoUrl, setVideoUrl] = useState("");
  const [platform, setPlatform] = useState<PlatformOption>("TikTok");
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [wallet, setWallet] = useState<WalletSummary | null>(null);
  const [clipPacks, setClipPacks] = useState<ClipPackSummary[]>([]);
  const [uploads, setUploads] = useState<UploadAsset[]>([]);
  const [batches, setBatches] = useState<BatchSummary[]>([]);
  const [campaigns, setCampaigns] = useState<CampaignSummary[]>([]);
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

  useEffect(() => {
    const existingToken = readStoredToken();
    if (existingToken) {
      setToken(existingToken);
    }
  }, []);

  useEffect(() => {
    if (!token) {
      setUser(null);
      setWallet(null);
      setClipPacks([]);
      setUploads([]);
      setBatches([]);
      setCampaigns([]);
      return;
    }
    void refreshAccount(token);
  }, [token]);

  async function refreshAccount(authToken: string) {
    setIsAccountLoading(true);
    setAccountError(null);
    try {
      const [me, walletData, clipPackData, uploadData, batchData, campaignData] = await Promise.all([
        loadMe(authToken),
        loadWallet(authToken),
        loadClipPacks(authToken),
        loadUploads(authToken),
        loadBatches(authToken),
        loadCampaigns(authToken),
      ]);
      setUser(me);
      setWallet(walletData);
      setClipPacks(clipPackData);
      setUploads(uploadData);
      setBatches(batchData);
      setCampaigns(campaignData);
    } catch (refreshError) {
      const message = refreshError instanceof Error ? refreshError.message : "Unable to load account.";
      setAccountError(message);
      clearStoredToken();
      setToken(null);
    } finally {
      setIsAccountLoading(false);
    }
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
      const data = await generateClips({
        url: videoUrl.trim() || undefined,
        platform,
        uploadFileId: selectedUpload?.file_id || selectedUpload?.source_ref?.upload_id,
      }, token);
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

  const featuredClip = result?.clips?.[0] ?? null;
  const remainingClips = result?.clips?.slice(1) ?? [];

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
        }}
      />
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 pb-16 pt-8 sm:px-6 lg:px-8">
        <header className="mb-10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-sm font-semibold text-ink shadow-glow">
              IWA
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-muted">LWA Web</p>
              <h1 className="text-base font-semibold text-ink">Clip Pack Studio</h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {user ? (
              <div className="hidden rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-ink/70 md:block">
                {user.email} · {user.plan_code || "free"}
              </div>
            ) : (
              <div className="hidden rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-ink/70 md:block">
                Browser-first creator workflow
              </div>
            )}
            <button
              type="button"
              onClick={() => {
                setAuthMode(user ? "login" : "login");
                setAuthOpen(!user);
              }}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
            >
              {user ? "Account Ready" : "Sign In"}
            </button>
            {!user ? (
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
            ) : null}
          </div>
        </header>

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

        <section id="generator" className="glass-panel rounded-[32px] p-5 sm:p-8">
          <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-muted">Generate</p>
              <h3 className="mt-2 text-2xl font-semibold text-ink">Paste a source and build a clip pack</h3>
            </div>
            {result?.processing_summary ? (
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink/70">
                {result.processing_summary.ai_provider || "fallback"} ·{" "}
                {result.processing_summary.target_platform || platform}
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

        {!result && !isLoading ? (
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

        {user ? (
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
        ) : (
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
        )}

        {isAccountLoading ? (
          <div className="mt-6 text-sm text-ink/60">Loading account workspace…</div>
        ) : null}
        {isClipPackLoading ? <div className="mt-4 text-sm text-ink/60">Loading clip pack editor…</div> : null}
        {accountError ? (
          <div className="mt-4 rounded-2xl border border-red-400/20 bg-red-400/8 px-4 py-3 text-sm text-red-100">
            {accountError}
          </div>
        ) : null}
        {selectedClipPack ? (
          <ClipPackEditor
            clipPack={selectedClipPack}
            onSave={saveClipMetadata}
            onClose={() => {
              setSelectedClipPack(null);
              setSelectedClipPackId(null);
            }}
          />
        ) : null}
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3">
      <span className="text-sm text-ink/60">{label}</span>
      <span className="text-sm font-medium text-ink">{value}</span>
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
