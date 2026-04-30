import type { UGCAsset } from "../../lib/worlds/types";
import { formatMoney } from "../../lib/worlds/utils";
import { StatPill } from "./StatPill";
import { StatusBadge } from "./StatusBadge";

export function UgcAssetCard({ asset }: { asset: UGCAsset }) {
  return (
    <article className="glass-panel rounded-[26px] p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <StatusBadge status={asset.status} />
        <StatusBadge status={asset.moderationStatus} />
      </div>

      <h3 className="mt-4 text-xl font-semibold text-ink">{asset.title}</h3>
      <p className="mt-2 text-sm leading-6 text-ink/62">{asset.description}</p>

      <div className="mt-4 flex flex-wrap gap-2">
        <StatPill label="Type" value={asset.assetType} />
        <StatPill label="Price" value={formatMoney(asset.price.amount)} accent />
        <StatPill label="Rights" value={asset.rightsConfirmed ? "Confirmed" : "Missing"} />
      </div>

      {asset.licenseSummary ? (
        <p className="mt-4 rounded-[18px] border border-[var(--divider)] bg-[var(--surface-soft)] p-3 text-sm leading-6 text-ink/56">
          {asset.licenseSummary}
        </p>
      ) : null}
    </article>
  );
}
