"use client";

import Link from "next/link";
import { UserProfile, WalletSummary } from "../lib/types";

type SettingsPanelProps = {
  user: UserProfile;
  wallet: WalletSummary | null;
  onSignOut: () => void;
};

export function SettingsPanel({ user, wallet, onSignOut }: SettingsPanelProps) {
  return (
    <section className="grid gap-6 xl:grid-cols-[0.95fr,1.05fr]">
      <div className="glass-panel rounded-[32px] p-6 sm:p-8">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Account</p>
        <h3 className="mt-2 text-3xl font-semibold text-ink">Workspace settings</h3>
        <p className="mt-4 text-sm leading-7 text-ink/64">
          The web app is set up as a cross-platform control room. Auth, uploads, history, campaigns, wallet, and posting state are all backend-owned.
        </p>

        <div className="mt-6 space-y-4">
          <InfoRow label="Email" value={user.email} />
          <InfoRow label="Plan" value={user.plan_code || "free"} />
          <InfoRow label="Created" value={user.created_at || "recent"} />
          <InfoRow label="Wallet available" value={`$${((wallet?.available_cents || 0) / 100).toFixed(2)}`} />
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/wallet"
            className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08]"
          >
            Open wallet
          </Link>
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
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Product State</p>
        <h3 className="mt-2 text-2xl font-semibold text-ink">What this web app already supports</h3>
        <div className="mt-6 grid gap-3">
          {[
            "JWT auth routed through the backend",
            "Upload-backed generation plus URL generation",
            "Saved clip pack history with browser editing",
            "Batch and campaign workflow surfaces",
            "Wallet ledger and payout groundwork",
            "Posting queue and provider abstraction scaffolding",
          ].map((item) => (
            <div key={item} className="rounded-[24px] border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-ink/72">
              {item}
            </div>
          ))}
        </div>

        <p className="mt-6 text-sm leading-7 text-ink/60">
          The next layers can add real checkout, provider auth, and richer analytics without replacing this frontend or disturbing the existing iOS app.
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
