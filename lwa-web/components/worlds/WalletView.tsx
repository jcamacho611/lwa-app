"use client";

import { useEffect, useState } from "react";
import { readStoredToken } from "../../lib/auth";
import { loadWallet, loadWalletLedger } from "../../lib/api";
import type { WalletSummary, WalletLedgerEntry } from "../../lib/types";

function cents(value?: number) {
  if (typeof value !== "number") return "$0.00";
  return `$${(value / 100).toFixed(2)}`;
}

function entryLabel(entry: WalletLedgerEntry) {
  return entry.description || entry.note || entry.kind || entry.type || "Transaction";
}

function entrySign(entry: WalletLedgerEntry) {
  return entry.amount_cents >= 0 ? "+" : "";
}

export function WalletView() {
  const [wallet, setWallet] = useState<WalletSummary | null>(null);
  const [ledger, setLedger] = useState<WalletLedgerEntry[]>([]);
  const [state, setState] = useState<"loading" | "no-token" | "error" | "ready">("loading");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    const token = readStoredToken();
    if (!token) {
      setState("no-token");
      return;
    }
    Promise.all([loadWallet(token), loadWalletLedger(token)])
      .then(([w, entries]) => {
        setWallet(w);
        setLedger(entries);
        setState("ready");
      })
      .catch((err) => {
        setErrorMsg(err instanceof Error ? err.message : "Unable to load wallet.");
        setState("error");
      });
  }, []);

  if (state === "loading") {
    return (
      <div className="glass-panel rounded-[28px] p-6 text-sm text-ink/60">
        Loading wallet…
      </div>
    );
  }

  if (state === "no-token") {
    return (
      <div className="glass-panel rounded-[28px] p-6">
        <p className="text-sm font-semibold text-ink">Sign in to view your wallet</p>
        <p className="mt-2 text-sm text-ink/60">Your balance and ledger are only visible when you are signed in to LWA.</p>
        <a href="/generate" className="primary-button mt-4 inline-flex rounded-full px-5 py-3 text-sm font-semibold">
          Go to generator
        </a>
      </div>
    );
  }

  if (state === "error") {
    return (
      <div className="rounded-[28px] border border-red-400/20 bg-red-400/8 p-6">
        <p className="text-sm font-semibold text-red-200">Unable to load wallet</p>
        <p className="mt-2 text-xs text-red-200/70">{errorMsg}</p>
        <p className="mt-3 text-xs text-ink/46">Wallet view requires Pro plan or above. Check your plan in the generator.</p>
      </div>
    );
  }

  const entries = ledger.length > 0 ? ledger : (wallet?.recent_entries ?? []);

  return (
    <div className="space-y-6">
      <div className="rounded-[28px] border border-amber-300/20 bg-amber-300/8 px-5 py-4 text-sm leading-6 text-amber-100/80">
        <span className="font-semibold">Payout readiness only.</span> Balance reflects campaign submission credits and manual adjustments. No automatic payouts are triggered. Stripe Connect is env-gated and not live.
      </div>

      <section className="grid gap-5 md:grid-cols-3">
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/46">Available</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{cents(wallet?.available_cents)}</p>
        </div>
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/46">Lifetime earned</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{cents(wallet?.lifetime_cents)}</p>
        </div>
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/46">Payout eligible</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{cents(wallet?.eligible_payout_cents)}</p>
        </div>
      </section>

      <section className="glass-panel rounded-[28px] p-5">
        <h2 className="text-xl font-semibold text-ink">Ledger</h2>
        {entries.length === 0 ? (
          <p className="mt-4 text-sm text-ink/50">No transactions yet. Credits appear after approved campaign submissions.</p>
        ) : (
          <div className="mt-4 grid gap-3">
            {entries.map((entry) => (
              <div key={entry.id} className="metric-tile flex items-center justify-between gap-4 rounded-[18px] p-4">
                <div>
                  <p className="text-sm font-medium text-ink">{entryLabel(entry)}</p>
                  {entry.created_at ? (
                    <p className="mt-0.5 text-xs text-ink/42">{new Date(entry.created_at).toLocaleDateString()}</p>
                  ) : null}
                </div>
                <span className={`text-sm font-semibold ${entry.amount_cents >= 0 ? "text-emerald-300" : "text-red-300"}`}>
                  {entrySign(entry)}{cents(entry.amount_cents)}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      {wallet?.pending_cents ? (
        <div className="glass-panel rounded-[28px] p-5">
          <p className="text-sm text-ink/46">Pending</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{cents(wallet.pending_cents)}</p>
          <p className="mt-2 text-xs text-ink/46">Pending transactions are under review and have not cleared yet.</p>
        </div>
      ) : null}
    </div>
  );
}
