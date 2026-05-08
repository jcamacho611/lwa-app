import { LwaShell } from "../../../components/worlds/LwaShell";
import { QuestBoard } from "../../../components/worlds/QuestBoard";
import { listQuests } from "../../../lib/worlds/api";
import { mockQuests } from "../../../lib/worlds/mock-data";

async function getQuests() {
  try {
    const quests = await listQuests();
    return quests.length > 0 ? quests : mockQuests;
  } catch {
    return mockQuests;
  }
}

export default async function QuestsPage() {
  const quests = await getQuests();
  return (
    <LwaShell title="Quest Board">
      <QuestBoard quests={quests} />
    </LwaShell>
  );
}
