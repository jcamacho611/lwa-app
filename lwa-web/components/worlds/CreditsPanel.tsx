import type { CreditBalance, CreditTransaction } from "../../lib/worlds/types";
import { mockCreditBalance, mockCreditTransactions } from "../../lib/worlds/mock-data";
import { formatDate } from "../../lib/worlds/utils";
import { StatPill } from "./StatPill";
import { StatusBadge } from "./StatusBadge";

export function CreditsPanel({
  balance = mockCreditBalance,
  transactions = mockCreditTransactions,
}: {
  balance?: CreditBalance;
  transactions?: CreditTransaction[];
}) {
  return (
    <section className="glass-panel rounded-[28px] p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="section-kicker">Credits</p>
          <h2 className="mt-2 text-3xl font-semibold text-ink">{balance.balance} available</h2>
        </div>
        <StatusBadge status="recorded" />
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <StatPill label="Monthly grant" value={balance.monthlyGrant} accent />
        <StatPill label="Used" value={balance.usedThisPeriod} />
        {balance.periodStart ? <StatPill label="Period" value={formatDate(balance.periodStart)} /> : null}
      </div>

      <div className="mt-5 grid gap-3">
        {transactions.slice(0, 4).map((transaction) => (
          <article key={transaction.id} className="metric-tile rounded-[18px] p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-semibold text-ink">{transaction.reason}</p>
                <p className="mt-1 text-xs text-ink/46">{transaction.transactionType}</p>
              </div>
              <StatPill label="Credits" value={transaction.amount > 0 ? `+${transaction.amount}` : transaction.amount} />
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
