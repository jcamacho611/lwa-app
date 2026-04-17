"use client";

import Link from "next/link";
import { BatchSummary, CampaignSummary, ClipPackSummary, UploadAsset, UserProfile, WalletSummary } from "../lib/types";

type AccountWorkspaceProps = {
  user: UserProfile;
  wallet: WalletSummary | null;
  clipPacks: ClipPackSummary[];
  uploads: UploadAsset[];
  batches: BatchSummary[];
  campaigns: CampaignSummary[];
  readyQueueCount?: number;
  planLabel?: string;
  onSignOut: () => void;
  onOpenClipPack: (requestId: string) => void;
  selectedClipPackId?: string | null;
};

function formatCents(value?: number | null) {
  return `$${((value || 0) / 100).toFixed(2)}`;
}

export function AccountWorkspace({
  user,
  wallet,
  clipPacks,
  uploads,
  batches,
  campaigns,
  readyQueueCount = 0,
  planLabel,
  onSignOut,
  onOpenClipPack,
  selectedClipPackId,
}: AccountWorkspaceProps) {
  return (
    <section className="mt-10 space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="section-kicker">Workspace</p>
          <h3 className="mt-2 text-3xl font-semibold text-ink">Operator home</h3>
          <p className="mt-2 text-sm leading-7 text-ink/64">{user.email} · Runs, uploads, campaigns, and ledger state in one place.</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <span className="rounded-full border border-accent/20 bg-accent/10 px-4 py-2 text-sm font-medium text-accent">
            Plan: {planLabel || user.plan_code}
          </span>
          <span className="rounded-full border border-white/10 bg-white/[0.05] px-4 py-2 text-sm font-medium text-ink/80">
            Role: {user.role || "creator"}
          </span>
          <Link
            href="/history"
            className="secondary-button rounded-full px-4 py-2 text-sm font-medium"
          >
            Full History
          </Link>
          <Link
            href="/campaigns"
            className="secondary-button rounded-full px-4 py-2 text-sm font-medium"
          >
            Campaigns
          </Link>
          <button
            type="button"
            onClick={onSignOut}
            className="secondary-button rounded-full px-4 py-2 text-sm font-medium"
          >
            Sign Out
          </button>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <StatCard label="Saved clip packs" value={String(clipPacks.length)} detail="Stored against your account." />
        <StatCard label="Uploads" value={String(uploads.length)} detail="Source files ready to reuse." />
        <StatCard label="Ready queue" value={String(readyQueueCount)} detail="Clips staged for next posting passes." />
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <div className="glass-panel rounded-[28px] p-5">
          <p className="text-lg font-semibold text-ink">Saved Clip Packs</p>
          <p className="mt-2 text-sm leading-7 text-ink/64">Recent ranked outputs.</p>
          <div className="mt-5 space-y-3">
            {clipPacks.length ? (
              clipPacks.slice(0, 5).map((item) => {
                const selected = item.request_id === selectedClipPackId;
                return (
                  <div
                    key={item.request_id}
                    className={[
                      "rounded-2xl border p-4 transition",
                      selected ? "border-accent/30 bg-accent/10" : "border-white/8 bg-white/[0.03]",
                    ].join(" ")}
                  >
                    <p className="text-sm font-medium text-ink">{item.source_title || item.video_url || item.request_id}</p>
                    <p className="mt-2 text-sm text-ink/62">
                      {item.clip_count || 0} clips · {item.target_platform || "TikTok"} · {item.created_at || "recent"}
                    </p>
                    <button
                      type="button"
                      onClick={() => onOpenClipPack(item.request_id)}
                      className="mt-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
                    >
                      {selected ? "Open in editor" : "Review clip pack"}
                    </button>
                  </div>
                );
              })
            ) : (
              <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4 text-sm text-ink/62">
                Generate while signed in to build your history.
              </div>
            )}
          </div>
        </div>
        <Panel
          title="Uploads"
          subtitle="Source files stored for reuse."
          empty="Upload a video file from the generator to see it here."
          items={uploads.slice(0, 5).map((item) => ({
            title: item.file_name || item.filename || "Uploaded source",
            detail: `${item.content_type || "file"} · ${item.file_size || item.size_bytes || 0} bytes`,
          }))}
        />
        <Panel
          title="Batches"
          subtitle="Multi-source runs you can reopen and reuse."
          empty="No batches yet."
          items={batches.slice(0, 5).map((item) => ({
            title: item.title,
            detail: `${item.status} · ${item.completed_sources}/${item.total_sources} completed`,
          }))}
        />
        <Panel
          title="Campaigns"
          subtitle="Active briefs and content pushes."
          empty="No campaigns yet."
          items={campaigns.slice(0, 5).map((item) => ({
            title: item.name || item.title || "Campaign",
            detail: `${item.status} · ${item.target_angle || "no angle"} · ${item.submission_summary?.total_assignments || 0} assignments · ${formatCents(item.payout_cents_per_1000_views)} per 1k views`,
          }))}
        />
      </div>
    </section>
  );
}

function StatCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="hero-card rounded-[28px] p-5">
      <p className="text-sm text-ink/60">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-ink">{value}</p>
      <p className="mt-3 text-sm leading-7 text-ink/64">{detail}</p>
    </div>
  );
}

function Panel({
  title,
  subtitle,
  items,
  empty,
}: {
  title: string;
  subtitle: string;
  items: { title: string; detail: string }[];
  empty: string;
}) {
  return (
    <div className="glass-panel rounded-[28px] p-5">
      <p className="text-lg font-semibold text-ink">{title}</p>
      <p className="mt-2 text-sm leading-7 text-ink/64">{subtitle}</p>
      <div className="mt-5 space-y-3">
        {items.length ? (
          items.map((item) => (
            <div key={`${item.title}-${item.detail}`} className="metric-tile rounded-[22px] p-4">
              <p className="text-sm font-medium text-ink">{item.title}</p>
              <p className="mt-2 text-sm text-ink/62">{item.detail}</p>
            </div>
          ))
        ) : (
          <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4 text-sm text-ink/62">{empty}</div>
        )}
      </div>
    </div>
  );
}
