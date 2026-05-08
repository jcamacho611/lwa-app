import { LwaShell } from "../../../components/worlds/LwaShell";
import { WorldProfile } from "../../../components/worlds/WorldProfile";
import { getMyWorldProfile } from "../../../lib/worlds/api";
import { mockQuests, mockWorldProfile } from "../../../lib/worlds/mock-data";

async function getProfileData() {
  try {
    const profile = await getMyWorldProfile();
    return { profile, quests: mockQuests };
  } catch {
    return { profile: mockWorldProfile, quests: mockQuests };
  }
}

export default async function WorldProfilePage() {
  const data = await getProfileData();
  return (
    <LwaShell title="World Profile">
      <WorldProfile {...data} />
    </LwaShell>
  );
}
