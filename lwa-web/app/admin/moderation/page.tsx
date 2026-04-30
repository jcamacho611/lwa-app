import { AdminModeration } from "../../../components/worlds/AdminModeration";
import { LwaShell } from "../../../components/worlds/LwaShell";
import { listFraudFlags, listModerationQueue, listRightsClaims } from "../../../lib/worlds/api";
import { mockFraudFlags, mockModerationQueue, mockRightsClaims } from "../../../lib/worlds/mock-data";

async function getAdminModerationData() {
  try {
    const [moderation, fraud, rights] = await Promise.all([
      listModerationQueue(),
      listFraudFlags(),
      listRightsClaims(),
    ]);
    return { moderation, fraud, rights };
  } catch {
    return {
      moderation: mockModerationQueue,
      fraud: mockFraudFlags,
      rights: mockRightsClaims,
    };
  }
}

export default async function AdminModerationPage() {
  const data = await getAdminModerationData();

  return (
    <LwaShell title="Admin Moderation">
      <AdminModeration moderation={data.moderation} fraud={data.fraud} rights={data.rights} />
    </LwaShell>
  );
}
