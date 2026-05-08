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

async function getEarningsData() {
  const [credits, creditTransactions, earnings, earningEvents, payoutPlaceholders, ledger] = await Promise.allSettled([
    getMyCredits(),
    listMyCreditTransactions(),
    getMyEarningsAccount(),
    listMyEarningEvents(),
    listMyPayoutPlaceholders(),
    getMyLedger(),
  ]);

  return {
    ...(credits.status === "fulfilled" ? { credits: credits.value } : {}),
    ...(creditTransactions.status === "fulfilled" ? { creditTransactions: creditTransactions.value } : {}),
    ...(earnings.status === "fulfilled" ? { earnings: earnings.value } : {}),
    ...(earningEvents.status === "fulfilled" ? { earningEvents: earningEvents.value } : {}),
    ...(payoutPlaceholders.status === "fulfilled" ? { payoutPlaceholders: payoutPlaceholders.value } : {}),
    ...(ledger.status === "fulfilled" ? { ledger: ledger.value } : {}),
  };
}

export default async function EarningsPage() {
  const data = await getEarningsData();
  return (
    <LwaShell title="Earnings">
      <EconomyLedger {...data} />
    </LwaShell>
  );
}
