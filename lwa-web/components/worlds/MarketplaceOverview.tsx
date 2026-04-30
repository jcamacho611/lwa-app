import Link from "next/link";
import { safetyCopy } from "../../lib/worlds/copy";
import { mockCampaigns } from "../../lib/worlds/mock-data";
import { CampaignCard } from "./CampaignCard";
import { SafetyNotice } from "./SafetyNotice";

export function MarketplaceOverview() {
  return (
    <div className="space-y-6">
      <section className="hero-card rounded-[32px] p-6 sm:p-8">
        <p className="section-kicker">Marketplace</p>
        <h2 className="page-title mt-3 text-3xl font-semibold leading-tight sm:text-[2.4rem]">
          Post jobs. Submit work. Earn from approved content.
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/62">
          The marketplace connects brands, creators, clippers, editors, and UGC builders. This shell starts with
          clipping jobs and campaign submissions, then expands into templates, quests, assets, and world content.
        </p>

        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/marketplace/post-job" className="primary-button rounded-full px-5 py-3 text-sm font-semibold">
            Post a job
          </Link>
          <Link href="/marketplace/campaigns" className="secondary-button rounded-full px-5 py-3 text-sm font-semibold">
            Browse campaigns
          </Link>
        </div>
      </section>

      <SafetyNotice>{safetyCopy.earnings}</SafetyNotice>

      <section>
        <div className="mb-4">
          <p className="section-kicker">Open Campaigns</p>
          <h3 className="mt-2 text-2xl font-semibold text-ink">Available work</h3>
        </div>
        <div className="grid gap-5 lg:grid-cols-2">
          {mockCampaigns.map((campaign) => (
            <CampaignCard key={campaign.id} campaign={campaign} />
          ))}
        </div>
      </section>
    </div>
  );
}
