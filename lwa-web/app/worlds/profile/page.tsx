import { LwaShell } from "../../../components/worlds/LwaShell";
import { WorldProfile } from "../../../components/worlds/WorldProfile";
import { getMyBadges, getMyRelics, getMyWorldProfile, listQuests } from "../../../lib/worlds/api";
import { mockQuests, mockWorldProfile } from "../../../lib/worlds/mock-data";

async function getProfileData() {
  const [profile, badges, relics, quests] = await Promise.allSettled([
    getMyWorldProfile(),
    getMyBadges(),
    getMyRelics(),
    listQuests(),
  ]);

  const resolvedProfile =
    profile.status === "fulfilled"
      ? {
          ...profile.value,
          badges: badges.status === "fulfilled" ? badges.value : [],
          relics: relics.status === "fulfilled" ? relics.value : [],
        }
      : mockWorldProfile;

  const resolvedQuests = quests.status === "fulfilled" && quests.value.length > 0 ? quests.value : mockQuests;

  return { profile: resolvedProfile, quests: resolvedQuests };
}

export default async function WorldProfilePage() {
  const data = await getProfileData();
  return (
    <LwaShell title="World Profile">
      <WorldProfile {...data} />
    </LwaShell>
  );
}
