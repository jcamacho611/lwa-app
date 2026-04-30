import Link from "next/link";
import type { MarketplaceCampaign } from "../../lib/worlds/types";
import { formatDate, formatMoney } from "../../lib/worlds/utils";
import { StatPill } from "./StatPill";
import { StatusBadge } from "./StatusBadge";

export function CampaignCard({ campaign }: { campaign: MarketplaceCampaign }) {
  return (
    <article className="glass-panel rounded-[24px] p-5 transition hover:border-[var(--gold-border)] hover:shadow-[var(--shadow-card)]">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <StatusBadge status={campaign.status} />
        <span className="text-xs text-ink/46">Due {formatDate(campaign.deadline)}</span>
      </div>

      <h3 className="mt-4 text-xl font-semibold text-ink">{campaign.title}</h3>
      <p className="mt-2 text-sm leading-7 text-ink/62">{campaign.description}</p>

      <div className="mt-4 flex flex-wrap gap-2">
        <StatPill label="Budget" value={formatMoney(campaign.budget.amount)} accent />
        <StatPill label="Clips" value={campaign.clipCount} />
        <StatPill label="Platform" value={campaign.targetPlatform} />
        <StatPill label="Subs" value={campaign.submissionsCount} />
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <Link href={`/marketplace/campaigns/${campaign.id}`} className="primary-button rounded-full px-4 py-2 text-sm font-semibold">
          View campaign
        </Link>
        <Link href="/ugc/create" className="secondary-button rounded-full px-4 py-2 text-sm font-semibold">
          Draft submission asset
        </Link>
      </div>
    </article>
  );
}
