import { EconomyLedger } from "../../components/worlds/EconomyLedger";
import { LwaShell } from "../../components/worlds/LwaShell";
import { loadWallet, loadWalletLedger } from "../../lib/api";
import { readStoredToken } from "../../lib/auth";
import type { WalletSummary, WalletLedgerEntry } from "../../lib/types";

async function getEconomyData() {
  const token = readStoredToken();

  if (!token) {
    return null;
  }

  try {
    const [wallet, ledger] = await Promise.all([
      loadWallet(token),
      loadWalletLedger(token),
    ]);

    // Transform wallet data to match expected EconomyLedger props
    const credits = {
      userId: "", // Not available in current API
      balance: wallet.available_cents || 0,
      monthlyGrant: 0, // Not available in current API
      usedThisPeriod: 0, // Not available in current API
      periodStart: undefined,
      periodEnd: undefined,
      updatedAt: new Date().toISOString(),
    };

    const creditTransactions: any[] = []; // Not available in current API
    const earnings = {
      userId: "", // Not available in current API
      estimatedAmount: 0, // Not available in current API
      pendingReviewAmount: 0,
      approvedAmount: 0,
      payableAmount: wallet.eligible_payout_cents || 0,
      paidAmount: 0,
      heldAmount: 0,
      currency: "USD" as const,
      updatedAt: new Date().toISOString(),
    };
    const earningEvents: any[] = []; // Not available in current API
    const payoutPlaceholders: any[] = []; // Not available in current API

    // Transform ledger entries to match expected format
    const transformedLedger = ledger.map((entry) => ({
      id: entry.id,
      type: (entry.type as any) || "credit_spent", // Use proper LedgerEventType
      label: entry.description || entry.note || "Transaction",
      amount: entry.amount_cents ? { amount: entry.amount_cents, currency: "USD" as const } : undefined,
      createdAt: entry.created_at || new Date().toISOString(),
      status: (entry.status as any) || "recorded",
      referenceId: entry.reference_id || undefined,
    }));

    return { credits, creditTransactions, earnings, earningEvents, payoutPlaceholders, ledger: transformedLedger };
  } catch {
    return null;
  }
}

export default async function EconomyPage() {
  const data = await getEconomyData();

  if (!data) {
    return (
      <LwaShell title="Economy Ledger">
        <div className="glass-panel rounded-[28px] p-8 text-center">
          <p className="text-lg font-semibold text-ink">Live data unavailable</p>
          <p className="mt-2 text-sm text-ink/62">Connect or sign in to view your economy ledger.</p>
        </div>
      </LwaShell>
    );
  }

  return (
    <LwaShell title="Economy Ledger">
      <EconomyLedger {...data} />
    </LwaShell>
  );
}
