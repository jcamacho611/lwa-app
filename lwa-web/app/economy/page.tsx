import { EconomyLedger } from "../../components/worlds/EconomyLedger";
import { LwaShell } from "../../components/worlds/LwaShell";
import {
  getMyCredits,
  getMyEarningsAccount,
  getMyLedger,
  listMyCreditTransactions,
  listMyEarningEvents,
  listMyPayoutPlaceholders,
} from "../../lib/worlds/api";
import {
  mockCreditBalance,
  mockCreditTransactions,
  mockEarningEvents,
  mockEarningsAccount,
  mockLedger,
  mockPayoutPlaceholders,
} from "../../lib/worlds/mock-data";

async function getEconomyData() {
  try {
    const [credits, creditTransactions, earnings, earningEvents, payoutPlaceholders, ledger] = await Promise.all([
      getMyCredits(),
      listMyCreditTransactions(),
      getMyEarningsAccount(),
      listMyEarningEvents(),
      listMyPayoutPlaceholders(),
      getMyLedger(),
    ]);

    return { credits, creditTransactions, earnings, earningEvents, payoutPlaceholders, ledger };
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
