import { notFound } from "next/navigation";

import { CampaignDetail } from "../../../../components/worlds/CampaignDetail";
import { LwaShell } from "../../../../components/worlds/LwaShell";
import { getCampaign, listSubmissions } from "../../../../lib/worlds/api";
import { mockCampaigns, mockSubmissions } from "../../../../lib/worlds/mock-data";

async function getCampaignData(id: string) {
  try {
    const [campaign, allSubmissions] = await Promise.all([getCampaign(id), listSubmissions()]);
    const submissions = allSubmissions.filter((s) => s.campaignId === id);
    return { campaign, submissions };
  } catch {
    const campaign = mockCampaigns.find((item) => item.id === id);
    const submissions = mockSubmissions.filter((s) => s.campaignId === id);
    return campaign ? { campaign, submissions } : null;
  }
}

export default async function CampaignDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const data = await getCampaignData(params.id);

  if (!data) {
    notFound();
  }

  return (
    <LwaShell title="Campaign Detail">
      <CampaignDetail campaign={data.campaign} submissions={data.submissions} />
    </LwaShell>
  );
}
