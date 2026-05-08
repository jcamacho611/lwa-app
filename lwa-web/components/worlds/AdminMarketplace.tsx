import type { AdminQueueItem } from "../../lib/worlds/types";
import { mockAdminQueue } from "../../lib/worlds/mock-data";
import { SafetyNotice } from "./SafetyNotice";
import { StatPill } from "./StatPill";
import { StatusBadge } from "./StatusBadge";

export function AdminMarketplace({ queue = mockAdminQueue }: { queue?: AdminQueueItem[] }) {
  const payoutReview = queue.filter((i) => i.type === "payout_review").length;
  const disputes = queue.filter((i) => i.type === "dispute").length;
  const fraudFlags = queue.filter((i) => i.type === "fraud_flag").length;

  return (
    <div className="space-y-6">
      <SafetyNotice title="Admin control">
        Every approval, rejection, payout hold, dispute resolution, and moderation action must create an audit log entry
        before production launch.
      </SafetyNotice>

      <section className="grid gap-5 md:grid-cols-4">
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/46">Open queue</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{queue.length}</p>
        </div>
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/46">Payout review</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{payoutReview}</p>
        </div>
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/46">Disputes</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{disputes}</p>
        </div>
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/46">Fraud flags</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{fraudFlags}</p>
        </div>
      </section>

      <section className="glass-panel rounded-[28px] p-5">
        <h2 className="text-2xl font-semibold text-ink">Review queue</h2>
        <div className="mt-5 grid gap-3">
          {queue.map((item) => (
            <article key={item.id} className="metric-tile rounded-[18px] p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-semibold text-ink">{item.title}</p>
                  <p className="mt-1 text-xs text-ink/46">{item.type}</p>
                </div>
                <StatusBadge status={item.status} />
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <StatPill label="Priority" value={item.priority} accent={item.priority === "high" || item.priority === "critical"} />
                {item.owner ? <StatPill label="Owner" value={item.owner} /> : null}
              </div>
              <div className="mt-4 flex flex-wrap gap-3">
                <button className="primary-button rounded-full px-4 py-2 text-sm font-semibold">Review</button>
                <button className="secondary-button rounded-full px-4 py-2 text-sm font-semibold">Hold</button>
                <button className="rounded-full border border-red-400/30 bg-red-400/10 px-4 py-2 text-sm font-semibold text-red-700 dark:text-red-200">
                  Flag
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
