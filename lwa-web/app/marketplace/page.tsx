import { LwaShell } from "../../components/worlds/LwaShell";
import { MarketplaceOverview } from "../../components/worlds/MarketplaceOverview";
import { listCampaigns } from "../../lib/worlds/api";
import { mockCampaigns } from "../../lib/worlds/mock-data";

async function getCampaigns() {
  try {
    const campaigns = await listCampaigns();
    return campaigns.length > 0 ? campaigns : mockCampaigns;
  } catch {
    return mockCampaigns;
  }
}

export default async function MarketplacePage() {
  const campaigns = await getCampaigns();
  return (
    <LwaShell title="Marketplace">
      <MarketplaceOverview campaigns={campaigns} />
    </LwaShell>
  );
}
