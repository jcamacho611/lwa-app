import { mockQuests } from "../../lib/worlds/mock-data";
import { StatPill } from "./StatPill";
import { StatusBadge } from "./StatusBadge";

export function QuestBoard() {
  return (
    <div className="grid gap-5 lg:grid-cols-2">
      {mockQuests.map((quest) => {
        const progress = Math.min(Math.round((quest.progress / quest.goal) * 100), 100);
        return (
          <article key={quest.id} className="glass-panel rounded-[24px] p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <StatusBadge status={quest.status} />
              <StatPill label="Reward" value={`+${quest.rewardXp} XP`} accent />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-ink">{quest.title}</h3>
            <p className="mt-2 text-sm leading-7 text-ink/62">{quest.description}</p>
            <div className="mt-5">
              <div className="mb-2 flex justify-between text-xs text-ink/46">
                <span>Progress</span>
                <span>
                  {quest.progress}/{quest.goal}
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-[var(--surface-inset-strong)]">
                <div className="h-full rounded-full bg-[var(--gold)]" style={{ width: `${progress}%` }} />
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
}
