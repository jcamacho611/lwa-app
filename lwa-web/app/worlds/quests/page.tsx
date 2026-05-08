import { LwaShell } from "../../../components/worlds/LwaShell";
import { QuestBoard } from "../../../components/worlds/QuestBoard";
import { mockQuests } from "../../../lib/worlds/mock-data";

export default function QuestsPage() {
  return (
    <LwaShell title="Quest Board">
      <QuestBoard quests={mockQuests} />
    </LwaShell>
  );
}
