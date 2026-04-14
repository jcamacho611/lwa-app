"use client";

import Link from "next/link";
import { FeatureFlags, UserProfile, WalletSummary } from "../lib/types";

type SettingsPanelProps = {
  user: UserProfile;
  wallet: WalletSummary | null;
  featureFlags: FeatureFlags;
  creditsRemaining?: number | null;
  planLabel: string;
  onSignOut: () => void;
};

export function SettingsPanel({ user, wallet, featureFlags, creditsRemaining, planLabel, onSignOut }: SettingsPanelProps) {
  const unlockedFeatures = [
    featureFlags.caption_editor ? "Clip metadata editing" : null,
    featureFlags.timeline_editor ? "Trim controls" : null,
    featureFlags.wallet_view ? "Wallet and payout view" : null,
    featureFlags.campaign_mode ? "Campaign workflows" : null,
    featureFlags.posting_queue ? "Posting queue controls" : null,
    featureFlags.premium_exports ? "Premium exports" : null,
  ].filter(Boolean) as string[];

  return (
    <section className="grid gap-6 xl:grid-cols-[0.95fr,1.05fr]">
      <div className="glass-panel rounded-[32px] p-6 sm:p-8">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Account</p>
        <h3 className="mt-2 text-3xl font-semibold text-ink">Workspace settings</h3>
        <p className="mt-4 text-sm leading-7 text-ink/64">
          Manage your account, plan, and creator workflow from one clean place.
        </p>

        <div className="mt-6 space-y-4">
          <InfoRow label="Email" value={user.email} />
          <InfoRow label="Plan" value={planLabel} />
          <InfoRow label="Created" value={user.created_at || "recent"} />
          <InfoRow label="Wallet available" value={`$${((wallet?.available_cents || 0) / 100).toFixed(2)}`} />
          <InfoRow
            label="Credits remaining"
            value={typeof creditsRemaining === "number" ? String(creditsRemaining) : "Run a generation to refresh"}
          />
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          {featureFlags.wallet_view ? (
            <Link
              href="/wallet"
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
            >
              Open wallet
            </Link>
          ) : null}
          <Link
            href="/history"
            className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
          >
            Open history
          </Link>
          <button
            type="button"
            onClick={onSignOut}
            className="rounded-full bg-gradient-to-r from-accent to-accentSoft px-4 py-2 text-sm font-semibold text-white shadow-glow"
          >
            Sign Out
          </button>
        </div>
      </div>

      <div className="glass-panel rounded-[32px] p-6 sm:p-8">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Plan + Limits</p>
        <h3 className="mt-2 text-2xl font-semibold text-ink">What this workspace unlocks</h3>
        <div className="mt-6 grid gap-3">
          {[
            `${featureFlags.clip_limit || 0} ranked clips returned per run`,
            `${featureFlags.max_generations_per_day || 0} generation credits available each day`,
            `${featureFlags.max_uploads_per_day || 0} uploads available each day`,
            featureFlags.premium_exports ? "No watermark on exports" : "Watermark remains on free exports",
            unlockedFeatures.length ? `Unlocked: ${unlockedFeatures.join(", ")}` : "Upgrade to unlock editing, wallet, and campaign tools",
          ].map((item) => (
            <div key={item} className="rounded-[24px] border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-ink/72">
              {item}
            </div>
          ))}
        </div>

        <p className="mt-6 text-sm leading-7 text-ink/60">
          This gives you a clear view of plan state, daily limits, and what unlocks next when you need more output.
        </p>
      </div>
    </section>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[24px] border border-white/10 bg-white/[0.03] px-4 py-3">
      <p className="text-xs uppercase tracking-[0.18em] text-muted">{label}</p>
      <p className="mt-2 text-sm font-medium text-ink">{value}</p>
    </div>
  );
}
