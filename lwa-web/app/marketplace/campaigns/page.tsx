import { CampaignCard } from "../../../components/worlds/CampaignCard";
import { LwaShell } from "../../../components/worlds/LwaShell";
import { listCampaigns } from "../../../lib/worlds/api";
import { mockCampaigns } from "../../../lib/worlds/mock-data";

async function getCampaignData() {
  try {
    return await listCampaigns();
  } catch {
    return mockCampaigns;
  }
}

export default async function CampaignsPage() {
  const campaigns = await getCampaignData();

  return (
    <LwaShell title="Campaigns">
      <div className="grid gap-5 lg:grid-cols-2">
        {campaigns.map((campaign) => (
          <CampaignCard key={campaign.id} campaign={campaign} />
        ))}
      </div>
    </LwaShell>
  );
}
