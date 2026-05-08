import type { Quest, UserWorldProfile } from "../../lib/worlds/types";
import { QuestBoard } from "./QuestBoard";
import { StatPill } from "./StatPill";

export function WorldProfile({ profile, quests }: { profile: UserWorldProfile; quests: Quest[] }) {
  const progress = Math.min(Math.round((profile.xp / profile.nextLevelXp) * 100), 100);

  return (
    <div className="space-y-6">
      <section className="hero-card rounded-[32px] p-6 sm:p-8">
        <p className="section-kicker">The Signal Realms</p>
        <h2 className="page-title mt-3 text-4xl font-semibold">{profile.displayName}</h2>
        <p className="mt-3 text-sm leading-7 text-ink/62">
          {profile.className} - {profile.faction}
        </p>
        <div className="mt-5 flex flex-wrap gap-2">
          <StatPill label="Level" value={profile.level} accent />
          <StatPill label="Creator Rep" value={profile.creatorReputation} />
          <StatPill label="Clipper Rep" value={profile.clipperReputation} />
          <StatPill label="Market Rep" value={profile.marketplaceReputation} />
        </div>
        <div className="mt-6">
          <div className="mb-2 flex justify-between text-sm text-ink/55">
            <span>XP Progress</span>
            <span>
              {profile.xp}/{profile.nextLevelXp}
            </span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-[var(--surface-inset-strong)]">
            <div className="h-full rounded-full bg-[var(--gold)]" style={{ width: `${progress}%` }} />
          </div>
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <div className="glass-panel rounded-[24px] p-5">
          <h3 className="text-2xl font-semibold text-ink">Badges</h3>
          <div className="mt-4 grid gap-3">
            {profile.badges.map((badge) => (
              <div key={badge.id} className="metric-tile rounded-[18px] p-4">
                <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-[var(--accent-wine)]">{badge.tier}</p>
                <h4 className="mt-1 text-lg font-semibold text-ink">{badge.name}</h4>
                <p className="mt-2 text-sm text-ink/62">{badge.description}</p>
                <p className="mt-2 text-sm italic text-ink/46">{badge.lore}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel rounded-[24px] p-5">
          <h3 className="text-2xl font-semibold text-ink">Relics</h3>
          <div className="mt-4 grid gap-3">
            {profile.relics.map((relic) => (
              <div key={relic.id} className="rounded-[18px] border border-[var(--gold-border)] bg-[var(--gold-dim)] p-4">
                <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-[var(--accent-wine)]">{relic.tier}</p>
                <h4 className="mt-1 text-lg font-semibold text-ink">{relic.name}</h4>
                <p className="mt-2 text-sm text-ink/62">{relic.description}</p>
                <p className="mt-2 text-sm italic text-ink/46">{relic.lore}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="glass-panel rounded-[24px] p-5">
        <h3 className="mb-5 text-2xl font-semibold text-ink">Active Quests</h3>
        <QuestBoard quests={quests} />
      </section>
    </div>
  );
}
