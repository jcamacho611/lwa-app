import { CommandCenter } from "../../components/worlds/CommandCenter";
import { LwaShell } from "../../components/worlds/LwaShell";
import { getMyEarningsAccount, getMyWorldProfile, listCampaigns } from "../../lib/worlds/api";
import { mockCampaigns, mockEarnings, mockWorldProfile } from "../../lib/worlds/mock-data";
import type { EarningSummary } from "../../lib/worlds/types";

async function getCommandCenterData() {
  const [profile, earningsAccount, campaigns] = await Promise.allSettled([
    getMyWorldProfile(),
    getMyEarningsAccount(),
    listCampaigns(),
  ]);

  const resolvedProfile = profile.status === "fulfilled" ? profile.value : mockWorldProfile;

  const resolvedEarnings: EarningSummary =
    earningsAccount.status === "fulfilled"
      ? {
          estimated: { amount: earningsAccount.value.estimatedAmount, currency: "USD" },
          pendingReview: { amount: earningsAccount.value.pendingReviewAmount, currency: "USD" },
          approved: { amount: earningsAccount.value.approvedAmount, currency: "USD" },
          payable: { amount: earningsAccount.value.payableAmount, currency: "USD" },
          paid: { amount: earningsAccount.value.paidAmount, currency: "USD" },
          held: { amount: earningsAccount.value.heldAmount, currency: "USD" },
        }
      : mockEarnings;

  const resolvedCampaigns = campaigns.status === "fulfilled" ? campaigns.value : mockCampaigns;

  return {
    profile: resolvedProfile,
    earnings: resolvedEarnings,
    campaignCount: resolvedCampaigns.length,
  };
}

export default async function CommandCenterPage() {
  const data = await getCommandCenterData();

  return (
    <LwaShell title="Command Center">
      <CommandCenter {...data} />
    </LwaShell>
  );
}
