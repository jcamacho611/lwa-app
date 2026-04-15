"use client";

import { useState } from "react";
import { PayoutRequest, WalletLedgerEntry, WalletSummary } from "../lib/types";

type WalletPanelProps = {
  wallet: WalletSummary | null;
  ledgerEntries: WalletLedgerEntry[];
  onRequestPayout: (amountCents: number) => Promise<PayoutRequest>;
};

function formatCents(value?: number | null) {
  return `$${((value || 0) / 100).toFixed(2)}`;
}

export function WalletPanel({ wallet, ledgerEntries, onRequestPayout }: WalletPanelProps) {
  const [payoutAmount, setPayoutAmount] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handlePayoutRequest() {
    const amountCents = Math.round(Number(payoutAmount || "0") * 100);
    if (!amountCents) {
      setMessage("Enter a payout amount in USD.");
      return;
    }

    setIsSaving(true);
    setMessage(null);
    try {
      const payout = await onRequestPayout(amountCents);
      setPayoutAmount("");
      setMessage(`Payout request ${payout.id} created.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to request payout.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="space-y-6">
      <div className="grid gap-5 lg:grid-cols-3">
        <MetricCard label="Available" value={formatCents(wallet?.available_cents)} detail="Balance ready for manual payout review." />
        <MetricCard label="Pending" value={formatCents(wallet?.pending_cents)} detail="Pending payout holds and unsettled campaign earnings." />
        <MetricCard
          label="Payout ready"
          value={formatCents(wallet?.eligible_payout_cents)}
          detail="Approved submissions become payout-ready before transfer rails are connected."
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.92fr,1.08fr]">
        <div className="glass-panel rounded-[32px] p-6 sm:p-8">
        <p className="section-kicker">Payout readiness</p>
        <h3 className="mt-2 text-3xl font-semibold text-ink">Request funds from the ledger</h3>
        <p className="mt-4 text-sm leading-7 text-ink/64">Review available balance and request a payout when you are ready.</p>

          {wallet?.submission_summary ? (
            <div className="mt-5 metric-tile rounded-[24px] p-4">
              <p className="text-sm font-medium text-ink">Submission readiness</p>
              <p className="mt-2 text-sm leading-7 text-ink/64">
                {wallet.submission_summary.status_counts.approved || 0} approved · {wallet.submission_summary.status_counts.submitted || 0} submitted ·{" "}
                {wallet.submission_summary.status_counts.paid || 0} paid.
              </p>
              <p className="mt-2 text-sm text-accent">
                Approval unlocks payout readiness. Transfers stay manual until payout rails are wired.
              </p>
            </div>
          ) : null}

          <label className="mt-6 block">
            <span className="mb-2 block text-sm font-medium text-ink/80">Amount in USD</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={payoutAmount}
              onChange={(event) => setPayoutAmount(event.target.value)}
              placeholder="25.00"
              className="input-surface w-full rounded-[24px] px-4 py-3 text-sm"
            />
          </label>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="button"
              disabled={isSaving}
              onClick={handlePayoutRequest}
              className="primary-button rounded-full px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSaving ? "Submitting..." : "Request Payout"}
            </button>
            {message ? <span className="text-sm text-accent">{message}</span> : null}
          </div>
        </div>

        <div className="glass-panel rounded-[32px] p-6 sm:p-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="section-kicker">Ledger</p>
              <h3 className="mt-2 text-2xl font-semibold text-ink">Recent entries</h3>
            </div>
            <span className="rounded-full border border-white/10 bg-white/[0.05] px-4 py-2 text-sm text-ink/72">{ledgerEntries.length} entries</span>
          </div>

          <div className="mt-6 space-y-3">
            {ledgerEntries.length ? (
              ledgerEntries.map((entry) => (
                <div key={entry.id} className="metric-tile rounded-[24px] p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-ink">{entry.description || entry.note || entry.type || "Ledger entry"}</p>
                      <p className="mt-1 text-xs text-muted">{entry.created_at || "recent"}</p>
                    </div>
                    <span className={["rounded-full px-3 py-1 text-xs font-medium", entry.amount_cents >= 0 ? "bg-emerald-400/10 text-emerald-300" : "bg-amber-400/10 text-amber-300"].join(" ")}>
                      {entry.amount_cents >= 0 ? "+" : "-"}
                      {formatCents(Math.abs(entry.amount_cents))}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4 text-sm text-ink/62">
                No ledger entries yet. Earnings and payout activity will accumulate here over time.
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function MetricCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="hero-card rounded-[28px] p-5">
      <p className="text-sm text-ink/60">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-ink">{value}</p>
      <p className="mt-3 text-sm leading-7 text-ink/64">{detail}</p>
    </div>
  );
}
