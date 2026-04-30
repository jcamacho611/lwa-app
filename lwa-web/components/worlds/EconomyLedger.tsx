import { safetyCopy } from "../../lib/worlds/copy";
import {
  mockCreditBalance,
  mockCreditTransactions,
  mockEarningEvents,
  mockEarningsAccount,
  mockLedger,
  mockPayoutPlaceholders,
} from "../../lib/worlds/mock-data";
import type {
  CreditBalance,
  CreditTransaction,
  EarningEvent,
  EarningsAccount,
  LedgerEntry,
  PayoutPlaceholder,
} from "../../lib/worlds/types";
import { formatMoney } from "../../lib/worlds/utils";
import { CreditsPanel } from "./CreditsPanel";
import { SafetyNotice } from "./SafetyNotice";
import { StatPill } from "./StatPill";
import { StatusBadge } from "./StatusBadge";

export function EconomyLedger({
  credits = mockCreditBalance,
  creditTransactions = mockCreditTransactions,
  earnings = mockEarningsAccount,
  earningEvents = mockEarningEvents,
  payoutPlaceholders = mockPayoutPlaceholders,
  ledger = mockLedger,
}: {
  credits?: CreditBalance;
  creditTransactions?: CreditTransaction[];
  earnings?: EarningsAccount;
  earningEvents?: EarningEvent[];
  payoutPlaceholders?: PayoutPlaceholder[];
  ledger?: LedgerEntry[];
}) {
  return (
    <div className="space-y-6">
      <CreditsPanel balance={credits} transactions={creditTransactions} />

      <section className="grid gap-5 md:grid-cols-3">
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/46">Estimated</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{formatMoney(earnings.estimatedAmount)}</p>
        </div>
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/46">Approved</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{formatMoney(earnings.approvedAmount)}</p>
        </div>
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/46">Payout eligible</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{formatMoney(earnings.payableAmount)}</p>
        </div>
      </section>

      <SafetyNotice>{safetyCopy.payouts}</SafetyNotice>

      <section className="grid gap-5 lg:grid-cols-2">
        <div className="glass-panel rounded-[28px] p-5">
          <h2 className="text-2xl font-semibold text-ink">Earning events</h2>
          <div className="mt-5 grid gap-3">
            {earningEvents.length > 0 ? (
              earningEvents.map((event) => (
                <article key={event.id} className="metric-tile rounded-[18px] p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="font-semibold text-ink">{event.sourceType}</p>
                      <p className="mt-1 text-xs text-ink/46">{event.note}</p>
                    </div>
                    <StatusBadge status={event.status} />
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <StatPill label="Gross" value={formatMoney(event.amount)} />
                    <StatPill label="Fee" value={formatMoney(event.platformFeeAmount)} />
                    <StatPill label="Net" value={formatMoney(event.netAmount)} accent />
                  </div>
                </article>
              ))
            ) : (
              <p className="input-surface rounded-[18px] p-4 text-sm text-ink/62">
                No earning events yet. Approved marketplace work will appear here before any payout eligibility.
              </p>
            )}
          </div>
        </div>

        <div className="glass-panel rounded-[28px] p-5">
          <h2 className="text-2xl font-semibold text-ink">Payout placeholders</h2>
          <div className="mt-5 grid gap-3">
            {payoutPlaceholders.length > 0 ? (
              payoutPlaceholders.map((payout) => (
                <article key={payout.id} className="metric-tile rounded-[18px] p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="font-semibold text-ink">{formatMoney(payout.amount)}</p>
                    <StatusBadge status={payout.status} />
                  </div>
                  <p className="mt-2 text-sm text-ink/62">{payout.blockedReason}</p>
                </article>
              ))
            ) : (
              <p className="input-surface rounded-[18px] p-4 text-sm text-ink/62">
                No payout placeholders yet. Real payout automation remains disabled.
              </p>
            )}
          </div>
        </div>
      </section>

      <section className="glass-panel rounded-[28px] p-5">
        <h2 className="text-2xl font-semibold text-ink">Ledger events</h2>
        <div className="mt-5 grid gap-3">
          {ledger.map((entry) => (
            <article key={entry.id} className="metric-tile rounded-[18px] p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-semibold text-ink">{entry.label}</p>
                  <p className="mt-1 text-xs text-ink/46">{entry.type}</p>
                </div>
                <StatusBadge status={entry.status} />
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {entry.amount ? <StatPill label="Amount" value={formatMoney(entry.amount.amount)} accent /> : null}
                {entry.xp ? <StatPill label="XP" value={`+${entry.xp}`} /> : null}
                {entry.reputation ? <StatPill label="Rep" value={`+${entry.reputation}`} /> : null}
                {entry.referenceId ? <StatPill label="Ref" value={entry.referenceId} /> : null}
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
