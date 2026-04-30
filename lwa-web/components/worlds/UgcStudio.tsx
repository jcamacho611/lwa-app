import Link from "next/link";
import type { UGCAsset } from "../../lib/worlds/types";
import { mockUgcAssets } from "../../lib/worlds/mock-data";
import { SafetyNotice } from "./SafetyNotice";
import { UgcAssetCard } from "./UgcAssetCard";

const assetTypes = [
  "Hook Pack",
  "Caption Pack",
  "Quest Template",
  "Campaign Template",
  "Avatar Cosmetic Concept",
  "World Event Concept",
  "Prompt Pack",
  "Editing Preset",
];

export function UgcStudio({ assets = mockUgcAssets }: { assets?: UGCAsset[] }) {
  return (
    <div className="space-y-6">
      <section className="hero-card rounded-[32px] p-6 sm:p-8">
        <p className="section-kicker">UGC Studio</p>
        <h2 className="page-title mt-3 text-3xl font-semibold">Build assets the economy can sell.</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/62">
          UGC starts with templates, prompts, quests, campaign packs, and creator tools. Later it can expand into
          cosmetics, world spaces, and app modules after review systems exist.
        </p>
        <Link href="/ugc/create" className="primary-button mt-6 inline-flex rounded-full px-5 py-3 text-sm font-semibold">
          Create UGC asset
        </Link>
      </section>

      <SafetyNotice>
        UGC assets must be original or properly licensed. No stolen IP, copied characters, or copyrighted brand assets
        without permission.
      </SafetyNotice>

      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {assetTypes.map((type) => (
          <div key={type} className="metric-tile rounded-[24px] p-5">
            <p className="text-lg font-semibold text-ink">{type}</p>
            <p className="mt-2 text-sm leading-6 text-ink/62">Draft, submit for review, sell later.</p>
          </div>
        ))}
      </section>

      <section>
        <h3 className="mb-4 text-2xl font-semibold text-ink">UGC drafts and review queue</h3>
        <div className="grid gap-5 lg:grid-cols-2">
          {assets.map((asset) => (
            <UgcAssetCard key={asset.id} asset={asset} />
          ))}
        </div>
      </section>
    </div>
  );
}
