import type { CampaignSubmission, MarketplaceCampaign } from "../../lib/worlds/types";
import { formatDate, formatMoney } from "../../lib/worlds/utils";
import { SafetyNotice } from "./SafetyNotice";
import { StatPill } from "./StatPill";
import { StatusBadge } from "./StatusBadge";

export function CampaignDetail({
  campaign,
  submissions,
}: {
  campaign: MarketplaceCampaign;
  submissions: CampaignSubmission[];
}) {

  return (
    <div className="space-y-6">
      <section className="hero-card rounded-[32px] p-6 sm:p-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <StatusBadge status={campaign.status} />
          <span className="text-sm text-ink/46">Created {formatDate(campaign.createdAt)}</span>
        </div>

        <h2 className="page-title mt-4 text-3xl font-semibold">{campaign.title}</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/62">{campaign.description}</p>

        <div className="mt-5 flex flex-wrap gap-2">
          <StatPill label="Budget" value={formatMoney(campaign.budget.amount)} accent />
          <StatPill label="Platform fee" value={`${campaign.platformFeePercent}%`} />
          <StatPill label="Clips wanted" value={campaign.clipCount} />
          <StatPill label="Deadline" value={formatDate(campaign.deadline)} />
          <StatPill label="Target" value={campaign.targetPlatform} />
        </div>
      </section>

      <section className="glass-panel rounded-[24px] p-5">
        <h3 className="text-xl font-semibold text-ink">Requirements</h3>
        <ul className="mt-4 space-y-2">
          {campaign.requirements.map((requirement) => (
            <li key={requirement} className="text-sm leading-6 text-ink/70">
              - {requirement}
            </li>
          ))}
        </ul>
      </section>

      <SafetyNotice title="Rights required">{campaign.rightsRequired}</SafetyNotice>

      <section>
        <h3 className="mb-4 text-2xl font-semibold text-ink">Submissions</h3>
        <div className="grid gap-4">
          {submissions.map((submission) => (
            <article key={submission.id} className="metric-tile rounded-[24px] p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <StatusBadge status={submission.status} />
                <span className="text-sm text-ink/46">{formatMoney(submission.estimatedEarnings.amount)} estimated</span>
              </div>
              <h4 className="mt-3 text-lg font-semibold text-ink">{submission.title}</h4>
              <p className="mt-2 text-sm text-ink/68">{submission.hook}</p>
              <p className="mt-2 text-sm text-ink/46">By {submission.clipperName}</p>
              {submission.reviewNote ? (
                <p className="mt-3 rounded-[16px] border border-[var(--divider)] bg-[var(--surface-inset)] p-3 text-sm text-ink/62">
                  {submission.reviewNote}
                </p>
              ) : null}
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
