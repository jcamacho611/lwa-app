import { notFound } from "next/navigation";

import { CampaignDetail } from "../../../../components/worlds/CampaignDetail";
import { LwaShell } from "../../../../components/worlds/LwaShell";
import { getCampaign } from "../../../../lib/worlds/api";
import { mockCampaigns } from "../../../../lib/worlds/mock-data";

async function getCampaignData(id: string) {
  try {
    return await getCampaign(id);
  } catch {
    return mockCampaigns.find((item) => item.id === id);
  }
}

export default async function CampaignDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const campaign = await getCampaignData(params.id);

  if (!campaign) {
    notFound();
  }

  return (
    <LwaShell title="Campaign Detail">
      <CampaignDetail campaign={campaign} />
    </LwaShell>
  );
}
