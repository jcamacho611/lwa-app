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
    return {
      credits: mockCreditBalance,
      creditTransactions: mockCreditTransactions,
      earnings: mockEarningsAccount,
      earningEvents: mockEarningEvents,
      payoutPlaceholders: mockPayoutPlaceholders,
      ledger: mockLedger,
    };
  }
}

export default async function EconomyPage() {
  const data = await getEconomyData();

  return (
    <LwaShell title="Economy Ledger">
      <EconomyLedger {...data} />
    </LwaShell>
  );
}
