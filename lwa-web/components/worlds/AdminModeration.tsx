import type { ContentRightsClaim, FraudFlag, ModerationQueueItem } from "../../lib/worlds/types";
import { mockFraudFlags, mockModerationQueue, mockRightsClaims } from "../../lib/worlds/mock-data";
import { SafetyNotice } from "./SafetyNotice";
import { StatPill } from "./StatPill";
import { StatusBadge } from "./StatusBadge";

export function AdminModeration({
  moderation = mockModerationQueue,
  fraud = mockFraudFlags,
  rights = mockRightsClaims,
}: {
  moderation?: ModerationQueueItem[];
  fraud?: FraudFlag[];
  rights?: ContentRightsClaim[];
}) {
  return (
    <div className="space-y-6">
      <SafetyNotice title="Trust and safety">
        UGC, campaigns, submissions, rights claims, and fraud flags must be reviewable before public marketplace scale.
        Automated checks can assist, but admin review remains required for high-risk actions.
      </SafetyNotice>

      <section className="grid gap-5 md:grid-cols-3">
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/50">Moderation items</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{moderation.length}</p>
        </div>
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/50">Fraud flags</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{fraud.length}</p>
        </div>
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/50">Rights claims</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{rights.length}</p>
        </div>
      </section>

      <section className="glass-panel rounded-[30px] p-5">
        <h2 className="text-2xl font-semibold text-ink">Moderation queue</h2>
        <div className="mt-5 grid gap-3">
          {moderation.map((item) => (
            <article key={item.id} className="rounded-[20px] border border-[var(--divider)] bg-white/40 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-medium text-ink">{item.targetType}</p>
                  <p className="mt-1 text-xs text-ink/42">{item.targetId}</p>
                </div>
                <StatusBadge status={item.status} />
              </div>
              <p className="mt-3 text-sm leading-6 text-ink/62">{item.reason}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {item.automatedScore !== undefined ? <StatPill label="Auto score" value={item.automatedScore} /> : null}
                {item.submittedBy ? <StatPill label="User" value={item.submittedBy} /> : null}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <div className="glass-panel rounded-[30px] p-5">
          <h2 className="text-2xl font-semibold text-ink">Fraud flags</h2>
          <div className="mt-5 grid gap-3">
            {fraud.map((flag) => (
              <article key={flag.id} className="rounded-[20px] border border-[var(--divider)] bg-white/40 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="font-medium text-ink">{flag.flagType}</p>
                  <StatusBadge status={flag.status} />
                </div>
                <p className="mt-2 text-sm leading-6 text-ink/62">{flag.evidence}</p>
                <div className="mt-3">
                  <StatPill label="Severity" value={flag.severity} accent />
                </div>
              </article>
            ))}
          </div>
        </div>

        <div className="glass-panel rounded-[30px] p-5">
          <h2 className="text-2xl font-semibold text-ink">Rights claims</h2>
          <div className="mt-5 grid gap-3">
            {rights.map((claim) => (
              <article key={claim.id} className="rounded-[20px] border border-[var(--divider)] bg-white/40 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="font-medium text-ink">{claim.claimantName}</p>
                  <StatusBadge status={claim.status} />
                </div>
                <p className="mt-1 text-xs text-ink/42">{claim.claimantEmail}</p>
                <p className="mt-3 text-sm leading-6 text-ink/62">{claim.claimSummary}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
