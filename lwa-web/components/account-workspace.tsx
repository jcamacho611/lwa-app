"use client";

import { BatchSummary, CampaignSummary, ClipPackSummary, UploadAsset, UserProfile, WalletSummary } from "../lib/types";

type AccountWorkspaceProps = {
  user: UserProfile;
  wallet: WalletSummary | null;
  clipPacks: ClipPackSummary[];
  uploads: UploadAsset[];
  batches: BatchSummary[];
  campaigns: CampaignSummary[];
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
  onSignOut,
  onOpenClipPack,
  selectedClipPackId,
}: AccountWorkspaceProps) {
  return (
    <section className="mt-10 space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-muted">Workspace</p>
          <h3 className="mt-2 text-3xl font-semibold text-ink">Signed in as {user.email}</h3>
          <p className="mt-2 text-sm leading-7 text-ink/64">
            Your web workspace now follows the same backend account state as the iOS app and Railway backend.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <span className="rounded-full border border-accent/20 bg-accent/10 px-4 py-2 text-sm font-medium text-accent">
            Plan: {user.plan_code}
          </span>
          <button
            type="button"
            onClick={onSignOut}
            className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
          >
            Sign Out
          </button>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <StatCard label="Saved clip packs" value={String(clipPacks.length)} detail="Stored against your account." />
        <StatCard label="Uploads" value={String(uploads.length)} detail="Browser uploads ready for generation." />
        <StatCard label="Wallet available" value={formatCents(wallet?.available_cents)} detail="Groundwork for payouts and earnings." />
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <div className="glass-panel rounded-[28px] p-5">
          <p className="text-lg font-semibold text-ink">Saved Clip Packs</p>
          <p className="mt-2 text-sm leading-7 text-ink/64">Recent runs tied to your account.</p>
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
                      {selected ? "Open in editor" : "View clip pack"}
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
          subtitle="Queued and completed multi-source runs."
          empty="No batches yet."
          items={batches.slice(0, 5).map((item) => ({
            title: item.title,
            detail: `${item.status} · ${item.completed_sources}/${item.total_sources} completed`,
          }))}
        />
        <Panel
          title="Campaigns"
          subtitle="Creator or clipper workflow groundwork."
          empty="No campaigns yet."
          items={campaigns.slice(0, 5).map((item) => ({
            title: item.name || item.title || "Campaign",
            detail: `${item.status} · ${item.target_angle || "no angle"} · ${formatCents(item.payout_cents_per_1000_views)} per 1k views`,
          }))}
        />
      </div>
    </section>
  );
}

function StatCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="glass-panel rounded-[28px] p-5">
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
            <div key={`${item.title}-${item.detail}`} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
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
